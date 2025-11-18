# backend/app.py
from flask import Flask
from flask_cors import CORS

import os
from dotenv import load_dotenv

from authorize import init_authorize_routes
from customer import init_customer_routes
from manager import init_manager_routes


def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "fallback-secret")

    # Not strictly required for Tkinter client, but harmless:
    CORS(app)

    # Register route groups
    init_authorize_routes(app)
    init_customer_routes(app)
    init_manager_routes(app)

    return app


if __name__ == "__main__":
    app = create_app()
    print("Backend server running at http://localhost:5001")
    app.run(host="localhost", port=5001, debug=True)
