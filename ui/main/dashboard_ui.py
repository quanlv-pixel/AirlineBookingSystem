"""
ui/main/dashboard_ui.py
Giao diện Dashboard chính cho SkyBound Air
Đã tối ưu hóa stylesheet, hiệu ứng hover, và hỗ trợ load dữ liệu từ Database.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QFrame, QTableWidget, 
    QTableWidgetItem, QHeaderView, QComboBox, 
    QScrollArea, QSizePolicy, QAbstractItemView
)
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap
from PySide6.QtCore import Qt, Signal, QSize
import datetime

# Thử import từ database nếu có
try:
    from database.db import get_connection, fetchall, fetchone
except ImportError:
    # Fallback cho trường hợp test UI độc lập
    get_connection = None
    fetchall = None
    fetchone = None


class StatCard(QFrame):
    """Widget hiển thị các thẻ thông số nhanh (Stats)"""
    def __init__(self, title: str, value: str, icon_text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left area: Title & Value
        info_layout = QVBoxLayout()
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("StatTitle")
        
        self.val_lbl = QLabel(value)
        self.val_lbl.setObjectName("StatValue")
        
        info_layout.addWidget(self.title_lbl)
        info_layout.addWidget(self.val_lbl)
        info_layout.addStretch()
        
        # Right area: Icon
        self.icon_lbl = QLabel(icon_text)
        self.icon_lbl.setObjectName("StatIcon")
        self.icon_lbl.setAlignment(Qt.AlignCenter)
        
        layout.addLayout(info_layout, stretch=3)
        layout.addWidget(self.icon_lbl, stretch=1, alignment=Qt.AlignVCenter)


class DashboardWidget(QWidget):
    logout_clicked = Signal()
    search_triggered = Signal(dict)  

    def __init__(self, user_info: dict = None, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardWindow")
        self.user_info = user_info or {
            "id": 1,
            "first_name": "Khách",
            "last_name": "Hàng",
            "email": "customer@skybound.com",
            "role": "customer"
        }
        
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # 1. Root Layout & Background
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # ─── SIDEBAR NAVIGATION ──────────────────────────────────────────────
        sidebar = QFrame(self)
        sidebar.setObjectName("SidebarFrame")
        sidebar.setFixedWidth(260)
        
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(20, 30, 20, 30)
        side_layout.setSpacing(10)
        
        # App Branding
        brand_lbl = QLabel("SkyBound")
        brand_lbl.setObjectName("SidebarBrand")
        sub_brand_lbl = QLabel("AIRLINES")
        sub_brand_lbl.setObjectName("SidebarSubBrand")
        
        side_layout.addWidget(brand_lbl)
        side_layout.addWidget(sub_brand_lbl)
        side_layout.addSpacing(35)
        
        # Menu Navigation Buttons
        self.btn_home = QPushButton("  Giao diện chính")
        self.btn_home.setObjectName("SidebarBtnActive")
        
        self.btn_flights = QPushButton("  Chuyến bay")
        self.btn_flights.setObjectName("SidebarBtn")
        
        self.btn_bookings = QPushButton("  Vé của tôi")
        self.btn_bookings.setObjectName("SidebarBtn")
        
        self.btn_profile = QPushButton("  Cài đặt tài khoản")
        self.btn_profile.setObjectName("SidebarBtn")
        
        side_layout.addWidget(self.btn_home)
        side_layout.addWidget(self.btn_flights)
        side_layout.addWidget(self.btn_bookings)
        side_layout.addWidget(self.btn_profile)
        
        side_layout.addStretch()
        
        # Logout button
        btn_logout = QPushButton(" Đăng xuất")
        btn_logout.setObjectName("SidebarLogoutBtn")
        btn_logout.clicked.connect(self.logout_clicked.emit)
        side_layout.addWidget(btn_logout)
        
        root.addWidget(sidebar)

        # ─── MAIN AREA ────────────────────────────────────────────────────────
        main_area = QScrollArea(self)
        main_area.setWidgetResizable(True)
        main_area.setObjectName("MainAreaScroll")
        
        main_widget = QWidget()
        main_widget.setObjectName("MainAreaWidget")
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(35, 30, 35, 30)
        main_layout.setSpacing(25)
        
        # TOP BAR: Greeting & Welcome Text
        top_bar = QHBoxLayout()
        greet_layout = QVBoxLayout()
        
        full_name = f"{self.user_info.get('first_name', '')} {self.user_info.get('last_name', '')}"
        self.greeting_lbl = QLabel(f"Xin chào, {full_name or 'Hành khách'} 👋")
        self.greeting_lbl.setObjectName("GreetingTitle")
        
        sub_greet_lbl = QLabel("Chào mừng bạn trở lại với SkyBound Air. Hôm nay bạn muốn bay đi đâu?")
        sub_greet_lbl.setObjectName("GreetingSub")
        
        greet_layout.addWidget(self.greeting_lbl)
        greet_layout.addWidget(sub_greet_lbl)
        top_bar.addLayout(greet_layout)
        top_bar.addStretch()
        
        # Avatar (Initial)
        avatar = QLabel(f"{self.user_info.get('first_name', 'H')[0].upper()}")
        avatar.setObjectName("UserAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        top_bar.addWidget(avatar)
        
        main_layout.addLayout(top_bar)
        
        # ── STATS ROW ──
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
        
        self.card_bookings = StatCard("Tổng số vé đã đặt", "0 Vé", "🎫", self)
        self.card_points = StatCard("Điểm thưởng (SkyMiles)", "1,250 PTS", "⭐", self)
        self.card_next_trip = StatCard("Chuyến bay sắp tới", "Chưa có", "✈️", self)
        
        stats_layout.addWidget(self.card_bookings)
        stats_layout.addWidget(self.card_points)
        stats_layout.addWidget(self.card_next_trip)
        
        main_layout.addLayout(stats_layout)
        
        # ── QUICK SEARCH BOARD ──
        search_card = QFrame(self)
        search_card.setObjectName("SearchCard")
        search_layout = QVBoxLayout(search_card)
        search_layout.setContentsMargins(25, 25, 25, 25)
        search_layout.setSpacing(15)
        
        search_title = QLabel("Tìm kiếm chuyến bay nhanh")
        search_title.setObjectName("SectionTitle")
        search_layout.addWidget(search_title)
        
        # Inputs row
        inputs_layout = QHBoxLayout()
        inputs_layout.setSpacing(15)
        
        # From Combo
        from_layout = QVBoxLayout()
        lbl_from = QLabel("ĐIỂM KHỞI HÀNH")
        lbl_from.setObjectName("InputLabel")
        self.combo_from = QComboBox()
        self.combo_from.setObjectName("SearchCombo")
        from_layout.addWidget(lbl_from)
        from_layout.addWidget(self.combo_from)
        
        # To Combo
        to_layout = QVBoxLayout()
        lbl_to = QLabel("ĐIỂM ĐẾN")
        lbl_to.setObjectName("InputLabel")
        self.combo_to = QComboBox()
        self.combo_to.setObjectName("SearchCombo")
        to_layout.addWidget(lbl_to)
        to_layout.addWidget(self.combo_to)
        
        # Date
        date_layout = QVBoxLayout()
        lbl_date = QLabel("NGÀY KHỞI HÀNH (YYYY-MM-DD)")
        lbl_date.setObjectName("InputLabel")
        self.input_date = QLineEdit()
        self.input_date.setObjectName("SearchInput")
        self.input_date.setText(datetime.date.today().strftime("%Y-%m-%d"))
        date_layout.addWidget(lbl_date)
        date_layout.addWidget(self.input_date)
        
        inputs_layout.addLayout(from_layout, stretch=2)
        inputs_layout.addLayout(to_layout, stretch=2)
        inputs_layout.addLayout(date_layout, stretch=2)
        
        # Search Button
        btn_search = QPushButton(" Tìm chuyến bay")
        btn_search.setObjectName("PrimaryButton")
        btn_search.setFixedHeight(46)
        btn_search.clicked.connect(self._on_search)
        inputs_layout.addWidget(btn_search, alignment=Qt.AlignBottom)
        
        search_layout.addLayout(inputs_layout)
        main_layout.addWidget(search_card)
        
        # ── RECENT BOOKINGS TABLE ──
        table_card = QFrame(self)
        table_card.setObjectName("TableCard")
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(25, 25, 25, 25)
        table_layout.setSpacing(15)
        
        table_title = QLabel("Các chuyến bay đã đặt gần đây")
        table_title.setObjectName("SectionTitle")
        table_layout.addWidget(table_title)
        
        self.table_bookings = QTableWidget()
        self.table_bookings.setObjectName("BookingsTable")
        self.table_bookings.setColumnCount(6)
        self.table_bookings.setHorizontalHeaderLabels([
            "Mã đặt chỗ", "Chuyến bay", "Điểm khởi hành", "Điểm đến", "Thời gian bay", "Trạng thái"
        ])
        self.table_bookings.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_bookings.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_bookings.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_bookings.verticalHeader().setVisible(False)
        self.table_bookings.setFixedHeight(220)
        
        table_layout.addWidget(self.table_bookings)
        main_layout.addWidget(table_card)
        
        main_layout.addStretch()
        main_area.setWidget(main_widget)
        root.addWidget(main_area)

    # ─── DATA LOADING & LOGIC ────────────────────────────────────────────────
    
    def _load_data(self):
        """Tải dữ liệu sân bay và lịch sử vé từ SQLite."""
        # 1. Load airports into ComboBoxes
        airports = []
        if fetchall:
            try:
                rows = fetchall("SELECT code, city FROM airports ORDER BY city ASC")
                airports = [f"{r['city']} ({r['code']})" for r in rows]
            except Exception as e:
                print(f"Lỗi tải airports: {e}")
                
        if not airports:
            # Dữ liệu mẫu fallback nếu chưa có DB
            airports = [
                "Hà Nội (HAN)", "Hồ Chí Minh (SGN)", 
                "Đà Nẵng (DAD)", "Phú Quốc (PQC)", "Nha Trang (CXR)"
            ]
            
        self.combo_from.clear()
        self.combo_to.clear()
        self.combo_from.addItems(airports)
        self.combo_to.addItems(airports)
        
        if len(airports) > 1:
            self.combo_to.setCurrentIndex(1)  # Chọn SGN làm mặc định cho Điểm đến
            
        # 2. Load Bookings Table
        if fetchall and self.user_info.get("id"):
            try:
                # Đếm tổng số vé của user
                cnt_row = fetchone(
                    "SELECT COUNT(*) as total FROM bookings WHERE user_id = ?", 
                    (self.user_info["id"],)
                )
                total_v = cnt_row["total"] if cnt_row else 0
                self.card_bookings.val_lbl.setText(f"{total_v} Vé")
                
                # Truy vấn lịch sử vé gần đây
                booking_rows = fetchall("""
                    SELECT b.id as b_id, b.booking_code, f.flight_number,
                           a1.city as origin, a2.city as destination,
                           f.departure_time, b.status
                    FROM bookings b
                    JOIN flights f  ON f.id  = b.flight_id
                    JOIN airports a1 ON a1.id = f.origin_id
                    JOIN airports a2 ON a2.id = f.destination_id
                    WHERE b.user_id = ?
                    ORDER BY b.booked_at DESC
                    LIMIT 5
                """, (self.user_info["id"],))
                
                self.table_bookings.setRowCount(0)
                for r in booking_rows:
                    row_idx = self.table_bookings.rowCount()
                    self.table_bookings.insertRow(row_idx)
                    
                    self.table_bookings.setItem(row_idx, 0, QTableWidgetItem(f"BK-{r['b_id']:04d}"))
                    self.table_bookings.setItem(row_idx, 1, QTableWidgetItem(str(r['flight_number'])))
                    self.table_bookings.setItem(row_idx, 2, QTableWidgetItem(str(r['origin'])))
                    self.table_bookings.setItem(row_idx, 3, QTableWidgetItem(str(r['destination'])))
                    self.table_bookings.setItem(row_idx, 4, QTableWidgetItem(str(r['departure_time'])))
                    
                    # Trạng thái vé
                    status_lbl = str(r['status']).capitalize()
                    status_item = QTableWidgetItem(status_lbl)
                    if status_lbl.lower() == "confirmed":
                        status_item.setForeground(QColor("#11CAA0"))
                    else:
                        status_item.setForeground(QColor("#FFA114"))
                        
                    self.table_bookings.setItem(row_idx, 5, status_item)
                
                # Cập nhật Card chuyến bay sắp tới nếu có
                if booking_rows:
                    self.card_next_trip.val_lbl.setText(str(booking_rows[0]['origin']))
            except Exception as e:
                print(f"Lỗi tải bookings: {e}")
        else:
            # Dữ liệu bảng test UI tạm thời
            self._insert_mock_row("BK-0012", "SB-102", "Hà Nội", "Hồ Chí Minh", "2026-05-15 08:30", "Confirmed")
            self._insert_mock_row("BK-0034", "SB-501", "Hà Nội", "Đà Nẵng", "2026-05-22 14:15", "Pending")

    def _insert_mock_row(self, code, f_num, fr, to, time, status):
        row_idx = self.table_bookings.rowCount()
        self.table_bookings.insertRow(row_idx)
        self.table_bookings.setItem(row_idx, 0, QTableWidgetItem(code))
        self.table_bookings.setItem(row_idx, 1, QTableWidgetItem(f_num))
        self.table_bookings.setItem(row_idx, 2, QTableWidgetItem(fr))
        self.table_bookings.setItem(row_idx, 3, QTableWidgetItem(to))
        self.table_bookings.setItem(row_idx, 4, QTableWidgetItem(time))
        status_item = QTableWidgetItem(status)
        if status.lower() == "confirmed":
            status_item.setForeground(QColor("#11CAA0"))
        else:
            status_item.setForeground(QColor("#FFA114"))
        self.table_bookings.setItem(row_idx, 5, status_item)

    def _on_search(self):
        """Gửi tín hiệu tìm kiếm chuyến bay ra bên ngoài"""
        flight_from = self.combo_from.currentText()
        flight_to = self.combo_to.currentText()
        flight_date = self.input_date.text().strip()
        
        # Chỉ lấy mã code trong ngoặc tròn HAN, SGN...
        from_code = flight_from.split('(')[-1].replace(')', '') if '(' in flight_from else flight_from
        to_code = flight_to.split('(')[-1].replace(')', '') if '(' in flight_to else flight_to
        
        self.search_triggered.emit({
            "from_code": from_code,
            "to_code": to_code,
            "date": flight_date
        })


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    # Style nạp từ main.py qua app.setStyleSheet()
    
    # Test widget
    win = DashboardWidget()
    win.resize(1100, 750)
    win.show()
    sys.exit(app.exec())