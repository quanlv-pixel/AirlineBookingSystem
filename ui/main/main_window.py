from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Airline System")

        central = QWidget()
        layout = QHBoxLayout()

        # Sidebar
        sidebar = QVBoxLayout()
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_flights = QPushButton("Flights")

        sidebar.addWidget(self.btn_dashboard)
        sidebar.addWidget(self.btn_flights)

        # Pages
        self.stack = QStackedWidget()
        self.dashboard = QLabel("Dashboard")
        self.flights = QLabel("Flights Page")

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.flights)

        self.btn_dashboard.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_flights.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addLayout(sidebar, 1)
        layout.addWidget(self.stack, 4)

        central.setLayout(layout)
        self.setCentralWidget(central)