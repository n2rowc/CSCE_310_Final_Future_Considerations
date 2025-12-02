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
    api_submit_review
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
        self.sort_state = {} # sorting memory for books

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
                "price_buy", "price_rent")
        headers = {
            "title": "Title",
            "author": "Author",
            "genre": "Genre",
            "publication_year": "Year",
            "price_buy": "Buy",
            "price_rent": "Rent"
        }

        self.tree = ttk.Treeview(tf, columns=cols, show="headings", height=16)

        # Hidden column for ID
        self.tree.heading("id_hidden", text="")
        self.tree.column("id_hidden", width=0, stretch=False)

        for col in cols[1:]:
            self.sort_state[col] = None
            self.tree.heading(col, text=headers[col], command=lambda c=col: self._sort_col(c))
            self.tree.column(col, width=140, anchor="w")

        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(tf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self._open_book_popup_from_selection)
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
                    f"${float(b['price_rent']):.2f}"
                )
            )

    # ============================================================
    # SORTING
    # ============================================================

    def _sort_col(self, col):
        curr = self.sort_state[col]
        new_direction = "asc" if curr in (None, "desc") else "desc"
        self.sort_state[col] = new_direction
        reverse = (new_direction == "desc")

        items = []
        for iid in self.tree.get_children():
            val = self.tree.set(iid, col)
            try:
                if col in ("price_buy", "price_rent"):
                    val = float(val.replace("$", ""))
                elif col == "publication_year":
                    val = int(val) if val else 0
                else:
                    val = val.lower()
            except:
                pass
            items.append((val, iid))

        items.sort(reverse=reverse)
        for idx, (_, iid) in enumerate(items):
            self.tree.move(iid, "", idx)

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

        # Checkout
        bottom = tk.Frame(self.content, bg=PRIMARY_BG)
        bottom.pack(fill="x", pady=12)

        total = sum(i["price"] for i in self.cart)
        tk.Label(bottom,
                 text=f"Total: ${total:.2f}",
                 font=("Georgia", 14, "bold"),
                 bg=PRIMARY_BG,
                 fg=TEXT_COLOR).pack(side="left")

        tk.Button(
            bottom,
            text="Place Order",
            bg=ACCENT,
            fg=BUTTON_FG,
            font=LABEL_FONT,
            command=self._place_order
        ).pack(side="right")

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

        tk.Label(self.content,
                 text="History",
                 font=TITLE_FONT,
                 bg=PRIMARY_BG,
                 fg=ACCENT).pack(anchor="w", pady=10)

        data, err = api_get_history(self.user_info["user_id"])
        if err:
            messagebox.showerror("Error", err)
            return

        self._history_block("Purchases", data["purchases"])
        self._history_block("Current Rentals", data["current_rentals"])
        self._history_block("Past Rentals", data["past_rentals"])
        self._history_block("Your Reviews", data["reviews"])

    def _history_block(self, title, rows):
        tk.Label(self.content,
                 text=title,
                 font=("Georgia", 16, "bold"),
                 bg=PRIMARY_BG,
                 fg=TEXT_COLOR).pack(anchor="w", pady=(15, 5))

        if not rows:
            tk.Label(self.content, text="None",
                     font=LABEL_FONT, bg=PRIMARY_BG, fg=TEXT_COLOR).pack(anchor="w")
            return

        frame = tk.Frame(self.content, bg=PRIMARY_BG)
        frame.pack(fill="x")

        # Option 2: Cleaned, readable columns
        clean_cols = ["book_id", "title", "author"] + [
            c for c in rows[0].keys()
            if c not in ("book_id", "title", "author")
        ]

        tree = ttk.Treeview(frame, columns=clean_cols, show="headings", height=5)

        # Hide book_id column
        tree.column("book_id", width=0, stretch=False)
        tree.heading("book_id", text="")

        for c in clean_cols[1:]:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=160)

        for r in rows:
            tree.insert("", "end", values=[r.get(c, "") for c in clean_cols])

        tree.pack(side="left", fill="x", expand=True)
        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        tree.bind("<Double-1>", lambda e, t=tree: self._open_book_popup_from_history(t))

    # ============================================================
    # POPUP LOGIC (UNIFIED)
    # ============================================================

    def _open_book_popup_from_selection(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        row = self.tree.item(sel[0], "values")
        book_id = int(row[0])  # first column is always id_hidden
        self._open_book_popup(book_id)

    def _open_book_popup_from_history(self, tree):
        sel = tree.selection()
        if not sel:
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
        win.geometry("450x550")
        win.configure(bg=PRIMARY_BG)

        # Info block
        info = [
            f"Title: {data['title']}",
            f"Author: {data['author']}",
            f"Genre: {data.get('genre', '')}",
            f"Year: {data.get('publication_year', '')}",
            f"Buy: ${float(data['price_buy']):.2f}" if data.get("price_buy") else "Buy: N/A",
            f"Rent: ${float(data['price_rent']):.2f}" if data.get("price_rent") else "Rent: N/A",
            "",
            (
                f"Average Rating: {data['avg_rating']:.2f} ({data['review_count']} reviews)"
                if data.get("avg_rating") else "No ratings yet."
            )
        ]

        tk.Label(
            win,
            text="\n".join(info),
            bg=PRIMARY_BG,
            fg=TEXT_COLOR,
            justify="left",
            font=LABEL_FONT
        ).pack(anchor="w", padx=10, pady=10)

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

        rating_var = tk.StringVar(
            value=str(data["user_review"]["rating"]) if data.get("user_review") else "5"
        )

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

        if data.get("user_review"):
            review_box.insert("1.0", data["user_review"]["review_text"])

        def submit_review():
            rating = int(rating_var.get())
            text = review_box.get("1.0", "end").strip()

            _, err2 = api_submit_review(
                self.user_info["user_id"], data["id"], rating, text
            )
            if err2:
                messagebox.showerror("Error", err2)
            else:
                messagebox.showinfo("Success", "Review submitted!")
                win.destroy()

        tk.Button(
            win,
            text="Submit Review",
            bg=ACCENT,
            fg=BUTTON_FG,
            font=LABEL_FONT,
            command=submit_review
        ).pack(pady=10)

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
