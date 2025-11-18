# backend/customer.py
from flask import request, jsonify
from database import get_db_connection


def init_customer_routes(app):
    # ---------- Book search / listing ----------
    @app.route("/api/books", methods=["GET"])
    def search_books():
        """
        GET /api/books?q=keyword   (q optional)
        Searches title and author, returns list of books.
        """
        keyword = (request.args.get("q") or "").strip()

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            if keyword:
                like = f"%{keyword}%"
                cursor.execute(
                    """
                    SELECT id, title, author, price_buy, price_rent
                    FROM books
                    WHERE title LIKE %s OR author LIKE %s
                    ORDER BY title
                    """,
                    (like, like),
                )
            else:
                cursor.execute(
                    """
                    SELECT id, title, author, price_buy, price_rent
                    FROM books
                    ORDER BY title
                    LIMIT 100
                    """
                )

            books = cursor.fetchall()
            return jsonify(books), 200

        except Exception as e:
            print("[SEARCH BOOKS ERROR]", e)
            return jsonify({"error": "Error searching books"}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ---------- Place order (buy / rent) ----------
    @app.route("/api/orders", methods=["POST"])
    def place_order():
        """
        JSON body:
        {
          "user_id": 2,
          "items": [
            {"book_id": 1, "type": "buy"},
            {"book_id": 3, "type": "rent"}
          ]
        }

        Creates an order with payment_status = 'Pending',
        inserts into orders + order_items, and returns a "bill".
        """
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        items = data.get("items") or []

        if not user_id or not items:
            return jsonify({"error": "user_id and items are required"}), 400

        # Validate item structure
        for item in items:
            if "book_id" not in item or "type" not in item:
                return jsonify({"error": "Each item needs book_id and type"}), 400
            if item["type"] not in ("buy", "rent"):
                return jsonify({"error": "Item type must be 'buy' or 'rent'"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Fetch all involved books
            book_ids = list({i["book_id"] for i in items})
            format_str = ",".join(["%s"] * len(book_ids))
            cursor.execute(
                f"""
                SELECT id, title, author, price_buy, price_rent
                FROM books
                WHERE id IN ({format_str})
                """,
                book_ids,
            )
            book_rows = cursor.fetchall()
            book_map = {b["id"]: b for b in book_rows}

            # Compute prices + total
            bill_items = []
            total_price = 0.0

            for item in items:
                b = book_map.get(item["book_id"])
                if not b:
                    return jsonify({"error": f"Book id {item['book_id']} not found"}), 400

                if item["type"] == "buy":
                    price = float(b["price_buy"])
                else:
                    price = float(b["price_rent"])

                total_price += price

                bill_items.append({
                    "book_id": b["id"],
                    "title": b["title"],
                    "author": b["author"],
                    "type": item["type"],
                    "price": price
                })

            # Insert into orders (payment_status Pending)
            cursor.execute(
                """
                INSERT INTO orders (user_id, total_price, payment_status)
                VALUES (%s, %s, 'Pending')
                """,
                (user_id, total_price),
            )
            order_id = cursor.lastrowid

            # Insert into order_items
            for bi in bill_items:
                cursor.execute(
                    """
                    INSERT INTO order_items (order_id, book_id, type, price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, bi["book_id"], bi["type"], bi["price"]),
                )

            conn.commit()

            bill = {
                "order_id": order_id,
                "user_id": user_id,
                "items": bill_items,
                "total_price": total_price,
                "payment_status": "Pending"
            }

            # In a real app, you'd send this bill via email here.
            print("[BILL GENERATED]", bill)

            return jsonify(bill), 201

        except Exception as e:
            if conn:
                conn.rollback()
            print("[PLACE ORDER ERROR]", e)
            return jsonify({"error": "Error placing order"}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
