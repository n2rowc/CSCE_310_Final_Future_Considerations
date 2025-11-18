# frontend/customer_view.py
import tkinter as tk
from tkinter import ttk, messagebox

from api_client import api_search_books, api_place_order

PRIMARY_BG = "#f7f1e3"
NAV_BG = "#3b3a30"
NAV_FG = "#fdfaf3"
ACCENT = "#8b0000"
TEXT_COLOR = "#2b2b2b"

BUTTON_BG = "#d2b48c"   # tan, readable on all platforms
BUTTON_FG = "#8b0000"
BUTTON_Black =  "#000000"  # black text

TITLE_FONT = ("Georgia", 20, "bold")
LABEL_FONT = ("Georgia", 12)
NAV_FONT = ("Georgia", 12, "bold")


class CustomerFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=PRIMARY_BG)
        self.controller = controller
        self.user_info = controller.user_info

        self.cart = []      # list of dicts: {book_id, title, author, type, price}
        self.book_map = {}  # book_id -> book details

        self._build_layout()
        self.show_books_view()

    # ---------- Layout ----------
    def _build_layout(self):
        # Top navbar
        nav = tk.Frame(self, bg=NAV_BG, height=50)
        nav.pack(side="top", fill="x")

        title = tk.Label(
            nav,
            text=f"Customer: {self.user_info['username']}",
            bg=NAV_BG,
            fg=NAV_FG,
            font=TITLE_FONT,
        )
        title.pack(side="left", padx=20)

        btn_books = tk.Button(
            nav,
            text="Books",
            bg=NAV_BG,
            fg=BUTTON_Black,
            font=NAV_FONT,
            relief="flat",
            command=self.show_books_view,
        )
        btn_books.pack(side="left", padx=10)

        btn_cart = tk.Button(
            nav,
            text="Checkout Cart",
            bg=NAV_BG,
            fg=BUTTON_Black,
            font=NAV_FONT,
            relief="flat",
            command=self.show_cart_view,
        )
        btn_cart.pack(side="left", padx=10)

        btn_logout = tk.Button(
            nav,
            text="Logout",
            bg=NAV_BG,
            fg=BUTTON_Black,
            font=NAV_FONT,
            relief="flat",
            command=self.controller.logout,
        )
        btn_logout.pack(side="right", padx=20)

        # Content area
        self.content = tk.Frame(self, bg=PRIMARY_BG)
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    # ---------- Books view ----------
    def show_books_view(self):
        self._clear_content()

        # Search bar
        search_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            search_frame,
            text="Search by title or author:",
            font=LABEL_FONT,
            bg=PRIMARY_BG,
            fg=TEXT_COLOR,
        ).pack(side="left")

        self.search_var = tk.StringVar()
        entry = tk.Entry(search_frame, textvariable=self.search_var, width=40, font=LABEL_FONT)
        entry.pack(side="left", padx=10)
        entry.bind("<Return>", lambda e: self._perform_search())

        btn_search = tk.Button(
            search_frame,
            text="Search",
            font=LABEL_FONT,
            bg=ACCENT,
            fg=BUTTON_FG,
            command=self._perform_search,
        )
        btn_search.pack(side="left")

        # Results table
        table_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        table_frame.pack(fill="both", expand=True)

        columns = ("title", "author", "price_buy", "price_rent")
        self.book_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )
        self.book_tree.heading("title", text="Title")
        self.book_tree.heading("author", text="Author")
        self.book_tree.heading("price_buy", text="Buy Price")
        self.book_tree.heading("price_rent", text="Rent Price")

        self.book_tree.column("title", width=350)
        self.book_tree.column("author", width=200)
        self.book_tree.column("price_buy", width=80, anchor="e")
        self.book_tree.column("price_rent", width=80, anchor="e")

        self.book_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Add buttons
        btn_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        btn_frame.pack(fill="x", pady=(10, 0))

        btn_buy = tk.Button(
            btn_frame,
            text="Add Selected as Buy",
            font=LABEL_FONT,
            bg=ACCENT,
            fg=BUTTON_FG,
            command=lambda: self._add_selected_to_cart("buy"),
        )
        btn_buy.pack(side="left")

        btn_rent = tk.Button(
            btn_frame,
            text="Add Selected as Rent",
            font=LABEL_FONT,
            bg=ACCENT,
            fg=BUTTON_FG,
            command=lambda: self._add_selected_to_cart("rent"),
        )
        btn_rent.pack(side="left", padx=10)

        self._perform_search(initial=True)

    def _perform_search(self, initial=False):
        keyword = self.search_var.get() if hasattr(self, "search_var") else ""
        books, error = api_search_books(keyword)
        if error:
            if not initial:
                messagebox.showerror("Search error", error)
            return

        # Clear current items
        for row in self.book_tree.get_children():
            self.book_tree.delete(row)

        self.book_map = {}
        for b in books:
            bid = b["id"]
            self.book_map[bid] = b
            self.book_tree.insert(
                "",
                "end",
                iid=str(bid),
                values=(
                    b["title"],
                    b["author"],
                    f"${float(b['price_buy']):.2f}",
                    f"${float(b['price_rent']):.2f}",
                ),
            )

    def _add_selected_to_cart(self, purchase_type: str):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Please select a book first.")
            return

        book_id = int(sel[0])
        b = self.book_map.get(book_id)
        if not b:
            messagebox.showerror("Error", "Selected book not found.")
            return

        if purchase_type == "buy":
            price = float(b["price_buy"])
        else:
            price = float(b["price_rent"])

        self.cart.append({
            "book_id": book_id,
            "title": b["title"],
            "author": b["author"],
            "type": purchase_type,
            "price": price,
        })

        messagebox.showinfo(
            "Added to cart",
            f"{b['title']} ({purchase_type}) added to your cart.",
        )

    # ---------- Cart view ----------
    def show_cart_view(self):
        self._clear_content()

        title = tk.Label(
            self.content,
            text="Your Cart",
            font=TITLE_FONT,
            bg=PRIMARY_BG,
            fg=ACCENT,
        )
        title.pack(anchor="w", pady=(0, 10))

        if not self.cart:
            msg = tk.Label(
                self.content,
                text="Your cart is empty. Go to the Books tab to add items.",
                font=LABEL_FONT,
                bg=PRIMARY_BG,
                fg=TEXT_COLOR,
            )
            msg.pack(anchor="w")
            return

        # Table
        table_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        table_frame.pack(fill="both", expand=True)

        columns = ("title", "author", "type", "price")
        cart_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10,
        )
        for col, text in zip(columns, ["Title", "Author", "Type", "Price"]):
            cart_tree.heading(col, text=text)

        cart_tree.column("title", width=350)
        cart_tree.column("author", width=200)
        cart_tree.column("type", width=80, anchor="center")
        cart_tree.column("price", width=80, anchor="e")

        for item in self.cart:
            cart_tree.insert(
                "",
                "end",
                values=(
                    item["title"],
                    item["author"],
                    item["type"],
                    f"${item['price']:.2f}",
                ),
            )

        cart_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=cart_tree.yview)
        cart_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Summary + order button
        bottom = tk.Frame(self.content, bg=PRIMARY_BG)
        bottom.pack(fill="x", pady=(10, 0))

        total = sum(i["price"] for i in self.cart)
        total_label = tk.Label(
            bottom,
            text=f"Total: ${total:.2f}",
            font=("Georgia", 14, "bold"),
            bg=PRIMARY_BG,
            fg=TEXT_COLOR,
        )
        total_label.pack(side="left")

        place_btn = tk.Button(
            bottom,
            text="Place Order",
            font=LABEL_FONT,
            bg=ACCENT,
            fg=BUTTON_FG,
            command=self._place_order,
        )
        place_btn.pack(side="right")

    def _place_order(self):
        if not self.cart:
            messagebox.showwarning("Empty cart", "There is nothing to order.")
            return

        confirm = messagebox.askyesno(
            "Confirm Order",
            "Place order and generate bill?",
        )
        if not confirm:
            return

        payload_items = [{"book_id": c["book_id"], "type": c["type"]} for c in self.cart]
        bill, error = api_place_order(self.user_info["user_id"], payload_items)

        if error:
            messagebox.showerror("Order error", error)
            return

        # Show bill in a popup
        self._show_bill_window(bill)
        # Clear cart and refresh
        self.cart = []
        self.show_cart_view()

    def _show_bill_window(self, bill):
        win = tk.Toplevel(self)
        win.title(f"Order #{bill['order_id']} Bill")
        win.geometry("500x400")
        win.configure(bg=PRIMARY_BG)

        text = tk.Text(win, bg=PRIMARY_BG, fg=TEXT_COLOR, font=("Courier New", 11))
        text.pack(fill="both", expand=True, padx=10, pady=10)

        lines = []
        lines.append(f"Order ID: {bill['order_id']}")
        lines.append(f"Customer ID: {bill['user_id']}")
        lines.append(f"Payment Status: {bill['payment_status']}")
        lines.append("")
        lines.append("Items:")
        lines.append("-" * 60)

        for item in bill["items"]:
            lines.append(
                f"{item['title']} ({item['type']}) - ${item['price']:.2f}"
            )

        lines.append("-" * 60)
        lines.append(f"TOTAL: ${bill['total_price']:.2f}")

        text.insert("1.0", "\n".join(lines))
        text.config(state="disabled")
