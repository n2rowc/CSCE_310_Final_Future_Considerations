# ============================================================
# frontend/manager_view.py  (FULL REWRITE)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime

from api_client import (
    api_manager_get_orders,
    api_manager_update_order_status,
    api_manager_list_books,
    api_manager_get_book_details,
    api_manager_get_reviews,
    api_manager_add_book,
    api_manager_update_book,
    api_manager_update_inventory,
    api_manager_search_customers,
    api_manager_get_customer,
    api_manager_get_customer_orders,
    api_manager_get_customer_rentals,
    api_manager_manual_rent,
    api_manager_return_rental,
)

# ============================================================
# STYLE CONSTANTS (UNCHANGED FROM ORIGINAL)
# ============================================================

PRIMARY_BG = "#f7f1e3"
NAV_BG = "#3b3a30"
NAV_FG = "#fdfaf3"
ACCENT = "#8b0000"
TEXT_COLOR = "#2b2b2b"

BUTTON_BG = "#d2b48c"
BUTTON_FG = "#8b0000"
BUTTON_BLACK = "#000000"

TITLE_FONT = ("Georgia", 20, "bold")
LABEL_FONT = ("Georgia", 12)
NAV_FONT = ("Georgia", 12, "bold")


# ============================================================
# MANAGER FRAME (FULL REWRITE)
# ============================================================

