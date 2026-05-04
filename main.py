import sys
import os
from PySide6.QtWidgets import QApplication, QStackedWidget, QMainWindow, QLabel

# Import DB
from database.db import init_db

# Import Widgets
from ui.auth.login_ui import LoginWidget
from ui.auth.register_ui import RegisterWidget


class DummyMainWindow(QMainWindow):
    """Màn hình tạm thời nếu chưa tạo MainWindow chính thức."""
    def __init__(self, user_info):
        super().__init__()
        self.setWindowTitle("SkyBound Air - Dashboard")
        self.resize(800, 600)
        lbl = QLabel(f"Chào mừng {user_info.get('full_name')} quay trở lại!", self)
        self.setCentralWidget(lbl)


def load_style(app):
    """Nạp file style CSS."""
    qss_path = os.path.join("assets", "styles", "auth.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"Warning: Không tìm thấy style tại {qss_path}")


def main():
    # 1. Khởi tạo Database (Tạo bảng + Seed dữ liệu nếu chưa có)
    init_db(seed=True)

    # 2. Khởi tạo PySide6 Application
    app = QApplication(sys.argv)
    load_style(app)

    # 3. Tạo Stacked Widget để chuyển đổi giữa các màn hình Auth
    stack = QStackedWidget()
    stack.resize(450, 650)

    login = LoginWidget()
    register = RegisterWidget()

    stack.addWidget(login)
    stack.addWidget(register)

    # 4. Kết nối chuyển màn hình bằng Signals
    login.go_register.connect(lambda: stack.setCurrentIndex(1))
    register.go_login.connect(lambda: stack.setCurrentIndex(0))

    # 5. Xử lý sau khi đăng nhập / đăng ký thành công
    def handle_login_success(user_info):
        print(f"Đăng nhập thành công! User info: {user_info}")
        try:
            from ui.main.main_window import MainWindow
            main_win = MainWindow(user_info)
        except ImportError:
            main_win = DummyMainWindow(user_info)

        main_win.show()
        stack.close()
        # Giữ tham chiếu để tránh Garbage Collector thu hồi giao diện
        app.main_window = main_win

    def handle_register_success(user_info):
        print(f"Đăng ký thành công cho email: {user_info.get('email')}")
        # Chuyển về màn hình đăng nhập sau khi đăng ký xong
        stack.setCurrentIndex(0)

    login.logged_in.connect(handle_login_success)
    register.registered.connect(handle_register_success)

    stack.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()