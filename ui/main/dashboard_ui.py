"""
ui/main/dashboard_ui.py
SkyBoundAir — Dashboard chính
Thiết kế: TopNav + Hero Banner + Search Card + Stat Cards
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox,
    QScrollArea, QAbstractItemView, QRadioButton, QButtonGroup
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt, Signal
import datetime

try:
    from database.db import get_connection, fetchall, fetchone
except ImportError:
    get_connection = None
    fetchall = None
    fetchone = None


# ─────────────────────────────────────────────────────────────
#  Stat Card
# ─────────────────────────────────────────────────────────────
class StatCard(QFrame):
    def __init__(self, title: str, value: str,
                 icon_text: str, icon_color: str = "#3B82F6", parent=None):
        super().__init__(parent)
        self.setObjectName("StatCard")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(16)

        # Left: label + value
        info = QVBoxLayout()
        info.setSpacing(4)

        lbl_title = QLabel(title.upper())
        lbl_title.setObjectName("StatTitle")

        self.val_lbl = QLabel(value)
        self.val_lbl.setObjectName("StatValue")

        info.addWidget(lbl_title)
        info.addWidget(self.val_lbl)

        # Right: icon bubble
        icon_lbl = QLabel(icon_text)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setFixedSize(52, 52)
        icon_lbl.setStyleSheet(
            f"background-color: {icon_color}22; border-radius: 26px;"
            f"font-size: 24px; color: {icon_color};"
        )

        lay.addLayout(info, stretch=1)
        lay.addWidget(icon_lbl)


# ─────────────────────────────────────────────────────────────
#  Dashboard Widget
# ─────────────────────────────────────────────────────────────
class DashboardWidget(QWidget):
    logout_clicked  = Signal()
    search_triggered = Signal(dict)

    def __init__(self, user_info: dict = None, parent=None):
        super().__init__(parent)
        self.setObjectName("DashboardWindow")
        self.user_info = user_info or {
            "id": 1, "first_name": "John", "last_name": "Doe",
            "email": "john@skybound.com", "role": "customer"
        }
        self._build_ui()
        self._load_data()

    # ── Build ────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 1. Nav Bar
        root.addWidget(self._build_navbar())

        # 2. Scrollable body
        scroll = QScrollArea()
        scroll.setObjectName("MainAreaScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        body = QWidget()
        body.setObjectName("MainAreaWidget")
        body_lay = QVBoxLayout(body)
        body_lay.setContentsMargins(0, 0, 0, 0)
        body_lay.setSpacing(0)

        # 3. Hero Banner
        body_lay.addWidget(self._build_hero())

        # 4. Stats row
        stats_wrap = QWidget()
        stats_wrap.setObjectName("StatsWrap")
        stats_lay = QHBoxLayout(stats_wrap)
        stats_lay.setContentsMargins(60, 28, 60, 28)
        stats_lay.setSpacing(20)

        self.card_dest     = StatCard("Total Destinations", "284",     "📈", "#3B82F6")
        self.card_bookings = StatCard("Active Bookings",    "1,284",   "🛡️", "#10B981")
        self.card_rating   = StatCard("User Rating",        "4.9 / 5", "⚡", "#F59E0B")

        for c in (self.card_dest, self.card_bookings, self.card_rating):
            stats_lay.addWidget(c)

        body_lay.addWidget(stats_wrap)

        # 5. Recent Bookings Table (below the fold)
        body_lay.addWidget(self._build_table_section())
        body_lay.addStretch()

        scroll.setWidget(body)
        root.addWidget(scroll)

    # ── NavBar ───────────────────────────────────────────────
    def _build_navbar(self) -> QFrame:
        nav = QFrame()
        nav.setObjectName("NavBar")
        nav.setFixedHeight(62)

        lay = QHBoxLayout(nav)
        lay.setContentsMargins(32, 0, 32, 0)
        lay.setSpacing(0)

        # Logo
        logo_icon = QLabel("▲")
        logo_icon.setObjectName("NavLogoIcon")

        brand = QLabel()
        brand.setObjectName("NavBrand")
        brand.setText(
            '<span style="color:#111111;font-weight:700;font-size:16px;">SkyBound</span>'
            '<span style="color:#2563EB;font-weight:700;font-size:16px;">Air</span>'
        )
        brand.setTextFormat(Qt.RichText)

        logo_lay = QHBoxLayout()
        logo_lay.setSpacing(6)
        logo_lay.addWidget(logo_icon)
        logo_lay.addWidget(brand)
        lay.addLayout(logo_lay)

        lay.addSpacing(36)

        # Nav links
        nav_items = ["Home", "Flights", "Status", "Check-in", "Manage"]
        self.nav_btns: dict[str, QPushButton] = {}
        for i, name in enumerate(nav_items):
            btn = QPushButton(name)
            btn.setObjectName("NavBtnActive" if i == 0 else "NavBtn")
            btn.setCursor(Qt.PointingHandCursor)
            lay.addWidget(btn)
            self.nav_btns[name] = btn

        lay.addStretch()

        # Right icons + avatar
        for icon in ("🔔", "⊞"):
            b = QPushButton(icon)
            b.setObjectName("NavIconBtn")
            lay.addWidget(b)
            lay.addSpacing(2)

        initials = (
            self.user_info.get("first_name", "J")[0] +
            self.user_info.get("last_name", "D")[0]
        ).upper()
        avatar = QLabel(initials)
        avatar.setObjectName("NavAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        lay.addSpacing(6)
        lay.addWidget(avatar)

        return nav

    # ── Hero Banner ──────────────────────────────────────────
    def _build_hero(self) -> QFrame:
        hero = QFrame()
        hero.setObjectName("HeroBanner")
        hero.setFixedHeight(590)

        lay = QVBoxLayout(hero)
        lay.setContentsMargins(64, 48, 64, 40)
        lay.setSpacing(0)

        # Headline
        lbl_enjoy = QLabel("Enjoy Festive")
        lbl_enjoy.setObjectName("HeroTitle")

        sky_row = QHBoxLayout()
        sky_row.setSpacing(14)
        sky_row.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_sky = QLabel("Sky-high")
        lbl_sky.setObjectName("HeroTitleAccent")
        lbl_savings = QLabel("Savings")
        lbl_savings.setObjectName("HeroTitle")
        sky_row.addWidget(lbl_sky)
        sky_row.addWidget(lbl_savings)
        sky_row.addStretch()

        lbl_sub = QLabel("World's leading low-cost airline. Fly more, pay less!")
        lbl_sub.setObjectName("HeroSubtitle")

        lay.addWidget(lbl_enjoy)
        lay.addLayout(sky_row)
        lay.addSpacing(12)
        lay.addWidget(lbl_sub)
        lay.addSpacing(36)

        # Search Card
        lay.addWidget(self._build_search_card())
        lay.addStretch()

        return hero

    # ── Search Card ──────────────────────────────────────────
    def _build_search_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("SearchCard")

        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 20)
        lay.setSpacing(0)

        # ── Tab row ──
        tab_row = QHBoxLayout()
        tab_row.setContentsMargins(0, 0, 0, 0)
        tab_row.setSpacing(0)
        tab_row.setAlignment(Qt.AlignLeft)

        self.tab_book    = QPushButton("🔍  Book Flight")
        self.tab_checkin = QPushButton("🎫  Check-in")
        self.tab_status  = QPushButton("✈   Flight Status")

        self.tab_book.setObjectName("SearchTabActive")
        self.tab_checkin.setObjectName("SearchTab")
        self.tab_status.setObjectName("SearchTab")

        for btn in (self.tab_book, self.tab_checkin, self.tab_status):
            btn.setCursor(Qt.PointingHandCursor)
            tab_row.addWidget(btn)

        lay.addLayout(tab_row)

        # ── Inner card body ──
        inner = QFrame()
        inner.setObjectName("SearchInner")
        inner_lay = QVBoxLayout(inner)
        inner_lay.setContentsMargins(24, 16, 24, 0)
        inner_lay.setSpacing(14)

        # Trip type + class
        opts_row = QHBoxLayout()
        opts_row.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.rb_round = QRadioButton("Round trip")
        self.rb_round.setObjectName("TripRadio")
        self.rb_round.setChecked(True)

        self.rb_one = QRadioButton("One way")
        self.rb_one.setObjectName("TripRadio")

        grp = QButtonGroup(self)
        grp.addButton(self.rb_round)
        grp.addButton(self.rb_one)

        opts_row.addWidget(self.rb_round)
        opts_row.addSpacing(20)
        opts_row.addWidget(self.rb_one)
        opts_row.addStretch()

        class_lbl = QLabel("CLASS:")
        class_lbl.setObjectName("ClassLabel")

        self.combo_class = QComboBox()
        self.combo_class.setObjectName("ClassCombo")
        self.combo_class.addItems(["Eco", "Business", "First Class"])
        self.combo_class.setFixedWidth(130)

        opts_row.addWidget(class_lbl)
        opts_row.addSpacing(6)
        opts_row.addWidget(self.combo_class)

        inner_lay.addLayout(opts_row)

        # ── Inputs row ──
        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(10)

        def _field(label_text: str, widget: QWidget) -> QVBoxLayout:
            col = QVBoxLayout()
            col.setSpacing(4)
            lbl = QLabel(label_text)
            lbl.setObjectName("FieldLabel")
            col.addWidget(lbl)
            col.addWidget(widget)
            return col

        self.combo_from = QComboBox()
        self.combo_from.setObjectName("HeroCombo")
        self.combo_from.setMinimumWidth(190)

        self.combo_to = QComboBox()
        self.combo_to.setObjectName("HeroCombo")
        self.combo_to.setMinimumWidth(190)

        self.input_date = QLineEdit()
        self.input_date.setObjectName("HeroInput")
        self.input_date.setText(datetime.date.today().strftime("%m/%d/%Y"))
        self.input_date.setMinimumWidth(160)

        btn_search = QPushButton("🔍  Search Flights")
        btn_search.setObjectName("HeroSearchBtn")
        btn_search.setFixedHeight(52)
        btn_search.setCursor(Qt.PointingHandCursor)
        btn_search.clicked.connect(self._on_search)

        inputs_row.addLayout(_field("FROM",      self.combo_from),  stretch=3)
        inputs_row.addLayout(_field("TO",        self.combo_to),    stretch=3)
        inputs_row.addLayout(_field("DEPARTURE", self.input_date),  stretch=2)
        inputs_row.addWidget(btn_search, stretch=2, alignment=Qt.AlignBottom)

        inner_lay.addLayout(inputs_row)
        lay.addWidget(inner)

        return card

    # ── Recent Bookings Table ────────────────────────────────
    def _build_table_section(self) -> QFrame:
        section = QFrame()
        section.setObjectName("TableCard")

        lay = QVBoxLayout(section)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(14)

        title = QLabel("Các chuyến bay đã đặt gần đây")
        title.setObjectName("SectionTitle")
        lay.addWidget(title)

        self.table_bookings = QTableWidget()
        self.table_bookings.setObjectName("BookingsTable")
        self.table_bookings.setColumnCount(6)
        self.table_bookings.setHorizontalHeaderLabels([
            "Mã đặt chỗ", "Chuyến bay", "Điểm khởi hành",
            "Điểm đến", "Thời gian bay", "Trạng thái"
        ])
        self.table_bookings.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_bookings.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_bookings.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_bookings.verticalHeader().setVisible(False)
        self.table_bookings.setFixedHeight(230)

        lay.addWidget(self.table_bookings)
        return section

    # ── Data ────────────────────────────────────────────────
    def _load_data(self):
        airports = []
        if fetchall:
            try:
                rows = fetchall("SELECT code, city FROM airports ORDER BY city ASC")
                airports = [f"{r['city']} ({r['code']})" for r in rows]
            except Exception as e:
                print(f"Lỗi tải airports: {e}")

        if not airports:
            airports = [
                "Ho Chi Minh (SGN)", "Hanoi (HAN)",
                "Da Nang (DAD)", "Phu Quoc (PQC)", "Nha Trang (CXR)"
            ]

        self.combo_from.addItems(airports)
        self.combo_to.addItems(airports)
        if len(airports) > 1:
            self.combo_to.setCurrentIndex(1)

        # Mock bookings
        if fetchall and self.user_info.get("id"):
            try:
                rows = fetchall("""
                    SELECT b.id, b.booking_code, f.flight_number,
                           a1.city as origin, a2.city as destination,
                           f.departure_time, b.status
                    FROM bookings b
                    JOIN flights f   ON f.id  = b.flight_id
                    JOIN airports a1 ON a1.id = f.origin_id
                    JOIN airports a2 ON a2.id = f.destination_id
                    WHERE b.user_id = ?
                    ORDER BY b.booked_at DESC LIMIT 5
                """, (self.user_info["id"],))
                for r in rows:
                    self._insert_row(
                        f"BK-{r['id']:04d}", str(r['flight_number']),
                        str(r['origin']), str(r['destination']),
                        str(r['departure_time']), str(r['status'])
                    )
            except Exception as e:
                print(f"Lỗi tải bookings: {e}")
                self._insert_mock()
        else:
            self._insert_mock()

    def _insert_mock(self):
        self._insert_row("BK-0012", "SB-102", "Hà Nội",    "Hồ Chí Minh", "2026-05-15 08:30", "Confirmed")
        self._insert_row("BK-0034", "SB-501", "Hà Nội",    "Đà Nẵng",     "2026-05-22 14:15", "Pending")
        self._insert_row("BK-0056", "SB-207", "Đà Nẵng",   "Phú Quốc",    "2026-06-03 09:00", "Confirmed")

    def _insert_row(self, code, flight, fr, to, time, status):
        idx = self.table_bookings.rowCount()
        self.table_bookings.insertRow(idx)
        for col, val in enumerate([code, flight, fr, to, time, status]):
            item = QTableWidgetItem(val)
            if col == 5:
                item.setForeground(
                    QColor("#10B981") if status.lower() == "confirmed"
                    else QColor("#F59E0B")
                )
            self.table_bookings.setItem(idx, col, item)

    def _on_search(self):
        f = self.combo_from.currentText()
        t = self.combo_to.currentText()
        self.search_triggered.emit({
            "from_code": f.split('(')[-1].replace(')', '') if '(' in f else f,
            "to_code":   t.split('(')[-1].replace(')', '') if '(' in t else t,
            "date":      self.input_date.text().strip(),
        })


# ── Standalone test ──────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    try:
        with open("assets/styles/style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    win = DashboardWidget()
    win.resize(1280, 860)
    win.show()
    sys.exit(app.exec())