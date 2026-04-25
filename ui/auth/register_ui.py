from PySide6.QtWidgets import *
from PySide6.QtCore import Qt
from modules.auth import register_user

class RegisterUI(QWidget):
    def __init__(self, switch_to_login):
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

        subtitle = QLabel("Create an account to start booking.")
        subtitle.setObjectName("subtitle")

        # Inputs
        self.username = QLineEdit()
        self.username.setPlaceholderText("Email address")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.confirm = QLineEdit()
        self.confirm.setPlaceholderText("Confirm Password")
        self.confirm.setEchoMode(QLineEdit.Password)

        # Buttons
        self.register_btn = QPushButton("Create Account")
        self.register_btn.setObjectName("primaryBtn")
        self.register_btn.setMinimumHeight(40)

        self.back_btn = QPushButton("Already have an account? Log in")
        self.back_btn.setObjectName("linkBtn")

        # Add widgets
        layout.addWidget(self.title, alignment=Qt.AlignCenter)
        layout.addWidget(subtitle, alignment=Qt.AlignCenter)
        layout.addWidget(self.username)
        layout.addWidget(self.password)
        layout.addWidget(self.confirm)
        layout.addWidget(self.register_btn)
        layout.addWidget(self.back_btn, alignment=Qt.AlignCenter)

        card.setLayout(layout)
        main_layout.addWidget(card)

        self.setLayout(main_layout)

        # Events
        self.back_btn.clicked.connect(switch_to_login)
        self.register_btn.clicked.connect(self.handle_register)

    def handle_register(self):
        user = self.username.text()
        pw = self.password.text()
        cf = self.confirm.text()

        if not user or not pw:
            QMessageBox.warning(self, "Error", "Fields cannot be empty")
            return

        if pw != cf:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return

        if register_user(user, pw):
            QMessageBox.information(self, "Success", "Account created")
            self.back_btn.click()
        else:
            QMessageBox.warning(self, "Error", "Username already exists")