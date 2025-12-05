# backend/authorize.py
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection
from auth_middleware import create_token, require_auth, get_token_from_request, revoke_token


def init_authorize_routes(app):
    # ---------- Registration (Customer only) ----------
    @app.route("/api/register", methods=["POST"])
    def register():
        """
        JSON body:
        {
          "username": "...",
          "email": "...",
          "password": "..."
        }
        Creates a new *customer* user.
        """
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        if not username or not email or not password:
            return jsonify({"error": "Username, email, and password are required"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Check for duplicates
            cursor.execute(
                "SELECT id FROM users WHERE username = %s OR email = %s",
                (username, email),
            )
            if cursor.fetchone():
                return jsonify({"error": "Username or email already exists"}), 400

            pw_hash = generate_password_hash(password)

            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, role)
                VALUES (%s, %s, %s, 'customer')
                """,
                (username, email, pw_hash),
            )
            conn.commit()
            user_id = cursor.lastrowid

            return jsonify({
                "user_id": user_id,
                "username": username,
                "email": email,
                "role": "customer"
            }), 201

        except Exception as e:
            print("[REGISTER ERROR]", e)
            return jsonify({"error": "Server error during registration"}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ---------- Login ----------
    @app.route("/api/login", methods=["POST"])
    def login():
        """
        JSON body: { "username": "...", "password": "..." }
        Returns: { "user_id": ..., "username": "...", "role": "customer|manager" }
        """
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not username or not password:
            return jsonify({"error": "Username and password are required"}), 400

        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username = %s",
                (username,),
            )
            user = cursor.fetchone()

            if not user:
                return jsonify({"error": "Invalid username or password"}), 401

            if not check_password_hash(user["password_hash"], password):
                return jsonify({"error": "Invalid username or password"}), 401

            # Create authentication token
            token = create_token(user["id"], user["username"], user["role"])

            return jsonify({
                "user_id": user["id"],
                "username": user["username"],
                "role": user["role"],
                "token": token
            }), 200

        except Exception as e:
            print("[LOGIN ERROR]", e)
            return jsonify({"error": "Server error during login"}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    # ---------- Logout ----------
    @app.route("/api/logout", methods=["POST"])
    @require_auth
    def logout():
        """Logout and revoke token"""
        token = get_token_from_request()
        if token:
            revoke_token(token)
        return jsonify({"message": "Logged out successfully"}), 200
