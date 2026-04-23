import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QFrame
)
from PySide6.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Airline Booking System - Dashboard")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        # Header
        header = QLabel("Find your next destination\nExplore over 200 paths to your dreams.")
        header.setAlignment(Qt.AlignCenter)
        header.setObjectName("header")
        main_layout.addWidget(header)

        # Search section
        search_layout = QHBoxLayout()
        self.txt_from = QLineEdit("London (LHR)")
        self.txt_to = QLineEdit("Tokyo (HND)")
        self.txt_date = QLineEdit("10/24/2026")
        btn_search = QPushButton("Search Flights")

        self.txt_from.setPlaceholderText("FROM")
        self.txt_to.setPlaceholderText("TO")
        self.txt_date.setPlaceholderText("DEPARTURE DATE")

        search_layout.addWidget(self.txt_from)
        search_layout.addWidget(self.txt_to)
        search_layout.addWidget(self.txt_date)
        search_layout.addWidget(btn_search)
        main_layout.addLayout(search_layout)

        # Stats section
        stats_layout = QHBoxLayout()
        lbl_dest = QLabel("Total Destinations:\n284")
        lbl_bookings = QLabel("Active Bookings:\n1,284")
        lbl_rating = QLabel("User Rating:\n4.9 / 5")

        for lbl in (lbl_dest, lbl_bookings, lbl_rating):
            lbl.setFrameShape(QFrame.Box)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setObjectName("statBox")
            stats_layout.addWidget(lbl)

        main_layout.addLayout(stats_layout)

        # Featured section
        featured_title = QLabel("Featured Destinations\nCurated collections just for you.")
        featured_title.setAlignment(Qt.AlignCenter)
        featured_title.setObjectName("featuredTitle")
        main_layout.addWidget(featured_title)

        featured_buttons = QHBoxLayout()
        btn_popular = QPushButton("Popular")
        btn_offers = QPushButton("Offers")
        featured_buttons.addWidget(btn_popular)
        featured_buttons.addWidget(btn_offers)
        main_layout.addLayout(featured_buttons)

        # Table placeholder (for search results)
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Flight", "From", "To"])
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open("style.qss", "r") as f:
        app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
