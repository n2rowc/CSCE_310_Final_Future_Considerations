# frontend/manager_view.py
import tkinter as tk
from tkinter import ttk, messagebox

from api_client import (
    api_search_books,
    api_manager_get_orders,
    api_manager_update_order_status,
    api_manager_add_book,
    api_manager_update_book,
)

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


class ManagerFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=PRIMARY_BG)
        self.controller = controller
        self.user_info = controller.user_info

        self.books = []
        self.book_map = {}
        self.orders = []

        self._build_layout()
        self.show_orders_view()

    # ---------- Layout ----------
    def _build_layout(self):
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

        btn_orders = tk.Button(
            nav,
            text="Orders",
            bg=NAV_BG,
            fg=BUTTON_Black,
            font=NAV_FONT,
            relief="flat",
            command=self.show_orders_view,
        )
        btn_orders.pack(side="left", padx=10)

        btn_books = tk.Button(
            nav,
            text="Manage Books",
            bg=NAV_BG,
            fg=BUTTON_Black,
            font=NAV_FONT,
            relief="flat",
            command=self.show_books_view,
        )
        btn_books.pack(side="left", padx=10)

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

        self.content = tk.Frame(self, bg=PRIMARY_BG)
        self.content.pack(fill="both", expand=True, padx=20, pady=20)

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    # ---------- Orders view ----------
    def show_orders_view(self):
        self._clear_content()

        top = tk.Frame(self.content, bg=PRIMARY_BG)
        top.pack(fill="x")

        tk.Label(
            top,
            text="All Orders",
            font=TITLE_FONT,
            bg=PRIMARY_BG,
            fg=ACCENT,
        ).pack(side="left")

        refresh_btn = tk.Button(
            top,
            text="Refresh",
            font=LABEL_FONT,
            bg=ACCENT,
            fg=BUTTON_FG,
            command=self._load_orders,
        )
        refresh_btn.pack(side="right")

        # Table
        table_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))

        columns = ("id", "customer", "total_price", "status", "created_at")
        self.order_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=15,
        )
        self.order_tree.heading("id", text="Order ID")
        self.order_tree.heading("customer", text="Customer")
        self.order_tree.heading("total_price", text="Total")
        self.order_tree.heading("status", text="Status")
        self.order_tree.heading("created_at", text="Created At")

        self.order_tree.column("id", width=70, anchor="center")
        self.order_tree.column("customer", width=150)
        self.order_tree.column("total_price", width=80, anchor="e")
        self.order_tree.column("status", width=80, anchor="center")
        self.order_tree.column("created_at", width=180)

        self.order_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.order_tree.yview)
        self.order_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Order details + status button
        bottom = tk.Frame(self.content, bg=PRIMARY_BG)
        bottom.pack(fill="x", pady=(10, 0))

        self.details_text = tk.Text(
            bottom,
            height=8,
            bg=PRIMARY_BG,
            fg=TEXT_COLOR,
            font=("Courier New", 10),
        )
        self.details_text.pack(side="left", fill="both", expand=True)

        self.order_tree.bind("<<TreeviewSelect>>", self._on_order_selected)

        btn_frame = tk.Frame(bottom, bg=PRIMARY_BG)
        btn_frame.pack(side="right", fill="y", padx=10)

        btn_paid = tk.Button(
            btn_frame,
            text="Mark as Paid",
            font=LABEL_FONT,
            bg=ACCENT,
            fg=BUTTON_FG,
            command=self._mark_order_paid,
        )
        btn_paid.pack(pady=5)

        self._load_orders()

    def _load_orders(self):
        self.orders, error = api_manager_get_orders()
        if error:
            messagebox.showerror("Error loading orders", error)
            return

        for row in self.order_tree.get_children():
            self.order_tree.delete(row)

        for o in self.orders:
            self.order_tree.insert(
                "",
                "end",
                iid=str(o["id"]),
                values=(
                    o["id"],
                    o["customer_username"],
                    f"${o['total_price']:.2f}",
                    o["payment_status"],
                    str(o["created_at"]),
                ),
            )

        self.details_text.config(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", "Select an order to see details.")
        self.details_text.config(state="disabled")

    def _get_order_by_id(self, order_id):
        for o in self.orders:
            if o["id"] == order_id:
                return o
        return None

    def _on_order_selected(self, event):
        sel = self.order_tree.selection()
        if not sel:
            return
        order_id = int(sel[0])
        o = self._get_order_by_id(order_id)
        if not o:
            return

        lines = []
        lines.append(f"Order ID: {o['id']}")
        lines.append(f"Customer: {o['customer_username']} (ID {o['user_id']})")
        lines.append(f"Status: {o['payment_status']}")
        lines.append(f"Total: ${o['total_price']:.2f}")
        lines.append("")
        lines.append("Items:")
        lines.append("-" * 60)
        for it in o.get("items", []):
            lines.append(
                f"{it['title']} ({it['type']}) - ${it['price']:.2f}"
            )

        self.details_text.config(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", "\n".join(lines))
        self.details_text.config(state="disabled")

    def _mark_order_paid(self):
        sel = self.order_tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select an order first.")
            return
        order_id = int(sel[0])

        confirm = messagebox.askyesno(
            "Confirm",
            f"Mark order #{order_id} as Paid?",
        )
        if not confirm:
            return

        ok, error = api_manager_update_order_status(order_id, "Paid")
        if error:
            messagebox.showerror("Error", error)
            return

        messagebox.showinfo("Success", "Order status updated.")
        self._load_orders()

    # ---------- Manage books view ----------
    def show_books_view(self):
        self._clear_content()

        top = tk.Frame(self.content, bg=PRIMARY_BG)
        top.pack(fill="x")

        tk.Label(
            top,
            text="Manage Books",
            font=TITLE_FONT,
            bg=PRIMARY_BG,
            fg=ACCENT,
        ).pack(side="left")

        self.book_search_var = tk.StringVar()
        entry = tk.Entry(top, textvariable=self.book_search_var, width=30, font=LABEL_FONT)
        entry.pack(side="left", padx=10)
        entry.bind("<Return>", lambda e: self._load_books())

        btn_search = tk.Button(
            top,
            text="Search",
            font=LABEL_FONT,
            bg=ACCENT,
            fg= BUTTON_FG,
            command=self._load_books,
        )
        btn_search.pack(side="left")

        # Table
        table_frame = tk.Frame(self.content, bg=PRIMARY_BG)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))

        columns = ("id", "title", "author", "price_buy", "price_rent")
        self.book_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=12,
        )
        self.book_tree.heading("id", text="ID")
        self.book_tree.heading("title", text="Title")
        self.book_tree.heading("author", text="Author")
        self.book_tree.heading("price_buy", text="Buy Price")
        self.book_tree.heading("price_rent", text="Rent Price")

        self.book_tree.column("id", width=50, anchor="center")
        self.book_tree.column("title", width=300)
        self.book_tree.column("author", width=200)
        self.book_tree.column("price_buy", width=80, anchor="e")
        self.book_tree.column("price_rent", width=80, anchor="e")

        self.book_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.book_tree.bind("<<TreeviewSelect>>", self._on_book_selected)

        # Form for add/update
        form = tk.Frame(self.content, bg=PRIMARY_BG)
        form.pack(fill="x", pady=(10, 0))

        tk.Label(form, text="Title:", font=LABEL_FONT, bg=PRIMARY_BG).grid(
            row=0, column=0, sticky="e", padx=5, pady=3
        )
        self.form_title = tk.Entry(form, width=40, font=LABEL_FONT)
        self.form_title.grid(row=0, column=1, padx=5, pady=3)

        tk.Label(form, text="Author:", font=LABEL_FONT, bg=PRIMARY_BG).grid(
            row=1, column=0, sticky="e", padx=5, pady=3
        )
        self.form_author = tk.Entry(form, width=40, font=LABEL_FONT)
        self.form_author.grid(row=1, column=1, padx=5, pady=3)

        tk.Label(form, text="Buy Price:", font=LABEL_FONT, bg=PRIMARY_BG).grid(
            row=2, column=0, sticky="e", padx=5, pady=3
        )
        self.form_buy = tk.Entry(form, width=15, font=LABEL_FONT)
        self.form_buy.grid(row=2, column=1, sticky="w", padx=5, pady=3)

        tk.Label(form, text="Rent Price:", font=LABEL_FONT, bg=PRIMARY_BG).grid(
            row=3, column=0, sticky="e", padx=5, pady=3
        )
        self.form_rent = tk.Entry(form, width=15, font=LABEL_FONT)
        self.form_rent.grid(row=3, column=1, sticky="w", padx=5, pady=3)

        btn_frame = tk.Frame(form, bg=PRIMARY_BG)
        btn_frame.grid(row=0, column=2, rowspan=4, padx=15)

        add_btn = tk.Button(
            btn_frame,
            text="Add New Book",
            font=LABEL_FONT,
            bg=ACCENT,
            fg= BUTTON_FG,
            command=self._add_book,
        )
        add_btn.pack(pady=5, fill="x")

        update_btn = tk.Button(
            btn_frame,
            text="Update Selected",
            font=LABEL_FONT,
            bg=ACCENT,
            fg= BUTTON_FG,
            command=self._update_selected_book,
        )
        update_btn.pack(pady=5, fill="x")

        self._load_books()

    def _load_books(self):
        keyword = self.book_search_var.get() if hasattr(self, "book_search_var") else ""
        self.books, error = api_search_books(keyword)
        if error:
            messagebox.showerror("Error loading books", error)
            return

        for row in getattr(self, "book_tree").get_children():
            self.book_tree.delete(row)

        self.book_map = {}
        for b in self.books:
            self.book_map[b["id"]] = b
            self.book_tree.insert(
                "",
                "end",
                iid=str(b["id"]),
                values=(
                    b["id"],
                    b["title"],
                    b["author"],
                    f"${float(b['price_buy']):.2f}",
                    f"${float(b['price_rent']):.2f}",
                ),
            )

    def _on_book_selected(self, event):
        sel = self.book_tree.selection()
        if not sel:
            return
        book_id = int(sel[0])
        b = self.book_map.get(book_id)
        if not b:
            return

        self.form_title.delete(0, "end")
        self.form_title.insert(0, b["title"])

        self.form_author.delete(0, "end")
        self.form_author.insert(0, b["author"])

        self.form_buy.delete(0, "end")
        self.form_buy.insert(0, str(b["price_buy"]))

        self.form_rent.delete(0, "end")
        self.form_rent.insert(0, str(b["price_rent"]))

    def _add_book(self):
        title = self.form_title.get().strip()
        author = self.form_author.get().strip()
        try:
            price_buy = float(self.form_buy.get())
            price_rent = float(self.form_rent.get())
        except ValueError:
            messagebox.showwarning("Invalid price", "Please enter numeric prices.")
            return

        book, error = api_manager_add_book(title, author, price_buy, price_rent)
        if error:
            messagebox.showerror("Error adding book", error)
            return

        messagebox.showinfo("Success", f"Book '{book['title']}' added.")
        self._load_books()

    def _update_selected_book(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showwarning("No selection", "Select a book to update.")
            return
        book_id = int(sel[0])

        title = self.form_title.get().strip()
        author = self.form_author.get().strip()
        try:
            price_buy = float(self.form_buy.get())
            price_rent = float(self.form_rent.get())
        except ValueError:
            messagebox.showwarning("Invalid price", "Please enter numeric prices.")
            return

        ok, error = api_manager_update_book(book_id, title, author, price_buy, price_rent)
        if error:
            messagebox.showerror("Error updating book", error)
            return

        messagebox.showinfo("Success", "Book updated.")
        self._load_books()
