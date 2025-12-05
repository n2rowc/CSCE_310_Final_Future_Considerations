# frontend/api_client.py
import requests

BASE_URL = "http://localhost:5001"

# Global token storage
_auth_token = None

def set_auth_token(token):
    """Set the authentication token for API requests"""
    global _auth_token
    _auth_token = token

def get_auth_token():
    """Get the current authentication token"""
    return _auth_token

def clear_auth_token():
    """Clear the authentication token"""
    global _auth_token
    _auth_token = None

def _get_headers():
    """Get headers with authentication token if available"""
    headers = {"Content-Type": "application/json"}
    if _auth_token:
        headers["Authorization"] = f"Bearer {_auth_token}"
    return headers


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
        data = resp.json()
        # Store the token for future requests
        if "token" in data:
            set_auth_token(data["token"])
        return data, None
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
        resp = requests.get(f"{BASE_URL}/api/books", params=params, headers=_get_headers())
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
            "items": items  # user_id now comes from token
        }, headers=_get_headers())
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
        resp = requests.get(f"{BASE_URL}/api/history/{user_id}", headers=_get_headers())
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
        resp = requests.get(f"{BASE_URL}/api/books/{book_id}", params=params, headers=_get_headers())
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"

    if resp.status_code == 200:
        return resp.json(), None

    try:
        msg = resp.json().get("error", f"HTTP {resp.status_code}")
    except:
        msg = f"HTTP {resp.status_code}"
    return None, msg


def api_get_book_reviews(book_id: int):
    """Get all reviews for a book"""
    try:
        resp = requests.get(f"{BASE_URL}/api/books/{book_id}/reviews", headers=_get_headers())
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
            "book_id": book_id,
            "rating": rating,
            "review_text": review_text
            # user_id now comes from token
        }, headers=_get_headers())
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
def _safe_json(resp):
    try:
        return resp.json()
    except:
        return {}

def _handle(resp):
    if resp is None:
        return None, "No response"
    if resp.status_code in (200, 201):
        return resp.json(), None
    data = _safe_json(resp)
    return None, data.get("error", f"HTTP {resp.status_code}")
# ============================================================
# MANAGER — ORDERS
# ============================================================

def api_manager_get_orders():
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/orders", headers=_get_headers())
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_update_order_status(order_id: int, new_status: str):
    try:
        resp = requests.patch(
            f"{BASE_URL}/api/manager/orders/{order_id}/status",
            json={"payment_status": new_status},
            headers=_get_headers()
        )
    except Exception as e:
        return False, f"Connection error: {e}"

    if resp.status_code == 200:
        return True, None
    data = _safe_json(resp)
    return False, data.get("error", f"HTTP {resp.status_code}")


# ============================================================
# MANAGER — BOOKS (ADVANCED)
# ============================================================

def api_manager_list_books(params: dict):
    """
    Manager-side search:
    same params as customer search:
    q=, genre=, year=
    """
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/books", params=params, headers=_get_headers())
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_get_book_details(book_id: int):
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/books/{book_id}/details", headers=_get_headers())
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_get_reviews(book_id: int):
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/books/{book_id}/reviews", headers=_get_headers())
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_add_book(title, author, price_buy, price_rent, genre, year):
    try:
        resp = requests.post(f"{BASE_URL}/api/manager/books", json={
            "title": title,
            "author": author,
            "price_buy": price_buy,
            "price_rent": price_rent,
            "genre": genre,
            "publication_year": year
        }, headers=_get_headers())
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_update_book(book_id, title, author,
                            price_buy, price_rent,
                            genre, publication_year,
                            total_copies, available_copies):
    try:
        resp = requests.put(
            f"{BASE_URL}/api/manager/books/{book_id}",
            json={
                "title": title,
                "author": author,
                "price_buy": price_buy,
                "price_rent": price_rent,
                "genre": genre,
                "publication_year": publication_year,
                "total_copies": total_copies,
                "available_copies": available_copies
            },
            headers=_get_headers()
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



def api_manager_update_inventory(book_id: int, increment: int):
    try:
        resp = requests.patch(
            f"{BASE_URL}/api/manager/books/{book_id}/inventory",
            json={"increment": increment},
            headers=_get_headers()
        )
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


# ============================================================
# MANAGER — CUSTOMERS
# ============================================================

def api_manager_search_customers(query: str):
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/customers", params={"q": query}, headers=_get_headers())
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_get_customer(customer_id: int):
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/customers/{customer_id}", headers=_get_headers())
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_get_customer_orders(customer_id: int):
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/customers/{customer_id}/orders", headers=_get_headers())
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_get_customer_rentals(customer_id: int):
    try:
        resp = requests.get(f"{BASE_URL}/api/manager/customers/{customer_id}/rentals", headers=_get_headers())
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_manual_rent(customer_id: int, book_id: int, due_date: str):
    try:
        resp = requests.post(
            f"{BASE_URL}/api/manager/customers/{customer_id}/rentals",
            json={"book_id": book_id, "due_date": due_date},
            headers=_get_headers()
        )
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)


def api_manager_return_rental(rental_id: int):
    try:
        resp = requests.patch(
            f"{BASE_URL}/api/manager/rentals/{rental_id}/return",
            headers=_get_headers()
        )
    except Exception as e:
        return None, f"Connection error: {e}"
    return _handle(resp)
