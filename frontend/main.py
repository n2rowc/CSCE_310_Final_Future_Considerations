# frontend/main.py
import tkinter as tk

from login_view import LoginFrame, RegisterFrame
from customer_view import CustomerFrame
from manager_view import ManagerFrame
from api_client import clear_auth_token

PRIMARY_BG = "#f7f1e3"


class BookstoreApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Online Bookstore")
        # Large, “desktop app” window
        self.geometry("1100x700")
        self.configure(bg=PRIMARY_BG)

        self.user_info = None
        self.current_frame = None

        self.show_login()

    # --------- Navigation helpers ----------
    def _switch_frame(self, frame_cls):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_cls(self, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login(self):
        self._switch_frame(LoginFrame)

    def show_register(self):
        self._switch_frame(RegisterFrame)

    def on_login_success(self, user_info: dict):
        self.user_info = user_info
        role = user_info.get("role")
        if role == "manager":
            self._switch_frame(ManagerFrame)
        else:
            self._switch_frame(CustomerFrame)

    def logout(self):
        # Clear authentication token
        clear_auth_token()
        self.user_info = None
        self.show_login()


def main():
    app = BookstoreApp()
    app.mainloop()


if __name__ == "__main__":
    main()
