# backend/customer.py
from flask import request, jsonify
from database import get_db_connection
from datetime import datetime, timedelta


def init_customer_routes(app):

    # ============================================================
    # 1. UNIFIED BOOK SEARCH
    # ============================================================

    @app.route("/api/books", methods=["GET"])
    def search_books():
        """
        GET /api/books
        Supports:
          q, genre, year, sort_by, direction
        """
        q = (request.args.get("q") or "").strip()
        genre = (request.args.get("genre") or "").strip()
        year = (request.args.get("year") or "").strip()
        sort_by = request.args.get("sort_by", "title")
        direction = request.args.get("direction", "asc").lower()

        if sort_by not in (
            "title", "author", "genre", "publication_year",
            "price_buy", "price_rent"
        ):
            sort_by = "title"

        if direction not in ("asc", "desc"):
            direction = "asc"

        conn = None
        cur = None

        try:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)

            base = """
                SELECT
                    id,
                    title,
                    author,
                    genre,
                    publication_year,
                    price_buy,
                    price_rent
                FROM books
                WHERE 1=1
            """

            params = []

            if q:
                base += " AND (title LIKE %s OR author LIKE %s) "
                params.append(f"%{q}%")
                params.append(f"%{q}%")

            if genre:
                base += " AND genre LIKE %s "
                params.append(f"%{genre}%")

            if year:
                base += " AND publication_year = %s "
                params.append(year)

            base += f" ORDER BY {sort_by} {direction} LIMIT 200"

            cur.execute(base, params)
            rows = cur.fetchall()
            return jsonify(rows), 200

        except Exception as e:
            print("[BOOK SEARCH ERROR]", e)
            return jsonify({"error": "Error searching books"}), 500

        finally:
            if cur: cur.close()
            if conn: conn.close()

    # ============================================================
    # 2. BOOK DETAILS POPUP
    # ============================================================

    @app.route("/api/books/<int:book_id>", methods=["GET"])
    def get_book_details(book_id):
        """
        Returns:
            - core book data
            - avg rating
            - review count
            - user's own review (if user_id provided)
        """
        user_id = request.args.get("user_id")

        conn = None
        cur = None

        try:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)

            # Book base info
            cur.execute("""
                SELECT id, title, author, genre, publication_year,
                       price_buy, price_rent
                FROM books
                WHERE id = %s
            """, (book_id,))
            book = cur.fetchone()

            if not book:
                return jsonify({"error": "Book not found"}), 404

            # Average rating + count
            cur.execute("""
                SELECT ROUND(AVG(rating), 2) AS avg_rating,
                       COUNT(*) AS review_count
                FROM reviews
                WHERE book_id = %s
            """, (book_id,))
            stats = cur.fetchone()

            book["avg_rating"] = float(stats["avg_rating"]) if stats["avg_rating"] else None
            book["review_count"] = stats["review_count"]

            # User's review (if user_id given)
            if user_id:
                cur.execute("""
                    SELECT rating, review_text
                    FROM reviews
                    WHERE book_id = %s AND user_id = %s
                """, (book_id, user_id))
                book["user_review"] = cur.fetchone()
            else:
                book["user_review"] = None

            return jsonify(book), 200

        except Exception as e:
            print("[BOOK DETAILS ERROR]", e)
            return jsonify({"error": "Error fetching book details"}), 500

        finally:
            if cur: cur.close()
            if conn: conn.close()

    # ============================================================
    # 3. PLACE ORDER (auto-rentals)
    # ============================================================

    @app.route("/api/orders", methods=["POST"])
    def place_order():
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        items = data.get("items", [])

        if not user_id or not items:
            return jsonify({"error": "Missing user_id or items"}), 400

        conn = None
        cur = None

        try:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)

            # fetch book prices
            ids = list({i["book_id"] for i in items})
            fmt = ",".join(["%s"] * len(ids))

            cur.execute(f"""
                SELECT id, title, author, price_buy, price_rent
                FROM books
                WHERE id IN ({fmt})
            """, ids)
            rows = cur.fetchall()
            book_map = {b["id"]: b for b in rows}

            # calculate bill
            bill_items = []
            total = 0.0

            for it in items:
                b = book_map.get(it["book_id"])
                if not b:
                    return jsonify({"error": f"Book {it['book_id']} not found"}), 400

                price = float(b["price_buy"] if it["type"] == "buy" else b["price_rent"])
                total += price

                bill_items.append({
                    "book_id": b["id"],
                    "title": b["title"],
                    "author": b["author"],
                    "type": it["type"],
                    "price": price
                })

            # Create order
            cur.execute("""
                INSERT INTO orders (user_id, total_price, payment_status)
                VALUES (%s, %s, 'Pending')
            """, (user_id, total))
            order_id = cur.lastrowid

            # Insert order items, update inventory, and auto-create rentals for rents
            for it in bill_items:
                cur.execute("""
                    INSERT INTO order_items (order_id, book_id, type, price)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, it["book_id"], it["type"], it["price"]))
                order_item_id = cur.lastrowid

                # Lock inventory row for this book to avoid race conditions
                cur.execute("""
                    SELECT total_copies, available_copies
                    FROM inventory
                    WHERE book_id = %s
                    FOR UPDATE
                """, (it["book_id"],))
                inv = cur.fetchone()
                available = inv["available_copies"] if inv else 0

                if it["type"] == "rent":
                    # Renting consumes 1 available copy
                    if available <= 0:
                        # Not enough copies to rent
                        conn.rollback()
                        return jsonify({"error": f"No available copies to rent book {it['book_id']}"}), 400

                    # decrement available_copies
                    cur.execute("""
                        UPDATE inventory
                        SET available_copies = available_copies - 1
                        WHERE book_id = %s
                    """, (it["book_id"],))

                    due = datetime.now() + timedelta(days=14)
                    cur.execute("""
                        INSERT INTO rentals (order_item_id, user_id, book_id,
                                             rented_at, due_date)
                        VALUES (%s, %s, %s, NOW(), %s)
                    """, (order_item_id, user_id, it["book_id"], due))

                else:  # buy
                    # Buying consumes 1 total AND 1 available copy
                    if available <= 0:
                        conn.rollback()
                        return jsonify({"error": f"No available copies to buy book {it['book_id']}"}), 400

                    cur.execute("""
                        UPDATE inventory
                        SET total_copies = total_copies - 1,
                            available_copies = available_copies - 1
                        WHERE book_id = %s
                    """, (it["book_id"],))

            conn.commit()

            return jsonify({
                "order_id": order_id,
                "user_id": user_id,
                "items": bill_items,
                "total_price": total,
                "payment_status": "Pending"
            }), 201

        except Exception as e:
            if conn: conn.rollback()
            print("[PLACE ORDER ERROR]", e)
            return jsonify({"error": "Error placing order"}), 500

        finally:
            if cur: cur.close()
            if conn: conn.close()

    # ============================================================
    # 4. POST REVIEW
    # ============================================================

    @app.route("/api/reviews", methods=["POST"])
    def add_review():
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        book_id = data.get("book_id")
        rating = data.get("rating")
        review_text = data.get("review_text", "")

        if not (user_id and book_id and rating):
            return jsonify({"error": "Missing fields"}), 400

        conn = None
        cur = None

        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Insert or replace review
            cur.execute("""
                INSERT INTO reviews (user_id, book_id, rating, review_text)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    rating = VALUES(rating),
                    review_text = VALUES(review_text)
            """, (user_id, book_id, rating, review_text))

            conn.commit()
            return jsonify({"success": True}), 201

        except Exception as e:
            print("[REVIEW ERROR]", e)
            return jsonify({"error": "Error saving review"}), 500

        finally:
            if cur: cur.close()
            if conn: conn.close()

    # ============================================================
    # 5. HISTORY (purchases, current rentals, past rentals)
    # ============================================================

    @app.route("/api/history/<int:user_id>", methods=["GET"])
    def history(user_id):
        conn = None
        cur = None

        try:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)

            # purchases
            cur.execute("""
                SELECT 
                    b.id AS book_id,
                    b.title, 
                    b.author, 
                    oi.price, 
                    o.created_at AS purchased_at
                FROM orders o
                JOIN order_items oi ON oi.order_id = o.id
                JOIN books b ON b.id = oi.book_id
                WHERE o.user_id = %s AND oi.type = 'buy'
                ORDER BY o.created_at DESC
            """, (user_id,))
            purchases = cur.fetchall()

            # current rentals
            cur.execute("""
                SELECT 
                    b.id AS book_id,
                    b.title, 
                    b.author, 
                    r.rented_at, 
                    r.due_date,
                    DATEDIFF(r.due_date, NOW()) AS days_remaining
                FROM rentals r
                JOIN books b ON b.id = r.book_id
                WHERE r.user_id = %s AND r.returned_at IS NULL
                ORDER BY r.due_date ASC
            """, (user_id,))
            current_rentals = cur.fetchall()

            # past rentals
            cur.execute("""
                SELECT 
                    b.id AS book_id,
                    b.title, 
                    b.author, 
                    r.rented_at, 
                    r.returned_at
                FROM rentals r
                JOIN books b ON b.id = r.book_id
                WHERE r.user_id = %s AND r.returned_at IS NOT NULL
                ORDER BY r.returned_at DESC
            """, (user_id,))
            past_rentals = cur.fetchall()

            # user reviews
            cur.execute("""
                SELECT 
                    b.id AS book_id,
                    b.title,
                    b.author,
                    r.rating,
                    r.review_text,
                    r.created_at AS review_date
                FROM reviews r
                JOIN books b ON b.id = r.book_id
                WHERE r.user_id = %s
                ORDER BY r.created_at DESC
            """, (user_id,))
            reviews = cur.fetchall()

            return jsonify({
                "purchases": purchases,
                "current_rentals": current_rentals,
                "past_rentals": past_rentals,
                "reviews": reviews
            }), 200

        except Exception as e:
            print("[HISTORY ERROR]", e)
            return jsonify({"error": "Error fetching history"}), 500

        finally:
            if cur: cur.close()
            if conn: conn.close()

