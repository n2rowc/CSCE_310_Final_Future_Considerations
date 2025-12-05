# ============================================================
# Customer UI (Improved, Cleanup, Bug-Proofed)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox
from api_client import (
    api_search_books,
    api_place_order,
    api_get_history,
    api_get_book_details,
    api_submit_review,
    api_get_book_reviews
)

# ---------------- COLORS (UNCHANGED) ----------------
PRIMARY_BG = "#f7f1e3"
NAV_BG = "#3b3a30"
NAV_FG = "#fdfaf3"
ACCENT = "#8b0000"
TEXT_COLOR = "#2b2b2b"

BUTTON_BG = "#d2b48c"
BUTTON_FG = "#8b0000"
BUTTON_Black = "#000000"

TITLE_FONT = ("Georgia", 20, "bold")
LABEL_FONT = ("Georgia", 12)
NAV_FONT = ("Georgia", 12, "bold")


# ============================================================
# MAIN FRAME
# ============================================================

class CustomerFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=PRIMARY_BG)
        self.controller = controller
        self.user_info = controller.user_info

        self.cart = []       # items user selected
        self.book_map = {}   # id → book row
        self.sort_states = {}  # sorting memory for books (matches manager style)
        
        # Configure treeview style once during init
        style = ttk.Style()
        style.configure("Treeview", rowheight=25)
        style.configure("Treeview.Heading", font=("Georgia", 11, "bold"), padding=10)

        self._build_ui()
        self.show_books_view()

    # ============================================================
    # NAV + LAYOUT
    # ============================================================

    def _build_ui(self):
        nav = tk.Frame(self, bg=NAV_BG, height=50)
        nav.pack(side="top", fill="x")

        tk.Label(
            nav,
            text=f"Customer: {self.user_info['username']}",
            font=TITLE_FONT,
            bg=NAV_BG,
            fg=NAV_FG
        ).pack(side="left", padx=20)

        for name, func in [
            ("Books", self.show_books_view),
            ("Checkout Cart", self.show_cart_view),
            ("History", self.show_history_view)
        ]:
            tk.Button(
                nav,
                text=name,
                font=NAV_FONT,
                bg=NAV_BG,
                fg=BUTTON_Black,
                relief="flat",
                command=func
            ).pack(side="left", padx=10)

        tk.Button(
            nav,
            text="Logout",
            font=NAV_FONT,
            bg=NAV_BG,
            fg=BUTTON_Black,
            relief="flat",
            command=self.controller.logout
        ).pack(side="right", padx=20)

        self.content = tk.Frame(self, bg=PRIMARY_BG)
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

    def _clear(self):
        for child in self.content.winfo_children():
            child.destroy()

    # ============================================================
    # BOOKS VIEW
    # ============================================================

    def show_books_view(self):
        self._clear()

        # ---------------- SEARCH BAR ----------------
        sf = tk.Frame(self.content, bg=PRIMARY_BG)
        sf.pack(fill="x", pady=(0, 10))

        self.q_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.year_var = tk.StringVar()

        tk.Label(sf, text="Keyword:", bg=PRIMARY_BG, fg=TEXT_COLOR,
                 font=LABEL_FONT).grid(row=0, column=0, sticky="w")
        tk.Entry(sf, textvariable=self.q_var, width=18).grid(row=0, column=1, padx=5)

        tk.Label(sf, text="Genre:", bg=PRIMARY_BG, fg=TEXT_COLOR,
                 font=LABEL_FONT).grid(row=0, column=2, sticky="w")
        tk.Entry(sf, textvariable=self.genre_var, width=15).grid(row=0, column=3, padx=5)

        tk.Label(sf, text="Year:", bg=PRIMARY_BG, fg=TEXT_COLOR,
                 font=LABEL_FONT).grid(row=0, column=4, sticky="w")
        tk.Entry(sf, textvariable=self.year_var, width=10).grid(row=0, column=5, padx=5)

        tk.Button(
            sf,
            text="Search",
            bg=ACCENT,
            fg=BUTTON_FG,
            font=LABEL_FONT,
            command=self._search
        ).grid(row=0, column=6, padx=12)

        # ---------------- TABLE ----------------
        tf = tk.Frame(self.content, bg=PRIMARY_BG)
        tf.pack(fill="both", expand=True)

        cols = ("id_hidden", "title", "author", "genre", "publication_year",
                "price_buy", "price_rent", "available_copies")
        headers = {
            "title": "Title",
            "author": "Author",
            "genre": "Genre",
            "publication_year": "Year",
            "price_buy": "Buy",
            "price_rent": "Rent",
            "available_copies": "Available"
        }

        self.tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)

        # Hidden column for ID
        self.tree.heading("id_hidden", text="")
        self.tree.column("id_hidden", width=0, stretch=False)

        for col in cols[1:]:
            self.tree.heading(col, text=headers[col], command=lambda c=col: self._sort_col(c))
            self.tree.column(col, width=140, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # Give tree focus when view is shown
        self.tree.focus_set()
        
        self._search()

        # ---------------- ADD TO CART ----------------
        btns = tk.Frame(self.content, bg=PRIMARY_BG)
        btns.pack(fill="x", pady=(12, 0))

        tk.Button(
            btns,
            text="Add Selected as Buy",
            font=LABEL_FONT,
            bg=ACCENT,
            fg=BUTTON_FG,
            command=lambda: self.add_to_cart("buy")
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btns,
            text="Add Selected as Rent",
            font=LABEL_FONT,
            bg=ACCENT,
            fg=BUTTON_FG,
            command=lambda: self.add_to_cart("rent")
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            btns,
            text="View Info/Review",
            font=LABEL_FONT,
            bg=ACCENT,
            fg=BUTTON_FG,
            command=self._view_book_info
        ).pack(side="left")

    # ============================================================
    # SEARCH HANDLER
    # ============================================================

    def _search(self):
        params = {
            "q": self.q_var.get(),
            "genre": self.genre_var.get(),
            "year": self.year_var.get()
        }

        books, err = api_search_books(params)
        if err:
            messagebox.showerror("Search Error", err)
            return

        for r in self.tree.get_children():
            self.tree.delete(r)

        self.book_map = {}

        for b in books:
            bid = b["id"]
            self.book_map[bid] = b

            self.tree.insert(
                "",
                "end",
                values=(
                    bid,
                    b["title"],
                    b["author"],
                    b.get("genre") or "",
                    b.get("publication_year") or "",
                    f"${float(b['price_buy']):.2f}",
                    f"${float(b['price_rent']):.2f}",
                    b.get("available_copies", "N/A")
                )
            )

    # ============================================================
    # SORTING
    # ============================================================

    def _sort_col(self, col):
        """Sort a treeview column in asc/desc order with arrow indicator."""
        # Extract rows
        rows = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        # Convert values for numeric columns
        def convert(v):
            if v is None:
                return ""
            
            # Handle price columns (strip $ and convert to float)
            if col in ("price_buy", "price_rent"):
                try:
                    return float(str(v).replace("$", ""))
                except:
                    return 0
            
            # Handle year as numeric
            if col == "publication_year":
                try:
                    return float(v) if v else 0
                except:
                    return 0
            
            # Everything else as lowercase string
            if isinstance(v, str):
                return v.lower()
            
            return str(v).lower()

        rows = [(convert(v), k) for (v, k) in rows]

        # Determine direction (matches manager's logic)
        prev = self.sort_states.get(col, "none")
        direction = "asc" if prev != "asc" else "desc"
        self.sort_states[col] = direction

        reverse = (direction == "desc")
        rows.sort(reverse=reverse, key=lambda x: x[0])

        # Reinsert sorted rows
        for index, (_, k) in enumerate(rows):
            self.tree.move(k, "", index)

        # Update column headers with arrows (matches manager's style)
        headers = {
            "title": "Title",
            "author": "Author",
            "genre": "Genre",
            "publication_year": "Year",
            "price_buy": "Buy",
            "price_rent": "Rent"
        }
        
        for c in self.tree["columns"]:
            label = headers.get(c, c.replace("_", " ").title())
            
            # Add arrow only to sorted column
            if c == col:
                arrow = " ↑" if direction == "asc" else " ↓"
                label = label + arrow
            
            self.tree.heading(c, text=label, command=lambda x=c: self._sort_col(x))

    def _view_book_info(self):
        """Open book info popup for selected book"""
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select Book", "Please select a book.")
            return
        
        row = self.tree.item(sel[0], "values")
        book_id = int(row[0])  # hidden ID column
        self._open_book_popup(book_id)

    # ============================================================
    # CART VIEW
    # ============================================================

    def show_cart_view(self):
        self._clear()

        tk.Label(self.content,
                 text="Your Cart",
                 font=TITLE_FONT,
                 bg=PRIMARY_BG,
                 fg=ACCENT).pack(anchor="w", pady=(0, 10))

        if not self.cart:
            tk.Label(self.content,
                     text="Your cart is empty.",
                     font=LABEL_FONT,
                     bg=PRIMARY_BG,
                     fg=TEXT_COLOR).pack(anchor="w")
            return

        tf = tk.Frame(self.content, bg=PRIMARY_BG)
        tf.pack(fill="both", expand=True)

        cols = ("title", "author", "type", "price")
        tree = ttk.Treeview(tf, columns=cols, show="headings", height=10)

        for c in cols:
            tree.heading(c, text=c.title())
            tree.column(c, width=160)

        for it in self.cart:
            tree.insert("", "end", values=(
                it["title"],
                it["author"],
                it["type"],
                f"${it['price']:.2f}"
            ))

        tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(tf, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # Store reference to tree for cart item removal
        self.cart_tree = tree

        # Checkout
        bottom = tk.Frame(self.content, bg=PRIMARY_BG)
        bottom.pack(fill="x", pady=12)

        total = sum(i["price"] for i in self.cart)
        tk.Label(bottom,
                 text=f"Total: ${total:.2f}",
                 font=("Georgia", 14, "bold"),
                 bg=PRIMARY_BG,
                 fg=TEXT_COLOR).pack(side="left")

        # Button frame for cart actions
        button_frame = tk.Frame(bottom, bg=PRIMARY_BG)
        button_frame.pack(side="right", padx=5)

        tk.Button(
            button_frame,
            text="Remove from Cart",
            bg="#E74C3C",
            fg=BUTTON_FG,
            font=LABEL_FONT,
            command=self._remove_from_cart
        ).pack(side="left", padx=2)

        tk.Button(
            button_frame,
            text="Clear Cart",
            bg="#E67E22",
            fg=BUTTON_FG,
            font=LABEL_FONT,
            command=self._clear_cart
        ).pack(side="left", padx=2)

        tk.Button(
            button_frame,
            text="Place Order",
            bg=ACCENT,
            fg=BUTTON_FG,
            font=LABEL_FONT,
            command=self._place_order
        ).pack(side="left", padx=2)

    def _remove_from_cart(self):
        if not hasattr(self, 'cart_tree'):
            messagebox.showwarning("Warning", "No cart tree found")
            return

        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return

        # Get the index of selected item (0-based)
        item_id = selection[0]
        item_index = self.cart_tree.index(item_id)

        # Remove from cart list
        if 0 <= item_index < len(self.cart):
            self.cart.pop(item_index)
            self.show_cart_view()

    def _clear_cart(self):
        if not self.cart:
            messagebox.showinfo("Info", "Cart is already empty")
            return

        if messagebox.askyesno("Clear Cart", "Are you sure you want to clear your cart?"):
            self.cart = []
            self.show_cart_view()

    def _place_order(self):
        payload = [{"book_id": it["book_id"], "type": it["type"]} for it in self.cart]

        bill, err = api_place_order(self.user_info["user_id"], payload)
        if err:
            messagebox.showerror("Order Error", err)
            return

        self.cart = []
        self._show_bill(bill)
        self.show_cart_view()

    def _show_bill(self, bill):
        win = tk.Toplevel(self)
        win.title(f"Order #{bill['order_id']}")
        win.geometry("500x400")
        win.configure(bg=PRIMARY_BG)

        text = tk.Text(win, bg=PRIMARY_BG, fg=TEXT_COLOR, font=("Courier", 12))
        text.pack(fill="both", expand=True)

        lines = [
            f"Order ID: {bill['order_id']}",
            f"Customer ID: {bill['user_id']}",
            f"Payment Status: {bill['payment_status']}",
            "",
            "Items:",
            "-" * 50
        ]

        for it in bill["items"]:
            lines.append(f"{it['title']} ({it['type']}) - ${it['price']:.2f}")

        lines.append("-" * 50)
        lines.append(f"TOTAL: ${bill['total_price']:.2f}")

        text.insert("1.0", "\n".join(lines))
        text.configure(state="disabled")

    # ============================================================
    # HISTORY VIEW
    # ============================================================

    def show_history_view(self):
        self._clear()
        self.history_trees = []  # Track all history trees to deselect them
        self.history_sort_states = {}  # Track sort states for each tree

        # Create a scrollable frame for the entire history view
        canvas = tk.Canvas(self.content, bg=PRIMARY_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=PRIMARY_BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add title
        tk.Label(
            scrollable_frame,
            text="History",
            font=TITLE_FONT,
            bg=PRIMARY_BG,
            fg=ACCENT
        ).pack(anchor="w", pady=10, padx=10)

        data, err = api_get_history(self.user_info["user_id"])
        if err:
            messagebox.showerror("Error", err)
            return

        self._history_block("Purchases", data["purchases"], scrollable_frame)
        self._history_block("Current Rentals", data["current_rentals"], scrollable_frame)
        self._history_block("Past Rentals", data["past_rentals"], scrollable_frame)
        self._history_block("Your Reviews", data["reviews"], scrollable_frame)

    def _history_block(self, title, rows, parent_frame):
        tk.Label(
            parent_frame,
            text=title,
            font=("Georgia", 16, "bold"),
            bg=PRIMARY_BG,
            fg=TEXT_COLOR
        ).pack(anchor="w", pady=(15, 5), padx=10)

        if not rows:
            tk.Label(
                parent_frame,
                text="None",
                font=LABEL_FONT,
                bg=PRIMARY_BG,
                fg=TEXT_COLOR
            ).pack(anchor="w", padx=10)
            return

        frame = tk.Frame(parent_frame, bg=PRIMARY_BG)
        frame.pack(fill="x", pady=(0, 10), padx=10)

        # Cleaned, readable columns
        clean_cols = ["book_id", "title", "author"] + [
            c for c in rows[0].keys()
            if c not in ("book_id", "title", "author")
        ]

        tree = ttk.Treeview(frame, columns=clean_cols, show="headings", height=5)

        # Hide book_id column
        tree.column("book_id", width=0, stretch=False)
        tree.heading("book_id", text="")

        for c in clean_cols[1:]:
            tree.heading(
                c,
                text=c.replace("_", " ").title(),
                command=lambda col=c, t=tree: self._sort_history_col(t, col, title)
            )
            tree.column(c, width=160)

        for r in rows:
            tree.insert("", "end", values=[r.get(c, "") for c in clean_cols])

        tree.pack(side="left", fill="x", expand=True)
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # Bind click to deselect other trees
        tree.bind("<Button-1>", lambda e: self._deselect_other_history_trees(tree))
        
        # Track this tree
        self.history_trees.append(tree)
        self.history_sort_states[id(tree)] = {}  # Track sort state per tree

        # Add button frame for history actions
        btn_frame = tk.Frame(parent_frame, bg=PRIMARY_BG)
        btn_frame.pack(fill="x", pady=(0, 5), padx=10)

        # Only show "Leave a Review" button for Purchases and Current Rentals sections
        if title in ("Purchases", "Current Rentals"):
            tk.Button(
                btn_frame,
                text="Leave a Review",
                font=LABEL_FONT,
                bg=ACCENT,
                fg=BUTTON_FG,
                command=lambda t=tree: self._leave_review_from_history(t)
            ).pack(side="left", padx=(0, 5))

    # ============================================================
    # POPUP LOGIC (UNIFIED)
    # ============================================================

    def _sort_history_col(self, tree, col, table_title):
        """Sort history table column with arrow indicator."""
        tree_id = id(tree)
        
        # Extract rows
        rows = [(tree.set(k, col), k) for k in tree.get_children("")]

        # Convert values for sorting
        def convert(v):
            if v is None:
                return ""
            
            # Handle numeric values
            try:
                return float(str(v).replace("$", ""))
            except:
                # String comparison
                if isinstance(v, str):
                    return v.lower()
                return str(v).lower()

        rows = [(convert(v), k) for (v, k) in rows]

        # Determine direction
        prev = self.history_sort_states[tree_id].get(col, "none")
        direction = "asc" if prev != "asc" else "desc"
        self.history_sort_states[tree_id][col] = direction

        reverse = (direction == "desc")
        rows.sort(reverse=reverse, key=lambda x: x[0])

        # Reinsert sorted rows
        for index, (_, k) in enumerate(rows):
            tree.move(k, "", index)

        # Update column headers with arrows
        for c in tree["columns"]:
            label = c.replace("_", " ").title() if c != "book_id" else ""
            
            # Add arrow only to sorted column
            if c == col and c != "book_id":
                arrow = " ↑" if direction == "asc" else " ↓"
                label = label + arrow
            
            tree.heading(c, text=label, command=lambda x=c, t=tree: self._sort_history_col(t, x, table_title))

    def _deselect_other_history_trees(self, current_tree):
        """Deselect all other history trees when clicking on one"""
        for tree in self.history_trees:
            if tree != current_tree:
                tree.selection_remove(tree.selection())

    def _leave_review_from_history(self, tree):
        """Open book popup for selected item in history to leave a review"""
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Select Item", "Please select a book to review.")
            return
        row = tree.item(sel[0], "values")
        book_id = int(row[0])  # hidden column
        self._open_book_popup(book_id)

    def _open_book_popup(self, book_id):
        data, err = api_get_book_details(book_id, self.user_info["user_id"])
        if err:
            messagebox.showerror("Error", err)
            return

        win = tk.Toplevel(self)
        win.title(data["title"])
        win.geometry("500x700")
        win.configure(bg=PRIMARY_BG)

        # Store book_id for refresh functions
        book_id = data["id"]
        book_title = data["title"]
        book_author = data["author"]
        book_genre = data.get('genre', '')
        book_year = data.get('publication_year', '')
        book_price_buy = data.get("price_buy")
        book_price_rent = data.get("price_rent")

        # Info block frame (will be updated)
        info_frame = tk.Frame(win, bg=PRIMARY_BG)
        info_frame.pack(anchor="w", padx=10, pady=10, fill="x")
        
        info_label = tk.Label(
            info_frame,
            text="",
            bg=PRIMARY_BG,
            fg=TEXT_COLOR,
            justify="left",
            font=LABEL_FONT
        )
        info_label.pack(anchor="w")

        def update_info_block(book_data):
            """Update the info block with fresh data"""
            info = [
                f"Title: {book_data['title']}",
                f"Author: {book_data['author']}",
                f"Genre: {book_data.get('genre', '')}",
                f"Year: {book_data.get('publication_year', '')}",
                f"Buy: ${float(book_data['price_buy']):.2f}" if book_data.get("price_buy") else "Buy: N/A",
                f"Rent: ${float(book_data['price_rent']):.2f}" if book_data.get("price_rent") else "Rent: N/A",
                "",
                (
                    f"Average Rating: {book_data['avg_rating']:.1f} ({book_data['review_count']} reviews)"
                    if book_data.get("avg_rating") is not None else f"Average Rating: N/A ({book_data.get('review_count', 0)} reviews)"
                )
            ]
            info_label.config(text="\n".join(info))

        # Initial info display
        update_info_block(data)

        # Review section
        tk.Label(
            win,
            text="Leave a Review:",
            font=("Georgia", 14, "bold"),
            bg=PRIMARY_BG,
            fg=ACCENT
        ).pack(anchor="w", padx=10, pady=(10, 0))

        rf = tk.Frame(win, bg=PRIMARY_BG)
        rf.pack(fill="x", padx=10)

        tk.Label(rf, text="Rating (1–5):", font=LABEL_FONT,
                 bg=PRIMARY_BG).grid(row=0, column=0)

        # Rating defaults to 5, but don't autofill review text
        rating_var = tk.StringVar(value="5")

        ttk.Combobox(
            rf,
            values=["1", "2", "3", "4", "5"],
            textvariable=rating_var,
            width=5
        ).grid(row=0, column=1, padx=4)

        tk.Label(rf, text="Review:", font=LABEL_FONT,
                 bg=PRIMARY_BG).grid(row=1, column=0, pady=5)

        review_box = tk.Text(rf, width=35, height=5)
        review_box.grid(row=2, column=0, columnspan=2)
        # Keep review box blank - don't autofill previous review

        def submit_review():
            rating = int(rating_var.get())
            text = review_box.get("1.0", "end").strip()

            _, err2 = api_submit_review(
                self.user_info["user_id"], book_id, rating, text
            )
            if err2:
                messagebox.showerror("Error", err2)
            else:
                messagebox.showinfo("Success", "Review submitted!")
                # Clear the review text box
                review_box.delete("1.0", "end")
                # Refresh book details to get updated average rating
                refresh_book_data()
                # Refresh the reviews section
                load_reviews()

        def refresh_book_data():
            """Refresh book data to get updated average rating"""
            fresh_data, err = api_get_book_details(book_id, self.user_info["user_id"])
            if not err and fresh_data:
                update_info_block(fresh_data)

        tk.Button(
            win,
            text="Submit Review",
            bg=ACCENT,
            fg=BUTTON_FG,
            font=LABEL_FONT,
            command=submit_review
        ).pack(pady=10)

        # Reviews History Section
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
        reviews_canvas = tk.Canvas(reviews_section, bg=PRIMARY_BG, highlightthickness=0, height=200)
        reviews_scrollbar = ttk.Scrollbar(reviews_section, orient="vertical", command=reviews_canvas.yview)
        reviews_scrollable = tk.Frame(reviews_canvas, bg=PRIMARY_BG)

        reviews_scrollable.bind(
            "<Configure>",
            lambda e: reviews_canvas.configure(scrollregion=reviews_canvas.bbox("all"))
        )

        reviews_canvas.create_window((0, 0), window=reviews_scrollable, anchor="nw")
        reviews_canvas.configure(yscrollcommand=reviews_scrollbar.set)

        def load_reviews():
            # Clear existing reviews
            for widget in reviews_scrollable.winfo_children():
                widget.destroy()

            # Fetch all reviews
            all_reviews, err = api_get_book_reviews(book_id)
            if err:
                tk.Label(
                    reviews_scrollable,
                    text=f"Error loading reviews: {err}",
                    bg=PRIMARY_BG,
                    fg=TEXT_COLOR,
                    font=LABEL_FONT
                ).pack(anchor="w", padx=5, pady=5)
                return

            if not all_reviews:
                tk.Label(
                    reviews_scrollable,
                    text="No reviews yet. Be the first to review!",
                    bg=PRIMARY_BG,
                    fg=TEXT_COLOR,
                    font=("Georgia", 11, "italic")
                ).pack(anchor="w", padx=5, pady=5)
            else:
                for review in all_reviews:
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

            # Update scroll region
            reviews_canvas.update_idletasks()
            reviews_canvas.configure(scrollregion=reviews_canvas.bbox("all"))

        reviews_canvas.pack(side="left", fill="both", expand=True)
        reviews_scrollbar.pack(side="right", fill="y")

        # Load reviews initially
        load_reviews()

    # ============================================================
    # ADD TO CART
    # ============================================================

    def add_to_cart(self, type_):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select Book", "Please select a book.")
            return

        row = self.tree.item(sel[0], "values")
        bid = int(row[0])  # hidden ID column
        b = self.book_map.get(bid)
        if not b:
            messagebox.showerror("Error", "Invalid book selection.")
            return

        price = float(b["price_buy"] if type_ == "buy" else b["price_rent"])

        self.cart.append({
            "book_id": bid,
            "title": b["title"],
            "author": b["author"],
            "type": type_,
            "price": price
        })

        messagebox.showinfo("Added", f"{b['title']} ({type_}) added to cart.")
