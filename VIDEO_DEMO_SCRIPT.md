# Video Demonstration Script
## Online Bookstore Desktop Application

---

## 📋 PRE-DEMO SETUP

### Before Recording:
1. **Open these windows side-by-side:**
   - Terminal 1: Backend server running (`python3 backend/app.py`)
   - Terminal 2: Ready for curl commands (to show API)
   - VS Code/Editor: Show project structure
   - Desktop App: Frontend running
   - Database viewer (optional): MySQL Workbench or terminal

2. **Have test accounts ready:**
   - Customer account (e.g., "customer1" / "password")
   - Manager account (e.g., "manager1" / "password")

---

## 🎬 VIDEO STRUCTURE (15-20 minutes)

### **PART 1: Introduction & Technology Stack (2-3 min)**

#### 1.1 Project Overview
- [ ] Show desktop application window
- [ ] "This is a desktop bookstore application built with..."
- [ ] Mention: Desktop GUI (not web app)

#### 1.2 Technology Stack Demonstration

**Backend (Python Flask):**
- [ ] Open VS Code/editor
- [ ] Show `backend/app.py` - "This is our Flask backend server"
- [ ] Show `backend/customer.py` - "RESTful API endpoints"
- [ ] Show `backend/manager.py` - "Manager-specific endpoints"
- [ ] **Terminal**: Show backend running - "Server running on localhost:5001"

**Database (MySQL):**
- [ ] Show `sql/schema.sql` - "Our database schema"
- [ ] Point out tables: users, books, orders, order_items, rentals
- [ ] **Optional**: Show database in MySQL Workbench or terminal query

**Frontend (Python Tkinter):**
- [ ] Show `frontend/main.py` - "Main application entry point"
- [ ] Show `frontend/customer_view.py` - "Customer interface"
- [ ] Show `frontend/manager_view.py` - "Manager interface"
- [ ] Show running desktop app - "Native desktop GUI built with Tkinter"

**RESTful API:**
- [ ] Show API structure in code
- [ ] Mention: GET, POST, PUT, PATCH endpoints
- [ ] Show proper HTTP status codes in code comments

---

### **PART 2: Security Features (3-4 min)**

#### 2.1 Password Hashing
- [ ] **Terminal**: Query database to show password hashes
  ```sql
  SELECT username, password_hash FROM users LIMIT 1;
  ```
- [ ] "Passwords are stored as hashes, not plain text"
- [ ] Show `backend/authorize.py` - point to `generate_password_hash()`
- [ ] "Uses bcrypt-based hashing algorithm"

#### 2.2 API Authentication
- [ ] **Terminal**: Try accessing protected endpoint WITHOUT login:
  ```bash
  curl http://localhost:5001/api/books
  ```
- [ ] Show error: "Authentication required" or 401
- [ ] "All endpoints require authentication token"
- [ ] Show `backend/auth_middleware.py` - point to `@require_customer` decorator
- [ ] Show `backend/customer.py` - show decorators on endpoints

#### 2.3 Token-Based Authentication
- [ ] Show login in app
- [ ] **Terminal**: Show login response includes token:
  ```bash
  curl -X POST http://localhost:5001/api/login \
    -H "Content-Type: application/json" \
    -d '{"username":"customer1","password":"password"}'
  ```
- [ ] Point out "token" in response
- [ ] Show `frontend/api_client.py` - show token storage and `_get_headers()`
- [ ] "Token is sent with every authenticated request"

#### 2.4 Authorization (Role-Based Access Control)
- [ ] Login as **customer**
- [ ] **Terminal**: Try accessing manager endpoint as customer:
  ```bash
  curl -H "Authorization: Bearer <customer_token>" \
    http://localhost:5001/api/manager/orders
  ```
- [ ] Show error: "Insufficient permissions" or 403
- [ ] "Customers cannot access manager endpoints"
- [ ] Show `backend/auth_middleware.py` - `@require_manager` decorator
- [ ] Login as **manager** - show it works
- [ ] "Managers have separate, secure access"

#### 2.5 User Data Protection
- [ ] Show `backend/customer.py` - history endpoint
- [ ] Point out: `if current_user_id != user_id: return 403`
- [ ] "Users can only access their own data"
- [ ] Show that `user_id` comes from token, not request body
- [ ] Point to `get_current_user_id()` function

---

### **PART 3: User Account Management (2 min)**

#### 3.1 Registration
- [ ] Click "New user? Register here"
- [ ] Fill in: username, email, password
- [ ] Submit registration
- [ ] Show success message
- [ ] **Terminal**: Show registration API call (optional)

#### 3.2 Login
- [ ] Login with registered account
- [ ] Show welcome message with role
- [ ] "Session established with authentication token"

#### 3.3 Session Persistence
- [ ] After login, navigate through app (Books, Cart, History)
- [ ] "User remains authenticated throughout session"
- [ ] Show logout button
- [ ] Logout - "Token cleared, session ended"

---

### **PART 4: Customer Features (4-5 min)**

#### 4.1 Book Search
- [ ] Show Books view
- [ ] Search by keyword (e.g., "Harry")
- [ ] Show results matching title AND author
- [ ] "Search matches both book titles and author names"
- [ ] Show search results display: Title, Author, Buy Price, Rent Price