class ManagerFrame(tk.Frame):

    def __init__(self, master, controller):
        super().__init__(master, bg=PRIMARY_BG)

        self.pretty_headers = {
            "id": "ID",
            "title": "Title",
            "author": "Author",
            "buy": "Buy Price",
            "rent": "Rent Price",
            "total_copies": "Total Copies",
            "available_copies": "Available Copies",
            "rating": "Avg Rating",
            "genre": "Genre",
            "year": "Year",
            "date": "Date Added",
            "customer": "Customer",
            "total": "Total",
            "status": "Status",
            "created": "Created At",
            "email": "Email",
            "username": "Username",
        }

        self.controller = controller
        self.user_info = controller.user_info

        # Sorting state tracking (column_name → "asc" or "desc")
        self.sort_states = {}

        # Data caches
        self.book_rows = []
        self.customer_rows = []
        self.order_rows = []

        # Build UI
        self._build_nav()
        self._build_content()

        # Default view
        self.show_orders_view()

    # ========================================================
    # NAVIGATION BAR
    # ========================================================

    def _build_nav(self):
        nav = tk.Frame(self, bg=NAV_BG, height=50)
        nav.pack(side="top", fill="x")

        title = tk.Label(
            nav,
            text=f"Manager: {self.user_info['username']}",
            bg=NAV_BG,
            fg=NAV_FG,
            font=TITLE_FONT,
        )
        title.pack(side="left", padx=20)

        # ---- Orders button ----
        btn_orders = tk.Button(
            nav, text="Orders",
            command=self.show_orders_view,
            bg=NAV_BG, fg=BUTTON_BLACK,
            font=NAV_FONT, relief="flat"
        )
        btn_orders.pack(side="left", padx=10)

        # ---- Manage Books ----
        btn_books = tk.Button(
            nav, text="Manage Books",
            command=self.show_books_view,
            bg=NAV_BG, fg=BUTTON_BLACK,
            font=NAV_FONT, relief="flat"
        )
        btn_books.pack(side="left", padx=10)

        # ---- Customers ----
        btn_customers = tk.Button(
            nav, text="Customers",
            command=self.show_customers_view,
            bg=NAV_BG, fg=BUTTON_BLACK,
            font=NAV_FONT, relief="flat"
        )
        btn_customers.pack(side="left", padx=10)

        # ---- Logout ----
        btn_logout = tk.Button(
            nav, text="Logout",
            command=self.controller.logout,
            bg=NAV_BG, fg=BUTTON_BLACK,
            font=NAV_FONT, relief="flat"
        )
        btn_logout.pack(side="right", padx=20)

    # ========================================================
    # CONTENT AREA ROOT
    # ========================================================

    def _build_content(self):
        self.content = tk.Frame(self, bg=PRIMARY_BG)
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    # ========================================================
    # VIEW SWITCHERS — STUBS (IMPLEMENTED IN LATER SECTIONS)
    # ========================================================

    def show_orders_view(self):
        """Loads the full Orders page."""
        self._clear_content()
        self._build_orders_view()

    def show_books_view(self):
        """Loads the Manage Books page."""
        self._clear_content()
        self._build_books_view()

    def show_customers_view(self):
        """Loads the Customer Management page."""
        self._clear_content()
        self._build_customers_view()

    # ========================================================
    # SHARED: SORTING LOGIC FOR TREEVIEWS
    # ========================================================

    def sort_treeview(self, tree, column_id, col_index):
        """Sort a treeview column in asc/desc order with arrow indicator."""
        # Extract rows
        rows = [(tree.set(k, column_id), k) for k in tree.get_children("")]

        # Convert values for numeric columns
        def convert(v):
            """Return a consistent sortable key: (type_tag, value)

            type_tag: 0 = numeric, 1 = string, 2 = empty
            This avoids comparing different Python types directly.
            """
            if v is None or v == "":
                return (2, "")

            # Try to convert to float first (handles IDs, prices, ratings, etc.)
            try:
                num = float(str(v).replace("$", "").strip())
                return (0, num)
            except (ValueError, AttributeError):
                # Fall back to string comparison (case-insensitive)
                return (1, str(v).lower())

        rows = [(convert(v), k) for (v, k) in rows]

        # Determine direction
        prev = self.sort_states.get(column_id, "none")
        direction = "asc" if prev != "asc" else "desc"
        self.sort_states[column_id] = direction

        reverse = (direction == "desc")
        rows.sort(reverse=reverse, key=lambda x: x[0])

        # Reinsert sorted rows
        for index, (_, k) in enumerate(rows):
            tree.move(k, "", index)

        # Update column headers with arrows
        for col in tree["columns"]:
            label = self.pretty_headers.get(col, col)

            # Add arrow only to selected column
            if col == column_id:
                arrow = " ↑" if direction == "asc" else " ↓"
                label = label + arrow

            # Preserve nice formatting
            tree.heading(col, text=label, command=lambda c=col: self.sort_treeview(tree, c, 0))



    # ========================================================
    # SECTION 2 — ORDERS PAGE
    # ========================================================

    def _build_orders_view(self):
        """Full Orders page with sorting + detail panel + mark paid."""
        
        # ------------------ HEADER ------------------
        header = tk.Frame(self.content, bg=PRIMARY_BG)
        header.pack(fill="x")

        tk.Label(
            header, text="All Orders",
            bg=PRIMARY_BG, fg=ACCENT, font=TITLE_FONT
        ).pack(side="left")

        refresh_btn = tk.Button(
            header, text="Refresh",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=self.load_orders
        )
        refresh_btn.pack(side="right", padx=5)

        # ------------------ TABLE ------------------
        table_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))

        columns = ("id", "customer", "total", "status", "created")
        self.orders_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=14
        )

        headings = {
            "id": "Order ID",
            "customer": "Customer",
            "total": "Total",
            "status": "Status",
            "created": "Created At"
        }

        for col in columns:
            self.orders_tree.heading(
                col, text=headings[col],
                command=lambda c=col: self.sort_treeview(self.orders_tree, c, 0)
            )

        self.orders_tree.column("id", width=80, anchor="center")
        self.orders_tree.column("customer", width=160)
        self.orders_tree.column("total", width=100, anchor="e")
        self.orders_tree.column("status", width=110, anchor="center")
        self.orders_tree.column("created", width=180, anchor="center")

        self.orders_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=self.orders_tree.yview
        )
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.orders_tree.bind("<<TreeviewSelect>>", self.show_order_details)

        # ------------------ DETAILS + BUTTONS ------------------
        bottom = tk.Frame(self.content, bg=PRIMARY_BG)
        bottom.pack(fill="x", pady=(10, 0))

        self.order_details = tk.Text(
            bottom, bg=PRIMARY_BG, fg=TEXT_COLOR,
            height=10, font=("Courier New", 10)
        )
        self.order_details.pack(side="left", fill="both", expand=True)

        button_frame = tk.Frame(bottom, bg=PRIMARY_BG)
        button_frame.pack(side="right", padx=10)

        self.btn_set_paid = tk.Button(
            button_frame, text="Mark as Paid",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=lambda: self.change_order_status("Paid")
        )
        self.btn_set_paid.pack(pady=5, fill="x")

        self.btn_set_pending = tk.Button(
            button_frame, text="Mark as Pending",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=lambda: self.change_order_status("Pending")
        )
        self.btn_set_pending.pack(pady=5, fill="x")

        # ------------------ LOAD INITIAL DATA ------------------
        self.load_orders()


    # ========================================================
    # Load Orders
    # ========================================================

    def load_orders(self):
        self.orders_tree.delete(*self.orders_tree.get_children())

        orders, error = api_manager_get_orders()
        if error:
            messagebox.showerror("Error", error)
            return

        self.order_rows = orders

        for o in orders:
            self.orders_tree.insert(
                "", "end", iid=str(o["id"]),
                values=(
                    o["id"],
                    o["customer_username"],
                    f"${o['total_price']:.2f}",
                    o["payment_status"],
                    o["created_at"]
                )
            )

        self.order_details.delete("1.0", "end")
        self.order_details.insert("1.0", "Select an order to see details.")


    # ========================================================
    # Show Selected Order in Sidebar
    # ========================================================

    def show_order_details(self, event=None):
        sel = self.orders_tree.selection()
        if not sel:
            return

        order_id = int(sel[0])
        order = None
        for o in self.order_rows:
            if o["id"] == order_id:
                order = o
                break

        if not order:
            return

        lines = [
            f"Order ID: {order['id']}",
            f"Customer: {order['customer_username']} (ID {order['user_id']})",
            f"Status: {order['payment_status']}",
            f"Total: ${order['total_price']:.2f}",
            "",
            "Items:",
            "-" * 50
        ]

        for item in order.get("items", []):
            lines.append(
                f"{item['title']} ({item['type']}) — ${item['price']:.2f}"
            )

        self.order_details.delete("1.0", "end")
        self.order_details.insert("1.0", "\n".join(lines))


    # ========================================================
    # Change Order Status
    # ========================================================

    def change_order_status(self, new_status):
        sel = self.orders_tree.selection()
        if not sel:
            messagebox.showwarning("Select Order", "Select an order first.")
            return

        order_id = int(sel[0])

        confirm = messagebox.askyesno(
            "Confirm",
            f"Change Order #{order_id} to '{new_status}'?"
        )
        if not confirm:
            return

        ok, error = api_manager_update_order_status(order_id, new_status)
        if error:
            messagebox.showerror("Error", error)
            return

        self.load_orders()
        messagebox.showinfo("Success", f"Order marked as {new_status}.")


    # ========================================================
    # SECTION 3 — MANAGE BOOKS PAGE
    # ========================================================

    def _build_books_view(self):
        """Manage Books: advanced search + sortable table + edit form."""

        # ------------------ HEADER ------------------
        header = tk.Frame(self.content, bg=PRIMARY_BG)
        header.pack(fill="x")

        tk.Label(
            header, text="Manage Books",
            bg=PRIMARY_BG, fg=ACCENT, font=TITLE_FONT
        ).pack(side="left")

        # ------------------ ADVANCED SEARCH BAR ------------------
        search_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        search_frame.pack(fill="x", pady=(10, 0))

        # Keyword
        tk.Label(search_frame, text="Search:", bg=PRIMARY_BG, font=LABEL_FONT).pack(side="left")
        self.book_search_q = tk.Entry(search_frame, width=25, font=LABEL_FONT)
        self.book_search_q.pack(side="left", padx=5)

        # Genre
        tk.Label(search_frame, text="Genre:", bg=PRIMARY_BG, font=LABEL_FONT).pack(side="left")
        self.book_search_genre = tk.Entry(search_frame, width=15, font=LABEL_FONT)
        self.book_search_genre.pack(side="left", padx=5)

        # Year
        tk.Label(search_frame, text="Year:", bg=PRIMARY_BG, font=LABEL_FONT).pack(side="left")
        self.book_search_year = tk.Entry(search_frame, width=10, font=LABEL_FONT)
        self.book_search_year.pack(side="left", padx=5)


        search_btn = tk.Button(
            search_frame, text="Search",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=self.load_books
        )
        search_btn.pack(side="left", padx=10)

        # ------------------ BOOKS TABLE ------------------
        table_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))

        columns = (
            "id", "title", "author", "buy", "rent",
            "total_copies", "available_copies",
            "rating", "genre", "year", "date"
        )


        self.books_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=12
        )
        # Removed TreeviewSelect binding since form is gone


        headings = {
            "id": "ID (hidden)",
            "title": "Title",
            "author": "Author",
            "buy": "Buy Price",
            "rent": "Rent Price",
            "total_copies": "Total Copies",
            "available_copies": "Available Copies",
            "rating": "Avg Rating",
            "genre": "Genre",
            "year": "Year",
            "date": "Date Added",
        }


        for col in columns:
            label = headings[col]
            if col == "id":
                label = ""  # hide ID header
            self.books_tree.heading(
                col, text=label,
                command=lambda c=col: self.sort_treeview(self.books_tree, c, 0)
            )

        # Column widths
        self.books_tree.column("id", width=0, stretch=False)  # Hidden
        self.books_tree.column("title", width=250)
        self.books_tree.column("author", width=180)
        self.books_tree.column("buy", width=80, anchor="e")
        self.books_tree.column("rent", width=80, anchor="e")
        self.books_tree.column("total_copies", width=110, anchor="center")
        self.books_tree.column("available_copies", width=130, anchor="center")
        self.books_tree.column("rating", width=100, anchor="center")
        self.books_tree.column("genre", width=120)
        self.books_tree.column("year", width=80, anchor="center")
        self.books_tree.column("date", width=150)

        self.books_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=self.books_tree.yview
        )
        self.books_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Removed double-click binding - use "Edit Selected Item" button instead

        # ------------------ BOOK ACTION BUTTONS ------------------
        btn_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        btn_frame.pack(fill="x", pady=(10, 0), padx=10)

        add_btn = tk.Button(
            btn_frame, text="Add New Book",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=self.add_new_book
        )
        add_btn.pack(side="left", padx=5)

        edit_popup_btn = tk.Button(
            btn_frame, text="Edit Selected Item",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=self.open_edit_book_popup
        )
        edit_popup_btn.pack(side="left", padx=5)

        reviews_btn = tk.Button(
            btn_frame, text="View Reviews",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=self.open_book_reviews_popup
        )
        reviews_btn.pack(side="left", padx=5)

        # ------------------ LOAD INITIAL BOOKS ------------------
        self.load_books()


    # ========================================================
    # Load Books
    # ========================================================

    def load_books(self):
        params = {
            "q": self.book_search_q.get().strip(),
            "genre": self.book_search_genre.get().strip(),
            "year": self.book_search_year.get().strip(),
        }

        books, error = api_manager_list_books(params)
        if error:
            messagebox.showerror("Error", error)
            return

        # Cache
        self.book_rows = books

        # Clear table
        self.books_tree.delete(*self.books_tree.get_children())

        for b in books:
            self.books_tree.insert(
                "",
                "end",
                iid=str(b["id"]),
                values=(
                    b["id"],
                    b["title"],
                    b["author"],
                    f"${b['price_buy']:.2f}",
                    f"${b['price_rent']:.2f}",
                    b["total_copies"],
                    b["available_copies"],
                        ("N/A" if (b.get('review_count') is None or b.get('review_count') == 0) else f"{b['avg_rating']:.1f}"),
                    b["genre"] or "",
                    b["publication_year"] or "",
                    b["created_at"]
                )

            )

    # ========================================================
    # Add New Book
    # ========================================================

    def add_new_book(self):
        try:
            price_buy = float(self.form_buy.get())
            price_rent = float(self.form_rent.get())
        except:
            messagebox.showwarning("Invalid", "Enter numeric prices.")
            return

        book, error = api_manager_add_book(
            self.form_title.get().strip(),
            self.form_author.get().strip(),
            price_buy,
            price_rent,
            self.form_genre.get().strip(),
            self.form_year.get().strip()
        )

        if error:
            messagebox.showerror("Error Adding Book", error)
            return

        messagebox.showinfo("Success", "Book added.")
        self.load_books()

    # ========================================================
    # Update Selected Book
    # ========================================================

    def update_selected_book(self):
        sel = self.books_tree.selection()
        if not sel:
            messagebox.showwarning("Select Book", "Select a book first.")
            return

        book_id = int(sel[0])

        try:
            pb = float(self.form_buy.get())
            pr = float(self.form_rent.get())
        except:
            messagebox.showwarning("Invalid", "Prices must be numeric.")
            return

        ok, error = api_manager_update_book(
            book_id,
            self.form_title.get().strip(),
            self.form_author.get().strip(),
            pb,
            pr,
            self.form_genre.get().strip(),
            self.form_year.get().strip(),
            self.form_total_copies.get().strip(),
            self.form_available_copies.get().strip(),
        )


        if error:
            messagebox.showerror("Error", error)
            return

        messagebox.showinfo("Success", "Book updated.")
        self.load_books()

    # ========================================================
    # Double-Click Book → Book Popup
    # ========================================================

    def open_book_popup(self, event=None):
        # Determine where the click happened
        region = self.books_tree.identify_region(event.x, event.y)

        # Only allow popup for real table cells
        if region != "cell":
            return

        sel = self.books_tree.selection()
        if not sel:
            return

        book_id = int(sel[0])
        self._open_book_details_modal(book_id)

    def open_edit_book_popup(self):
        """Open a popup to edit selected book"""
        sel = self.books_tree.selection()
        if not sel:
            messagebox.showwarning("Select Book", "Please select a book to edit.")
            return
        
        book_id = int(sel[0])
        
        # Find the book in our list
        book = None
        for b in self.book_rows:
            if b["id"] == book_id:
                book = b
                break
        
        if not book:
            messagebox.showerror("Error", "Book not found.")
            return
        
        # Create edit popup
        win = tk.Toplevel(self)
        win.title(f"Edit Book - {book['title']}")
        win.geometry("500x450")
        win.configure(bg=PRIMARY_BG)
        win.transient(self)
        win.grab_set()
        
        # Header
        tk.Label(
            win, text=f"Edit Book - ID {book_id}",
            bg=PRIMARY_BG, fg=ACCENT, font=TITLE_FONT
        ).pack(pady=10)
        
        # Form
        form = tk.Frame(win, bg=PRIMARY_BG)
        form.pack(fill="x", padx=20)
        
        # Title
        tk.Label(form, text="Title:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=0, column=0, sticky="e", pady=5)
        title_var = tk.StringVar(value=book.get("title", ""))
        tk.Entry(form, textvariable=title_var, width=40, font=LABEL_FONT).grid(row=0, column=1, padx=5)
        
        # Author
        tk.Label(form, text="Author:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=1, column=0, sticky="e", pady=5)
        author_var = tk.StringVar(value=book.get("author", ""))
        tk.Entry(form, textvariable=author_var, width=40, font=LABEL_FONT).grid(row=1, column=1, padx=5)
        
        # Buy Price
        tk.Label(form, text="Buy Price:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=2, column=0, sticky="e", pady=5)
        buy_var = tk.StringVar(value=str(book.get("price_buy", "")))
        tk.Entry(form, textvariable=buy_var, width=15, font=LABEL_FONT).grid(row=2, column=1, sticky="w", padx=5)
        
        # Rent Price
        tk.Label(form, text="Rent Price:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=3, column=0, sticky="e", pady=5)
        rent_var = tk.StringVar(value=str(book.get("price_rent", "")))
        tk.Entry(form, textvariable=rent_var, width=15, font=LABEL_FONT).grid(row=3, column=1, sticky="w", padx=5)
        
        # Genre
        tk.Label(form, text="Genre:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=4, column=0, sticky="e", pady=5)
        genre_var = tk.StringVar(value=book.get("genre", ""))
        tk.Entry(form, textvariable=genre_var, width=30, font=LABEL_FONT).grid(row=4, column=1, sticky="w", padx=5)
        
        # Year
        tk.Label(form, text="Publication Year:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=5, column=0, sticky="e", pady=5)
        year_var = tk.StringVar(value=str(book.get("publication_year", "")))
        tk.Entry(form, textvariable=year_var, width=15, font=LABEL_FONT).grid(row=5, column=1, sticky="w", padx=5)
        
        # Total Copies
        tk.Label(form, text="Total Copies:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=6, column=0, sticky="e", pady=5)
        total_var = tk.StringVar(value=str(book.get("total_copies", "")))
        tk.Entry(form, textvariable=total_var, width=15, font=LABEL_FONT).grid(row=6, column=1, sticky="w", padx=5)
        
        # Available Copies
        tk.Label(form, text="Available Copies:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=7, column=0, sticky="e", pady=5)
        available_var = tk.StringVar(value=str(book.get("available_copies", "")))
        tk.Entry(form, textvariable=available_var, width=15, font=LABEL_FONT).grid(row=7, column=1, sticky="w", padx=5)
        
        # Buttons
        btn_frame = tk.Frame(win, bg=PRIMARY_BG)
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        def save_changes():
            try:
                _, err = api_manager_update_book(
                    book_id,
                    title_var.get(),
                    author_var.get(),
                    float(buy_var.get()),
                    float(rent_var.get()),
                    genre_var.get(),
                    year_var.get() or None,
                    int(total_var.get()),
                    int(available_var.get())
                )
                if err:
                    messagebox.showerror("Error", err)
                else:
                    messagebox.showinfo("Success", "Book updated successfully.")
                    win.destroy()
                    self.load_books()
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
        
        tk.Button(
            btn_frame, text="Save Changes",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=save_changes
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame, text="Cancel",
            bg=BUTTON_BG, fg=BUTTON_FG, font=LABEL_FONT,
            command=win.destroy
        ).pack(side="left", padx=5)


    # ========================================================
    # View Book Reviews Popup
    # ========================================================

    def open_book_reviews_popup(self):
        """Open a popup showing only reviews for the selected book"""
        sel = self.books_tree.selection()
        if not sel:
            messagebox.showwarning("Select Book", "Please select a book to view reviews.")
            return
        
        book_id = int(sel[0])
        
        # Find the book in our list
        book = None
        for b in self.book_rows:
            if b["id"] == book_id:
                book = b
                break
        
        if not book:
            messagebox.showerror("Error", "Book not found.")
            return
        
        # Fetch book details (for average rating) and reviews
        book_details, err_details = api_manager_get_book_details(book_id)
        if err_details:
            messagebox.showerror("Error", err_details)
            return
        
        reviews, err = api_manager_get_reviews(book_id)
        if err:
            messagebox.showerror("Error", err)
            return
        
        # Create reviews popup
        win = tk.Toplevel(self)
        win.title(f"Reviews - {book['title']}")
        win.geometry("500x700")
        win.configure(bg=PRIMARY_BG)
        win.transient(self)
        win.grab_set()
        
        # Header
        tk.Label(
            win, text=f"Reviews for '{book['title']}'",
            bg=PRIMARY_BG, fg=ACCENT, font=TITLE_FONT
        ).pack(pady=10)
        
        # Average Rating Display
        avg_rating_frame = tk.Frame(win, bg=PRIMARY_BG)
        avg_rating_frame.pack(pady=(0, 10))
        
        if book_details.get("avg_rating") is not None:
            avg_rating_text = f"Average Rating: {book_details['avg_rating']:.1f} ({book_details.get('review_count', 0)} reviews)"
        else:
            avg_rating_text = f"Average Rating: N/A ({book_details.get('review_count', 0)} reviews)"
        
        tk.Label(
            avg_rating_frame,
            text=avg_rating_text,
            bg=PRIMARY_BG,
            fg=TEXT_COLOR,
            font=("Georgia", 14, "bold")
        ).pack()
        
        # Reviews Section
        reviews_section = tk.Frame(win, bg=PRIMARY_BG)
        reviews_section.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        tk.Label(
            reviews_section,
            text="All Reviews:",
            font=("Georgia", 14, "bold"),
            bg=PRIMARY_BG,
            fg=ACCENT
        ).pack(anchor="w", pady=(5, 5))
        
        # Scrollable frame for reviews
        reviews_canvas = tk.Canvas(reviews_section, bg=PRIMARY_BG, highlightthickness=0, height=500)
        reviews_scrollbar = ttk.Scrollbar(reviews_section, orient="vertical", command=reviews_canvas.yview)
        reviews_scrollable = tk.Frame(reviews_canvas, bg=PRIMARY_BG)
        
        reviews_scrollable.bind(
            "<Configure>",
            lambda e: reviews_canvas.configure(scrollregion=reviews_canvas.bbox("all"))
        )
        
        reviews_canvas.create_window((0, 0), window=reviews_scrollable, anchor="nw")
        reviews_canvas.configure(yscrollcommand=reviews_scrollbar.set)
        
        # Display reviews in comment-style format
        if not reviews:
            tk.Label(
                reviews_scrollable,
                text="No reviews yet.",
                bg=PRIMARY_BG,
                fg=TEXT_COLOR,
                font=("Georgia", 11, "italic")
            ).pack(anchor="w", padx=5, pady=5)
        else:
            for review in reviews:
                # Create a frame for each review (like a comment)
                review_frame = tk.Frame(reviews_scrollable, bg="#f0f0f0", relief="raised", bd=1)
                review_frame.pack(fill="x", padx=5, pady=5)
                
                # Username and rating header
                header_frame = tk.Frame(review_frame, bg="#f0f0f0")
                header_frame.pack(fill="x", padx=8, pady=(8, 4))
                
                username_label = tk.Label(
                    header_frame,
                    text=f"@{review['username']}",
                    bg="#f0f0f0",
                    fg=ACCENT,
                    font=("Georgia", 11, "bold")
                )
                username_label.pack(side="left")
                
                # Rating stars
                rating_stars = "★" * review['rating'] + "☆" * (5 - review['rating'])
                rating_label = tk.Label(
                    header_frame,
                    text=rating_stars,
                    bg="#f0f0f0",
                    fg="#FFA500",
                    font=("Georgia", 10)
                )
                rating_label.pack(side="left", padx=(10, 0))
                
                # Review text
                if review.get('review_text'):
                    review_text_label = tk.Label(
                        review_frame,
                        text=review['review_text'],
                        bg="#f0f0f0",
                        fg=TEXT_COLOR,
                        font=LABEL_FONT,
                        justify="left",
                        wraplength=450
                    )
                    review_text_label.pack(anchor="w", padx=8, pady=(0, 4))
                
                # Date
                date_str = review.get('created_at', '')
                if date_str:
                    # Format date if needed
                    try:
                        from datetime import datetime as dt
                        if isinstance(date_str, str):
                            # Handle MySQL datetime format
                            date_str_clean = date_str.split('.')[0] if '.' in date_str else date_str
                            date_obj = dt.strptime(date_str_clean, '%Y-%m-%d %H:%M:%S')
                            date_str = date_obj.strftime('%B %d, %Y')
                    except Exception:
                        # If parsing fails, use original string
                        pass
                
                date_label = tk.Label(
                    review_frame,
                    text=date_str,
                    bg="#f0f0f0",
                    fg="#666666",
                    font=("Georgia", 9, "italic")
                )
                date_label.pack(anchor="w", padx=8, pady=(0, 8))
        
        reviews_canvas.pack(side="left", fill="both", expand=True)
        reviews_scrollbar.pack(side="right", fill="y")
        
        # Update scroll region
        reviews_canvas.update_idletasks()
        reviews_canvas.configure(scrollregion=reviews_canvas.bbox("all"))
        
        # Close button
        tk.Button(
            win, text="Close",
            bg=BUTTON_BG, fg=BUTTON_FG, font=LABEL_FONT,
            command=win.destroy
        ).pack(pady=10)


    # ========================================================
    # SECTION 4 — BOOK DETAILS POPUP (REVIEWS + INVENTORY)
    # ========================================================

    def _open_book_details_modal(self, book_id):
        """Create a popup showing full book details, reviews, and inventory tools."""

        # ------------------ FETCH BOOK DETAILS ------------------
        book, error = api_manager_get_book_details(book_id)
        if error:
            messagebox.showerror("Error", error)
            return

        reviews, err2 = api_manager_get_reviews(book_id)
        if err2:
            messagebox.showerror("Error", err2)
            return

        # ------------------ POPUP WINDOW ------------------
        win = tk.Toplevel(self)
        win.title(f"Book #{book_id} Details")
        win.configure(bg=PRIMARY_BG)
        win.geometry("780x600")

        # Make modal
        win.transient(self)
        win.grab_set()

        # ------------------ HEADER ------------------
        header = tk.Label(
            win, text=f"Book Details — ID {book_id}",
            bg=PRIMARY_BG, fg=ACCENT, font=TITLE_FONT
        )
        header.pack(pady=10)

        # ------------------ DETAILS FRAME ------------------
        details = tk.Frame(win, bg=PRIMARY_BG)
        details.pack(fill="x", padx=20)

        # Title
        tk.Label(details, text="Title:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=0, column=0, sticky="e")
        title_entry = tk.Entry(details, width=40, font=LABEL_FONT)
        title_entry.grid(row=0, column=1, padx=5, pady=2)
        title_entry.insert(0, book["title"])

        # Author
        tk.Label(details, text="Author:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=1, column=0, sticky="e")
        author_entry = tk.Entry(details, width=40, font=LABEL_FONT)
        author_entry.grid(row=1, column=1, padx=5, pady=2)
        author_entry.insert(0, book["author"])

        # Buy Price
        tk.Label(details, text="Buy Price:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=2, column=0, sticky="e")
        buy_entry = tk.Entry(details, width=15, font=LABEL_FONT)
        buy_entry.grid(row=2, column=1, sticky="w")
        buy_entry.insert(0, str(book["price_buy"]))

        # Rent Price
        tk.Label(details, text="Rent Price:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=3, column=0, sticky="e")
        rent_entry = tk.Entry(details, width=15, font=LABEL_FONT)
        rent_entry.grid(row=3, column=1, sticky="w")
        rent_entry.insert(0, str(book["price_rent"]))

        # Genre
        tk.Label(details, text="Genre:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=4, column=0, sticky="e")
        genre_entry = tk.Entry(details, width=25, font=LABEL_FONT)
        genre_entry.grid(row=4, column=1, sticky="w")
        genre_entry.insert(0, book.get("genre") or "")

        # Year
        tk.Label(details, text="Publication Year:", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=5, column=0, sticky="e")
        year_entry = tk.Entry(details, width=10, font=LABEL_FONT)
        year_entry.grid(row=5, column=1, sticky="w")
        year_entry.insert(0, book.get("publication_year") or "")



        # ------------------ INVENTORY FRAME ------------------
        inv_frame = tk.Frame(win, bg=PRIMARY_BG)
        inv_frame.pack(fill="x", padx=20, pady=(10, 5))

        tk.Label(inv_frame, text="Inventory:", bg=PRIMARY_BG, fg=ACCENT, font=("Georgia", 14, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))

        tk.Label(inv_frame, text=f"Total Copies: {book['total_copies']}", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=1, column=0, sticky="w")
        tk.Label(inv_frame, text=f"Available Copies: {book['available_copies']}", bg=PRIMARY_BG, font=LABEL_FONT).grid(row=2, column=0, sticky="w")

        # Increase Inventory Button
        def inc_inventory():
            amount = simpledialog.askinteger("Increase Inventory", "Increase by:", minvalue=1, parent=win)
            if not amount:
                return
            _, err = api_manager_update_inventory(book_id, amount)
            if err:
                messagebox.showerror("Error", err)
                return
            messagebox.showinfo("Success", "Inventory updated.")
            win.destroy()
            self.load_books()

        inc_btn = tk.Button(
            inv_frame, text="Increase Inventory",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=inc_inventory
        )
        inc_btn.grid(row=3, column=0, sticky="w", pady=5)

        # ------------------ REVIEWS ------------------
        reviews_frame = tk.Frame(win, bg=PRIMARY_BG)
        reviews_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tk.Label(
            reviews_frame, text="Reviews",
            bg=PRIMARY_BG, fg=ACCENT, font=("Georgia", 16, "bold")
        ).pack(anchor="w")

        reviews_box = tk.Text(
            reviews_frame, height=12,
            bg=PRIMARY_BG, fg=TEXT_COLOR,
            font=("Courier New", 10)
        )
        reviews_box.pack(fill="both", expand=True)

        if not reviews:
            reviews_box.insert("1.0", "No reviews yet.")
        else:
            for r in reviews:
                reviews_box.insert("end", f"User: {r['username']}\n")
                reviews_box.insert("end", f"Rating: {r['rating']}/5\n")
                reviews_box.insert("end", f"Review: {r['review_text']}\n")
                reviews_box.insert("end", f"Date: {r['created_at']}\n")
                reviews_box.insert("end", "-" * 50 + "\n")

        # ------------------ SAVE CHANGES BUTTON ------------------
        def save_updates():
            try:
                pb = float(buy_entry.get())
                pr = float(rent_entry.get())
            except:
                messagebox.showerror("Invalid Price", "Buy/Rent prices must be numeric.")
                return

            ok, err = api_manager_update_book(
                book_id,
                title_entry.get().strip(),
                author_entry.get().strip(),
                pb,
                pr,
                genre_entry.get().strip(),
                year_entry.get().strip()
            )
            if err:
                messagebox.showerror("Error", err)
                return

            messagebox.showinfo("Success", "Book updated.")
            win.destroy()
            self.load_books()

        save_btn = tk.Button(
            win, text="Save Changes",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=save_updates
        )
        save_btn.pack(pady=5)

        # ------------------ CLOSE BUTTON ------------------
        close_btn = tk.Button(
            win, text="Close",
            bg=BUTTON_BG, fg=BUTTON_BLACK, font=LABEL_FONT,
            command=win.destroy
        )
        close_btn.pack(pady=(0, 10))
    # ========================================================
    # SECTION 5 — CUSTOMERS PAGE
    # ========================================================

    def _build_customers_view(self):
        """Search customers → sortable table → double click = profile popup."""

        # ------------------ HEADER ------------------
        header = tk.Frame(self.content, bg=PRIMARY_BG)
        header.pack(fill="x")

        tk.Label(
            header, text="Customer Management",
            bg=PRIMARY_BG, fg=ACCENT, font=TITLE_FONT
        ).pack(side="left")

        # ------------------ SEARCH BAR ------------------
        search_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        search_frame.pack(fill="x", pady=(10, 0))

        tk.Label(search_frame, text="Search Name/Email:", bg=PRIMARY_BG, font=LABEL_FONT).pack(side="left")
        self.customer_search_var = tk.Entry(search_frame, width=30, font=LABEL_FONT)
        self.customer_search_var.pack(side="left", padx=10)

        btn_search = tk.Button(
            search_frame, text="Search",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=self.load_customers
        )
        btn_search.pack(side="left", padx=10)

        # ------------------ TABLE ------------------
        table_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))

        columns = ("id", "username", "email", "created", "orders", "rentals")
        self.customers_tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=14
        )

        headers = {
            "id": "ID (hidden)",
            "username": "Username",
            "email": "Email",
            "created": "Joined",
            "orders": "Total Orders",
            "rentals": "Active Rentals"
        }

        for col in columns:
            label = "" if col == "id" else headers[col]
            self.customers_tree.heading(
                col, text=label,
                command=lambda c=col: self.sort_treeview(self.customers_tree, c, 0)
            )

        # Column widths
        self.customers_tree.column("id", width=0, stretch=False)
        self.customers_tree.column("username", width=160)
        self.customers_tree.column("email", width=220)
        self.customers_tree.column("created", width=150)
        self.customers_tree.column("orders", width=120, anchor="center")
        self.customers_tree.column("rentals", width=120, anchor="center")

        self.customers_tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(
            table_frame, orient="vertical",
            command=self.customers_tree.yview
        )
        self.customers_tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # Button frame at bottom
        btn_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        btn_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            btn_frame, text="View Selected Customer",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=self.open_customer_profile
        ).pack(side="left", padx=5)

        # Initial load
        self.load_customers()


    # ========================================================
    # Load customers
    # ========================================================

    def load_customers(self):
        query = self.customer_search_var.get().strip()

        users, error = api_manager_search_customers(query)
        if error:
            messagebox.showerror("Error", error)
            return

        # Count orders & rentals
        rows = []
        for u in users:
            orders, _ = api_manager_get_customer_orders(u["id"])
            rentals, _ = api_manager_get_customer_rentals(u["id"])

            active_rentals = [r for r in rentals if r["returned_at"] is None]

            rows.append({
                "id": u["id"],
                "username": u["username"],
                "email": u["email"],
                "created": u["created_at"],
                "orders": len(orders),
                "rentals": len(active_rentals)
            })

        self.customer_rows = rows
        self.customers_tree.delete(*self.customers_tree.get_children())

        for r in rows:
            self.customers_tree.insert(
                "", "end", iid=str(r["id"]),
                values=(
                    r["id"],
                    r["username"],
                    r["email"],
                    r["created"],
                    r["orders"],
                    r["rentals"]
                )
            )


    # ========================================================
    # View Selected Customer Profile
    # ========================================================

    def open_customer_profile(self, event=None):
        sel = self.customers_tree.selection()
        if not sel:
            messagebox.showwarning("Select Customer", "Please select a customer to view.")
            return

        customer_id = int(sel[0])
        user, error = api_manager_get_customer(customer_id)
        if error:
            messagebox.showerror("Error", error)
            return

        self._open_customer_modal(user)


    # ========================================================
    # CUSTOMER MODAL
    # ========================================================

    def _open_customer_modal(self, user):
        from datetime import datetime, timedelta
        cid = user["id"]

        win = tk.Toplevel(self)
        win.title(f"Customer: {user['username']}")
        win.configure(bg=PRIMARY_BG)
        win.geometry("850x650")
        win.transient(self)
        win.grab_set()

        # ------------------ HEADER ------------------
        tk.Label(
            win, text=f"Customer Profile — {user['username']}",
            bg=PRIMARY_BG, fg=ACCENT, font=TITLE_FONT
        ).pack(pady=10)

        # ------------------ INFO BOX ------------------
        info = tk.Frame(win, bg=PRIMARY_BG)
        info.pack(fill="x", padx=20)

        tk.Label(info, text=f"User ID: {cid}", bg=PRIMARY_BG, font=LABEL_FONT).pack(anchor="w")
        tk.Label(info, text=f"Email: {user['email']}", bg=PRIMARY_BG, font=LABEL_FONT).pack(anchor="w")
        tk.Label(info, text=f"Created: {user['created_at']}", bg=PRIMARY_BG, font=LABEL_FONT).pack(anchor="w")

        # =====================================================
        # ORDERS SECTION
        # =====================================================
        tk.Label(
            win, text="Orders", bg=PRIMARY_BG,
            fg=ACCENT, font=("Georgia", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(10, 0))

        orders_box = tk.Frame(win, bg=PRIMARY_BG)
        orders_box.pack(fill="both", expand=True, padx=20, pady=5)

        orders_tree = ttk.Treeview(
            orders_box,
            columns=("id", "total", "status", "date"),
            show="headings", height=8
        )
        # Make headings sortable using shared sort_treeview
        orders_tree.heading("id", text="Order ID", command=lambda c="id": self.sort_treeview(orders_tree, c, 0))
        orders_tree.heading("total", text="Total", command=lambda c="total": self.sort_treeview(orders_tree, c, 0))
        orders_tree.heading("status", text="Status", command=lambda c="status": self.sort_treeview(orders_tree, c, 0))
        orders_tree.heading("date", text="Date", command=lambda c="date": self.sort_treeview(orders_tree, c, 0))

        orders_tree.column("id", width=120, anchor="center")
        orders_tree.column("total", width=140, anchor="e")
        orders_tree.column("status", width=150, anchor="center")
        orders_tree.column("date", width=200)

        orders_tree.pack(side="left", fill="both", expand=True)
        scroll1 = ttk.Scrollbar(orders_box, orient="vertical", command=orders_tree.yview)
        orders_tree.configure(yscrollcommand=scroll1.set)
        scroll1.pack(side="right", fill="y")

        # When selecting in one table, deselect rows in the other tables
        def _deselect_other_trees(active_tree):
            # Prevent recursive selection events when programmatically changing selection
            if getattr(self, "_suppress_tree_select", False):
                return
            setattr(self, "_suppress_tree_select", True)
            try:
                for t in (orders_tree, rentals_tree):
                    if t is not active_tree:
                        sel = t.selection()
                        if sel:
                            try:
                                t.selection_remove(*sel)
                            except Exception:
                                # fallback to setting empty selection
                                try:
                                    t.selection_set(())
                                except Exception:
                                    pass
            finally:
                setattr(self, "_suppress_tree_select", False)

        orders_tree.bind("<<TreeviewSelect>>", lambda e: _deselect_other_trees(orders_tree))

        # Load orders
        orders, _ = api_manager_get_customer_orders(cid)
        for o in orders:
            orders_tree.insert(
                "", "end", iid=str(o["id"]),
                values=(
                    o["id"],
                    f"${o['total_price']:.2f}",
                    o["payment_status"],
                    o["created_at"]
                )
            )

        # Buttons for order status
        btn_order_frame = tk.Frame(win, bg=PRIMARY_BG)
        btn_order_frame.pack(fill="x", padx=20)

        def set_order_status(new_status):
            sel = orders_tree.selection()
            if not sel:
                messagebox.showwarning("Select Order", "Select an order first.")
                return

            oid = int(sel[0])
            _, err = api_manager_update_order_status(oid, new_status)
            if err:
                messagebox.showerror("Error", err)
                return

            messagebox.showinfo("Success", f"Order marked {new_status}.")
            win.destroy()
            self.load_customers()

        tk.Button(
            btn_order_frame, text="Mark Paid",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=lambda: set_order_status("Paid")
        ).pack(side="left", padx=5)

        tk.Button(
            btn_order_frame, text="Mark Pending",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=lambda: set_order_status("Pending")
        ).pack(side="left", padx=5)

        # =====================================================
        # RENTALS SECTION
        # =====================================================
        tk.Label(
            win, text="Rentals", bg=PRIMARY_BG,
            fg=ACCENT, font=("Georgia", 16, "bold")
        ).pack(anchor="w", padx=20, pady=(10, 0))

        rentals_box = tk.Frame(win, bg=PRIMARY_BG)
        rentals_box.pack(fill="both", expand=True, padx=20, pady=5)

        rentals_tree = ttk.Treeview(
            rentals_box,
            columns=("id", "book", "due", "rented", "returned"),
            show="headings", height=8
        )
        rentals_tree.heading("id", text="Rental ID", command=lambda c="id": self.sort_treeview(rentals_tree, c, 0))
        rentals_tree.heading("book", text="Book", command=lambda c="book": self.sort_treeview(rentals_tree, c, 0))
        rentals_tree.heading("due", text="Due Date", command=lambda c="due": self.sort_treeview(rentals_tree, c, 0))
        rentals_tree.heading("rented", text="Rented At", command=lambda c="rented": self.sort_treeview(rentals_tree, c, 0))
        rentals_tree.heading("returned", text="Returned At", command=lambda c="returned": self.sort_treeview(rentals_tree, c, 0))

        rentals_tree.column("id", width=100, anchor="center")
        rentals_tree.column("book", width=300)
        rentals_tree.column("due", width=140, anchor="center")
        rentals_tree.column("rented", width=160, anchor="center")
        rentals_tree.column("returned", width=160, anchor="center")

        rentals_tree.pack(side="left", fill="both", expand=True)
        scroll2 = ttk.Scrollbar(rentals_box, orient="vertical", command=rentals_tree.yview)
        rentals_tree.configure(yscrollcommand=scroll2.set)
        scroll2.pack(side="right", fill="y")

        rentals_tree.bind("<<TreeviewSelect>>", lambda e: _deselect_other_trees(rentals_tree))

        # Load rentals
        rentals, _ = api_manager_get_customer_rentals(cid)
        for r in rentals:
            rentals_tree.insert(
                "", "end", iid=str(r["id"]),
                values=(
                    r["id"],
                    r["title"],
                    r["due_date"],
                    r["rented_at"],
                    r["returned_at"] or ""
                )
            )

        # Buttons for rentals
        btn_rental_frame = tk.Frame(win, bg=PRIMARY_BG)
        btn_rental_frame.pack(fill="x", padx=20)

        # ---- Mark Returned ----
        def return_rental():
            sel = rentals_tree.selection()
            if not sel:
                messagebox.showwarning("Select Rental", "Select a rental first.")
                return

            rid = int(sel[0])
            _, err = api_manager_return_rental(rid)
            if err:
                messagebox.showerror("Error", err)
                return

            messagebox.showinfo("Success", "Rental marked as returned.")
            win.destroy()
            self.load_customers()

        tk.Button(
            btn_rental_frame, text="Mark Returned",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=return_rental
        ).pack(side="left", padx=5)

        # =====================================================
        # MANUAL RENTAL CREATION BUTTON (THE ONE YOU NEED)
        # =====================================================

        tk.Button(
            btn_rental_frame, text="Manual Rental",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=lambda: self._manual_rental_popup(cid, win)
        ).pack(side="left", padx=5)



    # ============================================================
    # HELPER POPUP FOR MANUAL RENTAL (kept separate for clarity)
    # ============================================================
    def _manual_rental_popup(self, cid, parent_win):
        from datetime import datetime, timedelta

        rent_win = tk.Toplevel(parent_win)
        rent_win.title("Manual Rental")
        rent_win.configure(bg=PRIMARY_BG)
        rent_win.geometry("360x260")
        rent_win.transient(self)
        rent_win.grab_set()

        tk.Label(
            rent_win, text="Select Book:",
            bg=PRIMARY_BG, font=LABEL_FONT
        ).pack(pady=10)

        # Load books
        all_books, _ = api_manager_list_books({"q": "", "genre": "", "year": ""})

        book_var = tk.StringVar()
        dropdown = ttk.Combobox(
            rent_win, state="readonly", width=40,
            textvariable=book_var,
            values=[f"{b['id']} — {b['title']}" for b in all_books]
        )
        dropdown.pack()

        tk.Label(
            rent_win, text="Due in:",
            bg=PRIMARY_BG, font=LABEL_FONT
        ).pack(pady=10)

        due_var = tk.StringVar()
        due_box = ttk.Combobox(
            rent_win, state="readonly",
            textvariable=due_var,
            width=12,
            values=["7 days", "14 days", "21 days"]
        )
        due_box.pack()

        def submit():
            if not dropdown.get() or not due_box.get():
                messagebox.showwarning("Missing Fields", "Select both fields.")
                return

            book_id = int(dropdown.get().split("—")[0].strip())
            days = int(due_box.get().split()[0])
            due_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

            _, err = api_manager_manual_rent(cid, book_id, due_date)
            if err:
                messagebox.showerror("Error", err)
                return

            messagebox.showinfo("Success", "Rental created.")
            rent_win.destroy()
            parent_win.destroy()
            self.load_customers()

        tk.Button(
            rent_win, text="Create",
            bg=ACCENT, fg=BUTTON_FG, font=LABEL_FONT,
            command=submit
        ).pack(pady=15)
