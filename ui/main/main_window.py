"""
ui/main/main_window.py
Cửa sổ chính sau khi đăng nhập — SkyBoundAir
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QStackedWidget, QLabel
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QSize

from ui.main.dashboard_ui import DashboardWidget
from ui.main.flight_ui import FlightWidget


class MainWindow(QMainWindow):
    def __init__(self, user_info: dict = None, parent=None):
        super().__init__(parent)
        self.user_info = user_info or {}

        self.setWindowTitle("SkyBoundAir")
        self.setMinimumSize(QSize(1100, 700))
        self.resize(1200, 750)

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        from PySide6.QtWidgets import QHBoxLayout
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Stack chứa các trang ──────────────────────────────
        self.stack = QStackedWidget()

        # Trang 0: Dashboard
        self.page_dashboard = DashboardWidget(user_info=self.user_info)
        self.stack.addWidget(self.page_dashboard)

        # Trang 1: Flights
        self.page_flights = FlightWidget()
        self.stack.addWidget(self.page_flights)

        # Trang 2: Bookings (placeholder)
        self.page_bookings = self._placeholder("🎫  Vé của tôi\n\n(Đang phát triển)")
        self.stack.addWidget(self.page_bookings)

        # Trang 3: Profile (placeholder)
        self.page_profile = self._placeholder("👤  Cài đặt tài khoản\n\n(Đang phát triển)")
        self.stack.addWidget(self.page_profile)

        root.addWidget(self.stack)

        # ── Kết nối sidebar buttons ───────────────────────────
        self.page_dashboard.btn_home.clicked.connect(
            lambda: self.stack.setCurrentIndex(0))
        self.page_dashboard.btn_flights.clicked.connect(
            lambda: self.stack.setCurrentIndex(1))
        self.page_dashboard.btn_bookings.clicked.connect(
            lambda: self.stack.setCurrentIndex(2))
        self.page_dashboard.btn_profile.clicked.connect(
            lambda: self.stack.setCurrentIndex(3))

        # Đăng xuất
        self.page_dashboard.logout_clicked.connect(self._on_logout)

        # Search từ dashboard → chuyển sang trang flights
        self.page_dashboard.search_triggered.connect(self._on_search)

        # Đặt vé từ flight_ui → có thể chuyển sang booking sau
        self.page_flights.book_clicked.connect(self._on_book)

    # ── Helpers ──────────────────────────────────────────────

    def _placeholder(self, text: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background-color: #F8FAFC;")
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignCenter)
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont("Segoe UI", 16))
        lbl.setStyleSheet("color: #94A3B8;")
        lay.addWidget(lbl)
        return w

    def _on_logout(self):
        from ui.auth.login_ui import LoginWidget
        from ui.auth.register_ui import RegisterWidget
        from PySide6.QtWidgets import QStackedWidget as QSW

        self._auth = QSW()
        self._auth.setWindowTitle("SkyBoundAir")
        self._auth.resize(480, 680)

        login    = LoginWidget()
        register = RegisterWidget()
        self._auth.addWidget(login)
        self._auth.addWidget(register)

        login.go_register.connect(lambda: self._auth.setCurrentIndex(1))
        register.go_login.connect(lambda: self._auth.setCurrentIndex(0))

        def re_login(user_info):
            new_win = MainWindow(user_info)
            new_win.show()
            self._auth.close()

        login.logged_in.connect(re_login)
        register.registered.connect(re_login)

        self._auth.show()
        self.close()

    def _on_search(self, params: dict):
        print(f"[Search] {params}")
        self.page_flights.update_search(params)
        self.stack.setCurrentIndex(1)

    def _on_book(self, flight: dict):
        print(f"[Book] {flight}")
        self.stack.setCurrentIndex(2)