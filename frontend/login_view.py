# frontend/login_view.py
import tkinter as tk
from tkinter import messagebox

from api_client import api_login, api_register

PRIMARY_BG = "#f7f1e3"
NAV_BG = "#3b3a30"
NAV_FG = "#fdfaf3"
ACCENT = "#8b0000"
TEXT_COLOR = "#2b2b2b"

BUTTON_BG = "#d2b48c"   # tan, readable on all platforms
BUTTON_FG = "#8b0000"   # black text

TITLE_FONT = ("Georgia", 24, "bold")
SUBTITLE_FONT = ("Georgia", 14)
LABEL_FONT = ("Georgia", 12)


class LoginFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=PRIMARY_BG)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        # Center wrapper
        wrapper = tk.Frame(self, bg=PRIMARY_BG)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(
            wrapper,
            text="Online Bookstore",
            font=TITLE_FONT,
            fg=ACCENT,
            bg=PRIMARY_BG,
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        subtitle = tk.Label(
            wrapper,
            text="Please sign in to continue",
            font=SUBTITLE_FONT,
            fg=TEXT_COLOR,
            bg=PRIMARY_BG,
        )
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Username
        tk.Label(wrapper, text="Username:", font=LABEL_FONT, bg=PRIMARY_BG).grid(
            row=2, column=0, sticky="e", padx=(0, 10), pady=5
        )
        self.username_entry = tk.Entry(wrapper, width=30, font=LABEL_FONT)
        self.username_entry.grid(row=2, column=1, pady=5)

        # Password
        tk.Label(wrapper, text="Password:", font=LABEL_FONT, bg=PRIMARY_BG).grid(
            row=3, column=0, sticky="e", padx=(0, 10), pady=5
        )
        self.password_entry = tk.Entry(wrapper, show="*", width=30, font=LABEL_FONT)
        self.password_entry.grid(row=3, column=1, pady=5)

        # Login button
        login_btn = tk.Button(
            wrapper,
            text="Login",
            font=LABEL_FONT,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            width=20,
            command=self.handle_login,
        )
        login_btn.grid(row=4, column=0, columnspan=2, pady=(15, 5))

        # Register link
        reg_btn = tk.Button(
            wrapper,
            text="New user? Register here",
            font=("Georgia", 11, "underline"),
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            relief="flat",
            command=self.controller.show_register,
        )
        reg_btn.grid(row=5, column=0, columnspan=2, pady=(5, 0))

        self.username_entry.focus_set()

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Missing info", "Please enter username and password.")
            return

        user_info, error = api_login(username, password)
        if error:
            messagebox.showerror("Login failed", error)
            return

        messagebox.showinfo("Welcome", f"Logged in as {user_info['username']} ({user_info['role']})")
        self.controller.on_login_success(user_info)


class RegisterFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, bg=PRIMARY_BG)
        self.controller = controller
        self._build_ui()

    def _build_ui(self):
        wrapper = tk.Frame(self, bg=PRIMARY_BG)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(
            wrapper,
            text="Create a New Account",
            font=TITLE_FONT,
            fg=ACCENT,
            bg=PRIMARY_BG,
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        subtitle = tk.Label(
            wrapper,
            text="Fill in your details to register as a customer",
            font=SUBTITLE_FONT,
            fg=TEXT_COLOR,
            bg=PRIMARY_BG,
        )
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 20))

        # Username
        tk.Label(wrapper, text="Username:", font=LABEL_FONT, bg=PRIMARY_BG).grid(
            row=2, column=0, sticky="e", padx=(0, 10), pady=5
        )
        self.username_entry = tk.Entry(wrapper, width=30, font=LABEL_FONT)
        self.username_entry.grid(row=2, column=1, pady=5)

        # Email
        tk.Label(wrapper, text="Email:", font=LABEL_FONT, bg=PRIMARY_BG).grid(
            row=3, column=0, sticky="e", padx=(0, 10), pady=5
        )
        self.email_entry = tk.Entry(wrapper, width=30, font=LABEL_FONT)
        self.email_entry.grid(row=3, column=1, pady=5)

        # Password
        tk.Label(wrapper, text="Password:", font=LABEL_FONT, bg=PRIMARY_BG).grid(
            row=4, column=0, sticky="e", padx=(0, 10), pady=5
        )
        self.password_entry = tk.Entry(wrapper, show="*", width=30, font=LABEL_FONT)
        self.password_entry.grid(row=4, column=1, pady=5)

        # Register button
        reg_btn = tk.Button(
            wrapper,
            text="Create Account",
            font=LABEL_FONT,
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            width=20,
            command=self.handle_register,
        )
        reg_btn.grid(row=5, column=0, columnspan=2, pady=(15, 5))

        # Back to login
        back_btn = tk.Button(
            wrapper,
            text="Back to Login",
            font=("Georgia", 11, "underline"),
            bg=BUTTON_BG,
            fg=BUTTON_FG,
            relief="flat",
            command=self.controller.show_login,
        )
        back_btn.grid(row=6, column=0, columnspan=2, pady=(5, 0))

    def handle_register(self):
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not email or not password:
            messagebox.showwarning("Missing info", "Please fill all fields.")
            return

        user_info, error = api_register(username, email, password)
        if error:
            messagebox.showerror("Registration failed", error)
            return

        messagebox.showinfo(
            "Success",
            f"Account created for {user_info['username']}.\nYou can now log in.",
        )
        self.controller.show_login()
