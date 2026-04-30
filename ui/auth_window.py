"""
ui/auth_window.py
Cửa sổ chứa cả Register và Login, dùng QStackedWidget để chuyển đổi.
Chạy file này để test giao diện độc lập.
"""

import sys, os

# Thêm root project vào sys.path để import đúng module
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget,
    QWidget, QVBoxLayout,
)
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtCore import Qt, QSize

from ui.auth.register_ui import RegisterWidget
from ui.auth.login_ui    import LoginWidget


# ─── AuthWindow ─────────────────────────────────────────────────────────────

class AuthWindow(QMainWindow):
    """
    Cửa sổ xác thực chính.
    Sau khi đăng nhập thành công sẽ emit tín hiệu hoặc mở MainWindow.
    """

    PAGE_REGISTER = 0
    PAGE_LOGIN    = 1

    def __init__(self, start_page: int = PAGE_REGISTER, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SkyBoundAir")
        self.setMinimumSize(QSize(520, 680))

        # Nền tổng thể
        pal = self.palette()
        pal.setColor(QPalette.Window, QColor("#EEF0F5"))
        self.setPalette(pal)
        self.setAutoFillBackground(True)

        # Load stylesheet
        self._load_qss()

        # Stack
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # Pages
        self._register_page = RegisterWidget()
        self._login_page    = LoginWidget()

        self._stack.addWidget(self._register_page)   # index 0
        self._stack.addWidget(self._login_page)       # index 1

        # Kết nối signals
        self._register_page.go_login.connect(self._show_login)
        self._login_page.go_register.connect(self._show_register)

        self._register_page.registered.connect(self._on_auth_success)
        self._login_page.logged_in.connect(self._on_auth_success)

        self._stack.setCurrentIndex(start_page)

    # ── Navigation ───────────────────────────────────────────────────────

    def _show_login(self):
        self._stack.setCurrentIndex(self.PAGE_LOGIN)

    def _show_register(self):
        self._stack.setCurrentIndex(self.PAGE_REGISTER)

    # ── Auth success ─────────────────────────────────────────────────────

    def _on_auth_success(self, user_info: dict):
        """
        Gọi khi đăng nhập / đăng ký thành công.
        Mở MainWindow và đóng AuthWindow.
        """
        print(f"[Auth] Đăng nhập thành công: {user_info}")

        try:
            from ui.main.main_window import MainWindow
            self._main = MainWindow(user_info=user_info)
            self._main.show()
        except ImportError:
            # main_window.py chưa tồn tại — hiển thị thông báo tạm
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self,
                "Thành công 🎉",
                f"Xin chào, {user_info.get('full_name', 'bạn')}!\n\n"
                "Đăng nhập thành công. MainWindow chưa được tạo.",
            )
            return

        self.close()

    # ── QSS Loader ───────────────────────────────────────────────────────

    def _load_qss(self):
        qss_path = os.path.join(ROOT, "assets", "styles", "auth.qss")
        if os.path.exists(qss_path):
            with open(qss_path, encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"[Warning] Không tìm thấy auth.qss tại: {qss_path}")


# ─── Entry point ─────────────────────────────────────────────────────────────

def run_auth(start_page: int = AuthWindow.PAGE_REGISTER):
    app = QApplication.instance() or QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    win = AuthWindow(start_page=start_page)
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    # Truyền "login" làm argument để mở thẳng màn hình đăng nhập
    page = AuthWindow.PAGE_LOGIN if (len(sys.argv) > 1 and sys.argv[1] == "login") \
           else AuthWindow.PAGE_REGISTER
    run_auth(page)