from PySide6.QtWidgets import QApplication, QStackedWidget
from database.init_db import init_db

from ui.auth.login_ui import LoginUI
from ui.auth.register_ui import RegisterUI
from ui.main.main_window import MainWindow

def load_style(app):
    with open("assets/styles/style.qss", "r") as f:
        app.setStyleSheet(f.read())

init_db()

app = QApplication([])
load_style(app)

stack = QStackedWidget()

def open_main():
    main = MainWindow()
    main.show()
    stack.close()

login = LoginUI(
    switch_to_register=lambda: stack.setCurrentIndex(1),
    login_success=open_main
)

register = RegisterUI(
    switch_to_login=lambda: stack.setCurrentIndex(0)
)

stack.addWidget(login)
stack.addWidget(register)

stack.show()
app.exec()