# ============================================================
# backend/manager.py  (FULL REWRITE)
# ============================================================

from flask import request, jsonify
from database import get_db_connection
from datetime import datetime


def init_manager_routes(app):

    # ============================================================
    # UTIL
    # ============================================================

    def _dictfetch(cursor):
        return cursor.fetchall()

    def _safe_close(cursor, conn):
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # ============================================================
    # ORDERS: LIST + UPDATE STATUS
    # ============================================================

    @app.route("/api/manager/orders", methods=["GET"])
    def manager_list_orders():
        """Returns all orders w/ customer username + items."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT o.id, o.user_id, u.username AS customer_username,
                       o.total_price, o.payment_status, o.created_at
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC
            """)
            orders = cursor.fetchall()

            if orders:
                ids = [o["id"] for o in orders]
                fmt = ",".join(["%s"] * len(ids))

                cursor.execute(f"""
                    SELECT oi.order_id, oi.book_id, b.title, b.author,
                           oi.type, oi.price
                    FROM order_items oi
                    JOIN books b ON oi.book_id = b.id
                    WHERE oi.order_id IN ({fmt})
                    ORDER BY oi.order_id
                """, ids)
                item_rows = cursor.fetchall()
            else:
                item_rows = []

            items_by_order = {}
            for row in item_rows:
                items_by_order.setdefault(row["order_id"], []).append({
                    "book_id": row["book_id"],
                    "title": row["title"],
                    "author": row["author"],
                    "type": row["type"],
                    "price": float(row["price"])
                })

            for o in orders:
                o["total_price"] = float(o["total_price"])
                o["items"] = items_by_order.get(o["id"], [])

            return jsonify(orders), 200

        except Exception as e:
            print("[MANAGER LIST ORDERS ERROR]", e)
            return jsonify({"error": "Error loading orders"}), 500
        finally:
            _safe_close(cursor, conn)


    @app.route("/api/manager/orders/<int:order_id>/status", methods=["PATCH"])
    def manager_update_order_status(order_id):
        """Mark order as Paid/Pending."""
        data = request.get_json(silent=True) or {}
        status = data.get("payment_status")

        if status not in ("Paid", "Pending"):
            return jsonify({"error": "payment_status must be 'Paid' or 'Pending'"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE orders
                SET payment_status = %s
                WHERE id = %s
            """, (status, order_id))

            if cursor.rowcount == 0:
                return jsonify({"error": "Order not found"}), 404

            conn.commit()
            return jsonify({"message": "Status updated"}), 200

        except Exception as e:
            print("[MANAGER UPDATE ORDER STATUS ERROR]", e)
            if conn:
                conn.rollback()
            return jsonify({"error": "Error updating order"}), 500
        finally:
            _safe_close(cursor, conn)


    # ============================================================
    # BOOKS — SEARCH / LIST
    # ============================================================

    @app.route("/api/manager/books", methods=["GET"])
    def manager_search_books():
        """Advanced search: q, genre, year."""
        q = request.args.get("q", "").strip()
        genre = request.args.get("genre", "").strip()
        year = request.args.get("year", "").strip()

        where = []
        params = []

        if q:
            where.append("(b.title LIKE %s OR b.author LIKE %s)")
            params.extend([f"%{q}%", f"%{q}%"])

        if genre:
            where.append("b.genre LIKE %s")
            params.append(f"%{genre}%")

        if year:
            where.append("b.publication_year = %s")
            params.append(year)

        where_clause = " AND ".join(where)
        if where_clause:
            where_clause = "WHERE " + where_clause

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute(f"""
                SELECT b.id, b.title, b.author, b.price_buy, b.price_rent,
                    b.genre, b.publication_year, b.created_at,
                    COALESCE(inv.total_copies, 0) AS total_copies,
                    COALESCE(inv.available_copies, 0) AS available_copies,
                    COALESCE((
                        SELECT AVG(r.rating) FROM reviews r
                        WHERE r.book_id = b.id
                    ), 0) AS avg_rating,
                    COALESCE((
                        SELECT COUNT(*) FROM reviews r
                        WHERE r.book_id = b.id
                    ), 0) AS review_count
                FROM books b
                LEFT JOIN inventory inv ON inv.book_id = b.id
                {where_clause}
                ORDER BY b.created_at DESC
            """, params)

            rows = cursor.fetchall()

            for row in rows:
                row["price_buy"] = float(row["price_buy"])
                row["price_rent"] = float(row["price_rent"])
                row["avg_rating"] = float(row["avg_rating"])
                row["review_count"] = int(row.get("review_count", 0))

            return jsonify(rows), 200

        except Exception as e:
            print("[MANAGER BOOK SEARCH ERROR]", e)
            return jsonify({"error": "Error loading books"}), 500
        finally:
            _safe_close(cursor, conn)


    # ============================================================
    # BOOK DETAILS + REVIEWS
    # ============================================================

    @app.route("/api/manager/books/<int:book_id>/details", methods=["GET"])
    def manager_book_details(book_id):

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT b.*, inv.total_copies, inv.available_copies
                FROM books b
                LEFT JOIN inventory inv ON inv.book_id = b.id
                WHERE b.id = %s
            """, (book_id,))
            book = cursor.fetchone()

            if not book:
                return jsonify({"error": "Book not found"}), 404

            return jsonify(book), 200

        except Exception as e:
            print("[MANAGER BOOK DETAILS ERROR]", e)
            return jsonify({"error": "Error loading details"}), 500
        finally:
            _safe_close(cursor, conn)


    @app.route("/api/manager/books/<int:book_id>/reviews", methods=["GET"])
    def manager_book_reviews(book_id):
        """Return all reviews for this book."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT r.id, r.rating, r.review_text, r.created_at,
                       u.username
                FROM reviews r
                JOIN users u ON r.user_id = u.id
                WHERE r.book_id = %s
                ORDER BY r.created_at DESC
            """, (book_id,))

            reviews = cursor.fetchall()
            for r in reviews:
                r["rating"] = int(r["rating"])

            return jsonify(reviews), 200

        except Exception as e:
            print("[MANAGER REVIEWS ERROR]", e)
            return jsonify({"error": "Error loading reviews"}), 500
        finally:
            _safe_close(cursor, conn)


    # ============================================================
    # BOOK UPDATE + INVENTORY
    # ============================================================

    @app.route("/api/manager/books", methods=["POST"])
    def manager_add_book():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        author = (data.get("author") or "").strip()
        pb = data.get("price_buy")
        pr = data.get("price_rent")
        genre = data.get("genre")
        year = data.get("publication_year")

        if not title or not author or pb is None or pr is None:
            return jsonify({"error": "Missing required fields"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                INSERT INTO books (title, author, price_buy, price_rent, genre, publication_year)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, author, pb, pr, genre, year))

            book_id = cursor.lastrowid

            # Create inventory row
            cursor.execute("""
                INSERT INTO inventory (book_id, total_copies, available_copies)
                VALUES (%s, 10, 10)
            """, (book_id,))

            conn.commit()

            return jsonify({
                "id": book_id,
                "total_copies": 10,
                "available_copies": 10
            }), 201


        except Exception as e:
            print("[MANAGER ADD BOOK ERROR]", e)
            if conn:
                conn.rollback()
            return jsonify({"error": "Error adding book"}), 500
        finally:
            _safe_close(cursor, conn)


    @app.route("/api/manager/books/<int:book_id>", methods=["PUT"])
    def manager_update_book(book_id):
        data = request.get_json(silent=True) or {}

        title = (data.get("title") or "").strip()
        author = (data.get("author") or "").strip()
        pb = data.get("price_buy")
        pr = data.get("price_rent")
        total_copies = data.get("total_copies")
        available_copies = data.get("available_copies")
        genre = data.get("genre")
        year = data.get("publication_year")

        # Basic presence check
        if not title or not author or pb is None or pr is None or total_copies is None or available_copies is None:
            return jsonify({"error": "Missing required fields"}), 400

        # Validate numeric inventory fields
        try:
            total_copies = int(total_copies)
            available_copies = int(available_copies)
        except (ValueError, TypeError):
            return jsonify({"error": "total_copies and available_copies must be integers"}), 400

        if total_copies < 0 or available_copies < 0:
            return jsonify({"error": "Inventory counts cannot be negative"}), 400

        if total_copies < available_copies:
            return jsonify({"error": "total_copies cannot be less than available_copies"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Ensure the book exists first. Relying on cursor.rowcount after an
            # UPDATE can be misleading (MySQL reports 0 affected rows when the
            # new values equal the old values). Do a SELECT to check existence.
            cursor.execute("""
                SELECT id FROM books WHERE id = %s
            """, (book_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Book not found"}), 404

            cursor.execute("""
                UPDATE books
                SET title=%s, author=%s, price_buy=%s, price_rent=%s,
                    genre=%s, publication_year=%s
                WHERE id=%s
            """, (title, author, pb, pr, genre, year, book_id))

            cursor.execute("""
                UPDATE inventory
                SET total_copies = %s,
                    available_copies = %s
                WHERE book_id = %s
            """, (total_copies, available_copies, book_id))

            conn.commit()
            return jsonify({"message": "Book updated"}), 200

        except Exception as e:
            print("[MANAGER UPDATE BOOK ERROR]", e)
            if conn:
                conn.rollback()
            return jsonify({"error": "Error updating book"}), 500
        finally:
            _safe_close(cursor, conn)


    @app.route("/api/manager/books/<int:book_id>/inventory", methods=["PATCH"])
    def manager_adjust_inventory(book_id):
        """Increment available copies AND total copies if needed."""
        data = request.get_json(silent=True) or {}
        inc = data.get("increment")

        if inc is None:
            return jsonify({"error": "increment required"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # increment total + available equally
            cursor.execute("""
                UPDATE inventory
                SET total_copies = total_copies + %s,
                    available_copies = available_copies + %s
                WHERE book_id = %s
            """, (inc, inc, book_id))

            if cursor.rowcount == 0:
                return jsonify({"error": "Book not found"}), 404

            conn.commit()
            return jsonify({"message": "Inventory updated"}), 200

        except Exception as e:
            print("[MANAGER INVENTORY UPDATE ERROR]", e)
            if conn:
                conn.rollback()
            return jsonify({"error": "Error updating inventory"}), 500
        finally:
            _safe_close(cursor, conn)


    # ============================================================
    # CUSTOMERS — SEARCH + PROFILE
    # ============================================================

    @app.route("/api/manager/customers", methods=["GET"])
    def manager_search_customers():
        q = request.args.get("q", "").strip()

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            if q:
                cursor.execute("""
                    SELECT id, username, email, created_at
                    FROM users
                    WHERE role='customer'
                      AND (username LIKE %s OR email LIKE %s)
                    ORDER BY created_at DESC
                """, (f"%{q}%", f"%{q}%"))
            else:
                cursor.execute("""
                    SELECT id, username, email, created_at
                    FROM users
                    WHERE role='customer'
                    ORDER BY created_at DESC
                """)

            users = cursor.fetchall()
            return jsonify(users), 200

        except Exception as e:
            print("[MANAGER CUSTOMER SEARCH ERROR]", e)
            return jsonify({"error": "Error searching"}), 500
        finally:
            _safe_close(cursor, conn)


    @app.route("/api/manager/customers/<int:customer_id>", methods=["GET"])
    def manager_get_customer(customer_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT id, username, email, created_at
                FROM users
                WHERE id=%s AND role='customer'
            """, (customer_id,))
            user = cursor.fetchone()

            if not user:
                return jsonify({"error": "Customer not found"}), 404

            return jsonify(user), 200

        except Exception as e:
            print("[MANAGER GET CUSTOMER ERROR]", e)
            return jsonify({"error": "Error loading customer"}), 500
        finally:
            _safe_close(cursor, conn)


    # ============================================================
    # CUSTOMER ORDERS
    # ============================================================

    @app.route("/api/manager/customers/<int:customer_id>/orders", methods=["GET"])
    def manager_customer_orders(customer_id):
        """All orders for a customer."""
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT o.id, o.total_price, o.payment_status, o.created_at
                FROM orders o
                WHERE o.user_id = %s
                ORDER BY o.created_at DESC
            """, (customer_id,))

            orders = cursor.fetchall()
            for o in orders:
                o["total_price"] = float(o["total_price"])
            return jsonify(orders), 200

        except Exception as e:
            print("[MANAGER CUSTOMER ORDERS ERROR]", e)
            return jsonify({"error": "Error loading orders"}), 500
        finally:
            _safe_close(cursor, conn)


    # ============================================================
    # CUSTOMER RENTALS
    # ============================================================

    @app.route("/api/manager/customers/<int:customer_id>/rentals", methods=["GET"])
    def manager_customer_rentals(customer_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT r.id, r.book_id, r.due_date, r.rented_at, r.returned_at,
                       b.title
                FROM rentals r
                JOIN books b ON r.book_id = b.id
                WHERE r.user_id = %s
                ORDER BY r.rented_at DESC
            """, (customer_id,))

            return jsonify(cursor.fetchall()), 200

        except Exception as e:
            print("[MANAGER CUSTOMER RENTALS ERROR]", e)
            return jsonify({"error": "Error loading rentals"}), 500
        finally:
            _safe_close(cursor, conn)


    # ============================================================
    # MANUAL RENTAL CREATION
    # ============================================================

    @app.route("/api/manager/customers/<int:customer_id>/rentals", methods=["POST"])
    def manager_add_manual_rental(customer_id):
        data = request.get_json(silent=True) or {}
        book_id = data.get("book_id")
        due_date = data.get("due_date")

        if not book_id or not due_date:
            return jsonify({"error": "book_id and due_date required"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # check available
            cursor.execute("""
                SELECT available_copies FROM inventory
                WHERE book_id=%s
            """, (book_id,))
            inv = cursor.fetchone()

            if not inv or inv["available_copies"] <= 0:
                return jsonify({"error": "No copies available"}), 400

            # create rental record
            cursor.execute("""
                INSERT INTO rentals (order_item_id, user_id, book_id, due_date)
                VALUES (NULL, %s, %s, %s)
            """, (customer_id, book_id, due_date))

            # decrement inventory
            cursor.execute("""
                UPDATE inventory
                SET available_copies = available_copies - 1
                WHERE book_id = %s
            """, (book_id,))

            conn.commit()
            return jsonify({"message": "Rental created"}), 201

        except Exception as e:
            print("[MANAGER MANUAL RENT ERROR]", e)
            if conn:
                conn.rollback()
            return jsonify({"error": "Error creating rental"}), 500
        finally:
            _safe_close(cursor, conn)


    # ============================================================
    # MARK RENTAL RETURNED
    # ============================================================

    @app.route("/api/manager/rentals/<int:rental_id>/return", methods=["PATCH"])
    def manager_mark_returned(rental_id):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # get rental row
            cursor.execute("""
                SELECT book_id, returned_at
                FROM rentals
                WHERE id=%s
            """, (rental_id,))
            rental = cursor.fetchone()

            if not rental:
                return jsonify({"error": "Rental not found"}), 404

            if rental["returned_at"] is not None:
                return jsonify({"error": "Already returned"}), 400

            # set returned time
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                UPDATE rentals
                SET returned_at = %s
                WHERE id = %s
            """, (now, rental_id))

            # increment inventory
            cursor.execute("""
                UPDATE inventory
                SET available_copies = available_copies + 1
                WHERE book_id = %s
            """, (rental["book_id"],))

            conn.commit()
            return jsonify({"message": "Marked as returned"}), 200

        except Exception as e:
            print("[MANAGER RETURN RENTAL ERROR]", e)
            if conn:
                conn.rollback()
            return jsonify({"error": "Error returning rental"}), 500
        finally:
            _safe_close(cursor, conn)
