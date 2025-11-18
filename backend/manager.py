# backend/manager.py
from flask import request, jsonify
from database import get_db_connection


def init_manager_routes(app):
    # ---------- View all orders ----------
    @app.route("/api/manager/orders", methods=["GET"])
    def manager_list_orders():
        """
        Returns all orders with basic info and their items.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Orders + customer username
            cursor.execute(
                """
                SELECT o.id, o.user_id, u.username AS customer_username,
                       o.total_price, o.payment_status, o.created_at
                FROM orders o
                JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC
                """
            )
            orders = cursor.fetchall()

            # Get items for all these orders
            if orders:
                order_ids = [o["id"] for o in orders]
                fmt = ",".join(["%s"] * len(order_ids))
                cursor.execute(
                    f"""
                    SELECT oi.order_id, oi.book_id, b.title, b.author,
                           oi.type, oi.price
                    FROM order_items oi
                    JOIN books b ON oi.book_id = b.id
                    WHERE oi.order_id IN ({fmt})
                    ORDER BY oi.order_id
                    """,
                    order_ids,
                )
                items_rows = cursor.fetchall()
            else:
                items_rows = []

            # Group items by order_id
            items_by_order = {}
            for r in items_rows:
                items_by_order.setdefault(r["order_id"], []).append({
                    "book_id": r["book_id"],
                    "title": r["title"],
                    "author": r["author"],
                    "type": r["type"],
                    "price": float(r["price"]),
                })

            for o in orders:
                o["total_price"] = float(o["total_price"])
                o["items"] = items_by_order.get(o["id"], [])

            return jsonify(orders), 200

        except Exception as e:
            print("[MANAGER LIST ORDERS ERROR]", e)
            return jsonify({"error": "Error loading orders"}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ---------- Update payment status ----------
    @app.route("/api/manager/orders/<int:order_id>/status", methods=["PATCH"])
    def manager_update_order_status(order_id):
        """
        JSON body: { "payment_status": "Pending" | "Paid" }
        """
        data = request.get_json(silent=True) or {}
        new_status = data.get("payment_status")

        if new_status not in ("Pending", "Paid"):
            return jsonify({"error": "payment_status must be 'Pending' or 'Paid'"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "UPDATE orders SET payment_status = %s WHERE id = %s",
                (new_status, order_id),
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "Order not found"}), 404

            conn.commit()
            return jsonify({"message": "Payment status updated"}), 200

        except Exception as e:
            if conn:
                conn.rollback()
            print("[MANAGER UPDATE STATUS ERROR]", e)
            return jsonify({"error": "Error updating status"}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ---------- Add new book ----------
    @app.route("/api/manager/books", methods=["POST"])
    def manager_add_book():
        """
        JSON body:
        {
          "title": "...",
          "author": "...",
          "price_buy": 12.99,
          "price_rent": 4.99
        }
        """
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        author = (data.get("author") or "").strip()
        price_buy = data.get("price_buy")
        price_rent = data.get("price_rent")

        if not title or not author or price_buy is None or price_rent is None:
            return jsonify({"error": "title, author, price_buy, price_rent required"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                INSERT INTO books (title, author, price_buy, price_rent)
                VALUES (%s, %s, %s, %s)
                """,
                (title, author, price_buy, price_rent),
            )
            conn.commit()
            book_id = cursor.lastrowid

            return jsonify({
                "id": book_id,
                "title": title,
                "author": author,
                "price_buy": float(price_buy),
                "price_rent": float(price_rent)
            }), 201

        except Exception as e:
            if conn:
                conn.rollback()
            print("[MANAGER ADD BOOK ERROR]", e)
            return jsonify({"error": "Error adding book"}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ---------- Update existing book ----------
    @app.route("/api/manager/books/<int:book_id>", methods=["PUT"])
    def manager_update_book(book_id):
        """
        JSON body (all fields required for simplicity):
        {
          "title": "...",
          "author": "...",
          "price_buy": 12.99,
          "price_rent": 4.99
        }
        """
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        author = (data.get("author") or "").strip()
        price_buy = data.get("price_buy")
        price_rent = data.get("price_rent")

        if not title or not author or price_buy is None or price_rent is None:
            return jsonify({"error": "title, author, price_buy, price_rent required"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                UPDATE books
                SET title = %s, author = %s, price_buy = %s, price_rent = %s
                WHERE id = %s
                """,
                (title, author, price_buy, price_rent, book_id),
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "Book not found"}), 404

            conn.commit()
            return jsonify({"message": "Book updated"}), 200

        except Exception as e:
            if conn:
                conn.rollback()
            print("[MANAGER UPDATE BOOK ERROR]", e)
            return jsonify({"error": "Error updating book"}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
