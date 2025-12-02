# frontend/api_client.py
import requests

BASE_URL = "http://localhost:5001"


# ============================================================
# AUTH (UNCHANGED)
# ============================================================

def api_login(username: str, password: str):
    try:
        resp = requests.post(f"{BASE_URL}/api/login", json={
            "username": username,
            "password": password
        })
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code == 200:
        return resp.json(), None
    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"
    return None, msg


def api_register(username: str, email: str, password: str):
    try:
        resp = requests.post(f"{BASE_URL}/api/register", json={
            "username": username,
            "email": email,
            "password": password
        })
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code in (200, 201):
        return resp.json(), None
    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"
    return None, msg


# ============================================================
# CUSTOMER — UNIFIED SEARCH
# ============================================================

def api_search_books(params: dict):
    """
    Unified search:
    q, genre, year, sort_by, direction
    """
    try:
        resp = requests.get(f"{BASE_URL}/api/books", params=params)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code == 200:
        return resp.json(), None

    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"
    return None, msg


def api_place_order(user_id: int, items):
    try:
        resp = requests.post(f"{BASE_URL}/api/orders", json={
            "user_id": user_id,
            "items": items
        })
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code in (200, 201):
        return resp.json(), None

    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"
    return None, msg


# ============================================================
# CUSTOMER — HISTORY / DETAILS / REVIEWS
# ============================================================

def api_get_history(user_id: int):
    try:
        resp = requests.get(f"{BASE_URL}/api/history/{user_id}")
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code == 200:
        return resp.json(), None

    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"
    return None, msg


def api_get_book_details(book_id: int, user_id: int = None):
    params = {"user_id": user_id} if user_id else {}

    try:
        resp = requests.get(f"{BASE_URL}/api/books/{book_id}", params=params)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code == 200:
        return resp.json(), None

    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"
    return None, msg


def api_submit_review(user_id: int, book_id: int, rating: int, review_text: str):
    try:
        resp = requests.post(f"{BASE_URL}/api/reviews", json={
            "user_id": user_id,
            "book_id": book_id,
            "rating": rating,
            "review_text": review_text
        })
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code in (200, 201):
        return resp.json(), None

    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"
    return None, msg


# ============================================================
# MANAGER ENDPOINTS (FIXED SYNTAX)
# ============================================================

def api_manager_get_orders():
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/orders")
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"
    if resp.status_code == 200:
        return resp.json(), None
    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"
    return None, msg


def api_manager_update_order_status(order_id: int, new_status: str):
    try:
        resp = requests.patch(
            f"{BASE_URL}/api/manager/orders/{order_id}/status",
            json={"payment_status": new_status}
        )
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}"

    if resp.status_code == 200:
        return True, None

    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"

    return False, msg


def api_manager_add_book(title, author, price_buy, price_rent):
    try:
        resp = requests.post(f"{BASE_URL}/api/manager/books", json={
            "title": title,
            "author": author,
            "price_buy": price_buy,
            "price_rent": price_rent
        })
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code in (200, 201):
        return resp.json(), None

    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"

    return None, msg


def api_manager_update_book(book_id, title, author, price_buy, price_rent):
    try:
        resp = requests.put(f"{BASE_URL}/api/manager/books/{book_id}", json={
            "title": title,
            "author": author,
            "price_buy": price_buy,
            "price_rent": price_rent
        })
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {e}"

    if resp.status_code == 200:
        return True, None

    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"

    return False, msg
