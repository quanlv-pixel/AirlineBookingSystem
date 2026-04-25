from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from modules.auth import login_user

class LoginUI(QWidget):
    def __init__(self, switch_to_register, login_success):
        super().__init__()

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        card = QWidget()
        card.setObjectName("authCard")

        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Title
        self.title = QLabel("SkyBoundAir")
        self.title.setObjectName("title")

        subtitle = QLabel("Log in to manage your journeys.")
        subtitle.setObjectName("subtitle")

        # Inputs
        self.username = QLineEdit()
        self.username.setPlaceholderText("Email address")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        # Buttons
        self.login_btn = QPushButton("Sign In")
        self.login_btn.setObjectName("primaryBtn")
        self.login_btn.setMinimumHeight(40)

        self.register_btn = QPushButton("Don't have an account? Sign up")
        self.register_btn.setObjectName("linkBtn")

        # Add widgets
        layout.addWidget(self.title, alignment=Qt.AlignCenter)
        layout.addWidget(subtitle, alignment=Qt.AlignCenter)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.register_btn, alignment=Qt.AlignCenter)

        card.setLayout(layout)
        main_layout.addWidget(card)

        self.setLayout(main_layout)

        # Events
        self.register_btn.clicked.connect(switch_to_register)
        self.login_btn.clicked.connect(self.handle_login)

        self.login_success = login_success

    def handle_login(self):
        user = self.username.text()
        pw = self.password.text()

        if not user or not pw:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        if login_user(user, pw):
            self.login_success()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password")