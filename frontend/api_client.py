# frontend/api_client.py
import requests

BASE_URL = "http://localhost:5001"


# ---------- Auth ----------
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
    else:
        try:
            msg = resp.json().get("error", f"HTTP {resp.status_code}")
        except Exception:
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
    else:
        try:
            msg = resp.json().get("error", f"HTTP {resp.status_code}")
        except Exception:
            msg = f"HTTP {resp.status_code}"
        return None, msg


# ---------- Customer: books & orders ----------
def api_search_books(keyword: str):
    params = {}
    if keyword.strip():
        params["q"] = keyword.strip()

    try:
        resp = requests.get(f"{BASE_URL}/api/books", params=params)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code == 200:
        return resp.json(), None
    else:
        try:
            msg = resp.json().get("error", f"HTTP {resp.status_code}")
        except Exception:
            msg = f"HTTP {resp.status_code}"
        return None, msg


def api_place_order(user_id: int, items):
    """
    items: list of dicts with { "book_id": int, "type": "buy"|"rent" }
    """
    try:
        resp = requests.post(f"{BASE_URL}/api/orders", json={
            "user_id": user_id,
            "items": items
        })
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code in (200, 201):
        return resp.json(), None
    else:
        try:
            msg = resp.json().get("error", f"HTTP {resp.status_code}")
        except Exception:
            msg = f"HTTP {resp.status_code}"
        return None, msg


# ---------- Manager: orders & books ----------
def api_manager_get_orders():
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/orders")
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code == 200:
        return resp.json(), None
    else:
        try:
            msg = resp.json().get("error", f"HTTP {resp.status_code}")
        except Exception:
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
    else:
        try:
            msg = resp.json().get("error", f"HTTP {resp.status_code}")
        except Exception:
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
    else:
        try:
            msg = resp.json().get("error", f"HTTP {resp.status_code}")
        except Exception:
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
    else:
        try:
            msg = resp.json().get("error", f"HTTP {resp.status_code}")
        except Exception:
            msg = f"HTTP {resp.status_code}"
        return False, msg