#### 4.2 Add to Cart
- [ ] Select a book
- [ ] Click "Add Selected as Buy"
- [ ] Select another book
- [ ] Click "Add Selected as Rent"
- [ ] "Can add multiple books, both buy and rent"

#### 4.3 Place Order
- [ ] Go to "Checkout Cart"
- [ ] Show cart with items and total
- [ ] Click "Place Order"
- [ ] **Show receipt popup** - "Detailed bill generated"
- [ ] Point out: Order ID, Items, Prices, Total
- [ ] "Order created in single transaction"

#### 4.4 Order History
- [ ] Go to "History" tab
- [ ] Show: Purchases, Current Rentals, Past Rentals
- [ ] "Users can view their order history"

---

### **PART 5: Manager Features (3-4 min)**

#### 5.1 Manager Login
- [ ] Logout from customer account
- [ ] Login as manager
- [ ] "Separate login, distinct role"
- [ ] Show manager interface

#### 5.2 View Orders
- [ ] Go to "Orders" tab
- [ ] Show all orders with customer info
- [ ] "Managers can view all buy and rental orders"
- [ ] Show order details (items, prices, status)

#### 5.3 Update Payment Status
- [ ] Select an order
- [ ] Change status from "Pending" to "Paid"
- [ ] Show update success
- [ ] "Managers can update payment status"

#### 5.4 Manage Books
- [ ] Go to "Books" tab
- [ ] **Add new book**: Fill in title, author, prices, genre, year
- [ ] Submit - "New book added"
- [ ] **Edit existing book**: Select book, update information
- [ ] Update inventory (total copies, available copies)
- [ ] "Managers can add and update book information"

---

### **PART 6: Additional Features (1-2 min)**

#### 6.1 Book Reviews
- [ ] As customer, go to History
- [ ] Select a purchased book
- [ ] Click "Leave a Review"
- [ ] Submit rating and review
- [ ] "Users can review books they've purchased or rented"

#### 6.2 Advanced Search
- [ ] Show search filters: Genre, Year
- [ ] Demonstrate filtering
- [ ] "Advanced search capabilities beyond basic keyword"

---

### **PART 7: Summary & Code Structure (1 min)**

#### 7.1 Project Structure
- [ ] Show folder structure:
  ```
  backend/     - Flask API
  frontend/    - Tkinter GUI
  sql/         - Database schema
  ```
- [ ] "Clean separation of concerns"

#### 7.2 Key Files
- [ ] Quick overview of main files
- [ ] "RESTful API design"
- [ ] "Secure authentication and authorization"

---

## 🎯 KEY POINTS TO EMPHASIZE

### Technology Stack:
1. ✅ **Backend**: Python Flask (show code)
2. ✅ **Database**: MySQL (show schema)
3. ✅ **Frontend**: Python Tkinter (show running app)
4. ✅ **API**: RESTful design (show endpoints)

### Security:
1. ✅ **Password Hashing**: Show hashed passwords in DB
2. ✅ **API Authentication**: Show 401 error without token
3. ✅ **Token System**: Show token in login response
4. ✅ **Authorization**: Show 403 error (customer trying manager endpoint)
5. ✅ **Data Protection**: Show user_id validation

---

## 📝 DEMONSTRATION TIPS

### For Technology Stack:
- **Show code, don't just talk** - Point to actual files
- **Show running processes** - Terminal with server running
- **Show database** - Schema file or actual DB query
- **Mention RESTful** - Point out HTTP methods in code

### For Security:
- **Show failures first** - Try without auth, show error
- **Then show success** - With proper auth
- **Compare** - Customer vs Manager access
- **Show code** - Point to security decorators

### General Tips:
- **Speak clearly** - Explain what you're doing
- **Show, don't just tell** - Demonstrate features
- **Use real data** - Make it look realistic
- **Test beforehand** - Make sure everything works
- **Keep it concise** - 15-20 minutes total

---

## 🔧 QUICK REFERENCE COMMANDS

### Terminal Commands for Demo:

**Start Backend:**
```bash
cd backend
python3 app.py
```

**Test Authentication (No Token):**
```bash
curl http://localhost:5001/api/books
```

**Login and Get Token:**
```bash
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"customer1","password":"password"}'
```

**Test with Token:**
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:5001/api/books
```

**Test Authorization (Customer trying Manager):**
```bash
curl -H "Authorization: Bearer <CUSTOMER_TOKEN>" \
  http://localhost:5001/api/manager/orders
```

**Show Password Hash:**
```sql
SELECT username, password_hash FROM users WHERE username='customer1';
```

---

## ✅ CHECKLIST BEFORE RECORDING

- [ ] Backend server is running
- [ ] Frontend application is ready
- [ ] Test accounts exist (customer + manager)
- [ ] Terminal windows open for API testing
- [ ] Code editor open showing project structure
- [ ] Database accessible (optional)
- [ ] All features tested and working
- [ ] Screen recording software ready
- [ ] Audio/microphone working

---

**Good luck with your demonstration! 🎬**
