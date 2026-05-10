"""
ui/main/flight_ui.py
Trang danh sách chuyến bay — SkyBoundAir
Thiết kế: NavBar + Header xanh + FilterPanel trái + FlightCard phải
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QButtonGroup,
    QRadioButton, QSlider, QComboBox,
)
from PySide6.QtGui import QFont, QColor, QPainter, QPen
from PySide6.QtCore import Qt, Signal, QSize

try:
    from database.db import fetchall
except ImportError:
    fetchall = None


# ─────────────────────────────────────────────────────────────
#  Route Line (đường kẻ 2 chấm tròn)
# ─────────────────────────────────────────────────────────────
class _RouteLine(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(16)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#CBD5E1"), 1.5)
        p.setPen(pen)
        p.setBrush(QColor("#CBD5E1"))
        h = self.height() // 2
        w = self.width()
        r = 4
        p.drawEllipse(0, h - r, r * 2, r * 2)
        p.drawLine(r * 2, h, w - r * 2, h)
        p.drawEllipse(w - r * 2, h - r, r * 2, r * 2)
        p.end()


# ─────────────────────────────────────────────────────────────
#  Price Button (ECO / DELUXE / SKYBOSS)
# ─────────────────────────────────────────────────────────────
class PriceButton(QPushButton):
    _STYLES = {
        "ECO": {
            "bg": "#DCFCE7", "hover": "#BBF7D0",
            "tier_color": "#166534", "price_color": "#15803D",
        },
        "DELUXE": {
            "bg": "#FEF3C7", "hover": "#FDE68A",
            "tier_color": "#92400E", "price_color": "#B45309",
        },
        "SKYBOSS": {
            "bg": "#1E293B", "hover": "#334155",
            "tier_color": "#94A3B8", "price_color": "#FFFFFF",
        },
    }

    def __init__(self, tier: str, price: str, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(QSize(92, 68))

        s = self._STYLES.get(tier, self._STYLES["ECO"])

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 8, 6, 8)
        lay.setSpacing(3)
        lay.setAlignment(Qt.AlignCenter)

        tier_lbl = QLabel(tier)
        tier_lbl.setAlignment(Qt.AlignCenter)
        tier_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        tier_lbl.setStyleSheet(
            f"color: {s['tier_color']}; background: transparent;"
        )

        price_lbl = QLabel(price)
        price_lbl.setAlignment(Qt.AlignCenter)
        price_lbl.setFont(QFont("Segoe UI", 14, QFont.Bold))
        price_lbl.setStyleSheet(
            f"color: {s['price_color']}; background: transparent;"
        )

        lay.addWidget(tier_lbl)
        lay.addWidget(price_lbl)

        self.setStyleSheet(
            f"QPushButton {{ background-color: {s['bg']}; border-radius: 10px; border: none; }}"
            f"QPushButton:hover {{ background-color: {s['hover']}; }}"
            f"QPushButton:pressed {{ background-color: {s['hover']}; }}"
        )


# ─────────────────────────────────────────────────────────────
#  Flight Card
# ─────────────────────────────────────────────────────────────
class FlightCard(QFrame):
    book_clicked = Signal(dict)

    def __init__(self, flight: dict, parent=None):
        super().__init__(parent)
        self.flight = flight
        self.setObjectName("FlightCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(108)
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 0, 20, 0)
        root.setSpacing(0)

        # ── Plane icon bubble ──────────────────────────────────
        icon_wrap = QFrame()
        icon_wrap.setFixedSize(44, 44)
        icon_wrap.setStyleSheet(
            "QFrame { background-color: #EFF6FF; border-radius: 22px; border: none; }"
        )
        icon_lay = QHBoxLayout(icon_wrap)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        plane = QLabel("✈")
        plane.setFont(QFont("Segoe UI Emoji", 16))
        plane.setAlignment(Qt.AlignCenter)
        plane.setStyleSheet("color: #2563EB; background: transparent;")
        icon_lay.addWidget(plane)
        root.addWidget(icon_wrap, alignment=Qt.AlignVCenter)
        root.addSpacing(14)

        # ── Airline name + flight number ───────────────────────
        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        info_col.setAlignment(Qt.AlignVCenter)

        airline_lbl = QLabel(self.flight.get("airline", "SkyBound Air").upper())
        airline_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))
        airline_lbl.setStyleSheet("color: #94A3B8;")

        fn_lbl = QLabel(self.flight.get("flight_number", "SBA001"))
        fn_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        fn_lbl.setStyleSheet("color: #0F172A;")

        info_col.addWidget(airline_lbl)
        info_col.addWidget(fn_lbl)

        info_w = QWidget()
        info_w.setFixedWidth(120)
        info_w.setLayout(info_col)
        root.addWidget(info_w)

        # ── Departure time & code ──────────────────────────────
        root.addWidget(self._time_col(
            self._hhmm(self.flight.get("departure_time", "09:00")),
            self.flight.get("origin_code", "---")
        ))
        root.addSpacing(8)

        # ── Route: duration + line + stops ────────────────────
        root.addWidget(self._route_col(
            self.flight.get("duration", "2h 0m"),
            self.flight.get("stops", "NON-STOP"),
        ), stretch=1)
        root.addSpacing(8)

        # ── Arrival time & code ────────────────────────────────
        root.addWidget(self._time_col(
            self._hhmm(self.flight.get("arrival_time", "11:00")),
            self.flight.get("dest_code", "---")
        ))
        root.addSpacing(24)

        # ── Price buttons ──────────────────────────────────────
        eco  = self.flight.get("price_eco", 0)
        dlx  = self.flight.get("price_business", 0)
        boss = int(dlx * 1.56)

        btn_eco  = PriceButton("ECO",     self._fmt(eco))
        btn_dlx  = PriceButton("DELUXE",  self._fmt(dlx))
        btn_boss = PriceButton("SKYBOSS", self._fmt(boss))

        btn_eco.clicked.connect( lambda: self.book_clicked.emit({**self.flight, "class": "eco"}))
        btn_dlx.clicked.connect( lambda: self.book_clicked.emit({**self.flight, "class": "business"}))
        btn_boss.clicked.connect(lambda: self.book_clicked.emit({**self.flight, "class": "skyboss"}))

        price_row = QHBoxLayout()
        price_row.setSpacing(6)
        for b in (btn_eco, btn_dlx, btn_boss):
            price_row.addWidget(b)

        price_w = QWidget()
        price_w.setLayout(price_row)
        root.addWidget(price_w, alignment=Qt.AlignVCenter)

    # ── Helpers ──────────────────────────────────────────────
    @staticmethod
    def _hhmm(t: str) -> str:
        """Trả về HH:MM từ chuỗi datetime hoặc time."""
        return t[-5:] if len(t) >= 5 else t

    @staticmethod
    def _fmt(price) -> str:
        """Format: 95 → $95 | 1190 → $1190"""
        return f"${int(price):,}"

    def _time_col(self, time_str: str, code: str) -> QWidget:
        w = QWidget()
        w.setFixedWidth(72)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        lay.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        t = QLabel(time_str)
        t.setFont(QFont("Segoe UI", 18, QFont.Bold))
        t.setStyleSheet("color: #0F172A;")
        t.setAlignment(Qt.AlignCenter)

        c = QLabel(code)
        c.setFont(QFont("Segoe UI", 11))
        c.setStyleSheet("color: #64748B;")
        c.setAlignment(Qt.AlignCenter)

        lay.addWidget(t)
        lay.addWidget(c)
        return w

    def _route_col(self, duration: str, stops: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(10, 0, 10, 0)
        lay.setSpacing(4)
        lay.setAlignment(Qt.AlignVCenter)

        dur = QLabel(duration)
        dur.setFont(QFont("Segoe UI", 10))
        dur.setStyleSheet("color: #64748B;")
        dur.setAlignment(Qt.AlignCenter)

        line = _RouteLine()

        stop_color = "#16A34A" if stops == "NON-STOP" else "#EF4444"
        stp = QLabel(stops)
        stp.setFont(QFont("Segoe UI", 9, QFont.Bold))
        stp.setStyleSheet(f"color: {stop_color};")
        stp.setAlignment(Qt.AlignCenter)

        lay.addWidget(dur)
        lay.addWidget(line)
        lay.addWidget(stp)
        return w


# ─────────────────────────────────────────────────────────────
#  Filter Panel
# ─────────────────────────────────────────────────────────────
class FilterPanel(QFrame):
    filter_changed = Signal(dict)

    # Mock airlines theo ảnh
    DEFAULT_AIRLINES = [
        "SkyFlow Airlines",
        "Oceanic Airways",
        "Global Wings",
        "Emerald Air",
    ]

    def __init__(self, airlines: list[str] = None, parent=None):
        super().__init__(parent)
        self.setObjectName("FilterPanel")
        self.setFixedWidth(300)
        self._airlines = airlines or self.DEFAULT_AIRLINES
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(0)

        # ── Header ──────────────────────────────────────────────
        hdr = QHBoxLayout()
        title = QLabel("FILTERS")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color: #0F172A;")

        filter_icon = QLabel("⚙")
        filter_icon.setFont(QFont("Segoe UI Emoji", 15))
        filter_icon.setStyleSheet("color: #2563EB;")

        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(filter_icon)
        lay.addLayout(hdr)
        lay.addSpacing(24)

        # ── Airlines ─────────────────────────────────────────────
        al_lbl = QLabel("AIRLINES")
        al_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        al_lbl.setStyleSheet("color: #94A3B8;")
        lay.addWidget(al_lbl)
        lay.addSpacing(10)

        self._airline_group = QButtonGroup(self)
        self._airline_group.setExclusive(True)

        all_airlines = ["All"] + self._airlines
        self._airline_counts: list[QLabel] = []

        for i, name in enumerate(all_airlines):
            row = QHBoxLayout()
            row.setSpacing(0)

            rb = QRadioButton(name)
            rb.setFont(QFont("Segoe UI", 12))
            rb.setStyleSheet(
                "QRadioButton { color: #334155; spacing: 10px; }"
                "QRadioButton::indicator { width: 16px; height: 16px;"
                "  border-radius: 8px; border: 2px solid #CBD5E1; background: white; }"
                "QRadioButton::indicator:checked { border: 2px solid #2563EB; background: #2563EB; }"
            )
            if i == 0:
                rb.setChecked(True)

            cnt = QLabel("12")
            cnt.setFont(QFont("Segoe UI", 11))
            cnt.setStyleSheet("color: #94A3B8;")
            cnt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._airline_counts.append(cnt)

            self._airline_group.addButton(rb, i)
            row.addWidget(rb, stretch=1)
            row.addWidget(cnt)

            row_w = QWidget()
            row_w.setFixedHeight(36)
            row_w.setLayout(row)
            lay.addWidget(row_w)

        self._airline_group.buttonClicked.connect(self._emit)
        lay.addSpacing(28)

        # ── Price Range ───────────────────────────────────────────
        pr_header = QHBoxLayout()
        pr_lbl = QLabel("PRICE RANGE")
        pr_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        pr_lbl.setStyleSheet("color: #94A3B8;")

        self._price_val = QLabel("$2000")
        self._price_val.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._price_val.setStyleSheet("color: #2563EB;")
        self._price_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        pr_header.addWidget(pr_lbl)
        pr_header.addStretch()
        pr_header.addWidget(self._price_val)
        lay.addLayout(pr_header)
        lay.addSpacing(12)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(100, 3000)
        self._slider.setValue(2000)
        self._slider.setStyleSheet(
            "QSlider::groove:horizontal { height: 4px; background: #E2E8F0; border-radius: 2px; }"
            "QSlider::sub-page:horizontal { background: #2563EB; border-radius: 2px; }"
            "QSlider::handle:horizontal { background: #2563EB; width: 18px; height: 18px;"
            "  margin: -7px 0; border-radius: 9px; border: 2px solid #FFFFFF; }"
        )
        self._slider.valueChanged.connect(self._on_price_changed)
        lay.addWidget(self._slider)
        lay.addSpacing(6)

        minmax = QHBoxLayout()
        for txt, align in [("$100", Qt.AlignLeft), ("MAX", Qt.AlignRight)]:
            lbl = QLabel(txt)
            lbl.setFont(QFont("Segoe UI", 9))
            lbl.setStyleSheet("color: #94A3B8;")
            lbl.setAlignment(align)
            minmax.addWidget(lbl)
        lay.addLayout(minmax)

        lay.addStretch()

    def _on_price_changed(self, val: int):
        self._price_val.setText(f"${val:,}")
        self._emit()

    def _emit(self):
        checked = self._airline_group.checkedButton()
        self.filter_changed.emit({
            "airline":   checked.text() if checked else "All",
            "max_price": self._slider.value(),
        })


# ─────────────────────────────────────────────────────────────
#  Flight Widget (trang chính)
# ─────────────────────────────────────────────────────────────
class FlightWidget(QWidget):
    book_clicked = Signal(dict)
    nav_home     = Signal()   # quay về dashboard

    def __init__(self, search_params: dict = None,
                 user_info: dict = None, parent=None):
        super().__init__(parent)
        self.setObjectName("FlightPage")
        self.search_params = search_params or {}
        self.user_info = user_info or {
            "first_name": "John", "last_name": "Doe"
        }
        self._all_flights: list[dict] = []
        self._build_ui()
        self._load_flights()

    # ── UI ───────────────────────────────────────────────────
    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # 1. NavBar
        root.addWidget(self._build_navbar())

        # 2. Route header (xanh)
        self._header_frame = self._build_header()
        root.addWidget(self._header_frame)

        # 3. Body = FilterPanel trái + danh sách phải
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        self._filter = FilterPanel(airlines=[], parent=self)
        self._filter.filter_changed.connect(self._apply_filters)
        body.addWidget(self._filter)

        # Right area
        right = QVBoxLayout()
        right.setContentsMargins(24, 20, 24, 20)
        right.setSpacing(14)

        # Result count + sort bar
        bar = QHBoxLayout()

        self._result_lbl = QLabel("Đang tải...")
        self._result_lbl.setFont(QFont("Segoe UI", 13))
        self._result_lbl.setStyleSheet("color: #64748B;")

        sort_lbl = QLabel("SORT BY:")
        sort_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        sort_lbl.setStyleSheet("color: #64748B;")

        self._sort_combo = QComboBox()
        self._sort_combo.addItems([
            "Cheapest First", "Fastest First",
            "Departure ↑",    "Departure ↓",
        ])
        self._sort_combo.setFixedHeight(40)
        self._sort_combo.setStyleSheet(
            "QComboBox { border: 1px solid #E2E8F0; border-radius: 10px;"
            "  padding: 4px 14px; font-size: 13px; font-weight: bold;"
            "  color: #2563EB; background: #EFF6FF; min-width: 170px; }"
            "QComboBox::drop-down { border: none; width: 24px; }"
            "QComboBox QAbstractItemView { border: 1px solid #E2E8F0; }"
        )
        self._sort_combo.currentIndexChanged.connect(self._apply_filters)

        bar.addWidget(self._result_lbl)
        bar.addStretch()
        bar.addWidget(sort_lbl)
        bar.addSpacing(8)
        bar.addWidget(self._sort_combo)
        right.addLayout(bar)

        # Cards scroll
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
        )

        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet("background: transparent;")
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(12)
        self._cards_layout.addStretch()

        self._scroll.setWidget(self._cards_widget)
        right.addWidget(self._scroll)

        right_w = QWidget()
        right_w.setStyleSheet("background-color: #F1F5F9;")
        right_w.setLayout(right)
        body.addWidget(right_w, stretch=1)

        body_w = QWidget()
        body_w.setLayout(body)
        root.addWidget(body_w, stretch=1)

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

        # Nav links — "Flights" active
        for name in ["Home", "Flights", "Status", "Check-in", "Manage"]:
            btn = QPushButton(name)
            is_active = name == "Flights"
            btn.setObjectName("NavBtnActive" if is_active else "NavBtn")
            btn.setCursor(Qt.PointingHandCursor)
            if name == "Home":
                btn.clicked.connect(self.nav_home.emit)
            lay.addWidget(btn)

        lay.addStretch()

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

    # ── Header xanh ─────────────────────────────────────────
    def _build_header(self) -> QFrame:
        hdr = QFrame()
        hdr.setObjectName("FlightHeader")
        hdr.setFixedHeight(90)
        hdr.setStyleSheet(
            "QFrame#FlightHeader { background-color: #1a2c6e; border: none; }"
        )

        lay = QHBoxLayout(hdr)
        lay.setContentsMargins(32, 0, 32, 0)
        lay.setSpacing(0)

        origin = self.search_params.get("from_code", "Anywhere")
        dest   = self.search_params.get("to_code",   "Anywhere")

        self._lbl_from = QLabel(origin)
        self._lbl_from.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self._lbl_from.setStyleSheet("color: #FFFFFF; background: transparent;")

        arrow = QLabel("  ✈  ")
        arrow.setFont(QFont("Segoe UI Emoji", 18))
        arrow.setStyleSheet("color: #60A5FA; background: transparent;")

        self._lbl_to = QLabel(dest)
        self._lbl_to.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self._lbl_to.setStyleSheet("color: #FFFFFF; background: transparent;")

        btn_modify = QPushButton("  🔍  Modify Search")
        btn_modify.setFixedHeight(42)
        btn_modify.setFont(QFont("Segoe UI", 12))
        btn_modify.setCursor(Qt.PointingHandCursor)
        btn_modify.setStyleSheet(
            "QPushButton { background-color: rgba(255,255,255,35);"
            "  color: #FFFFFF; border: 1px solid rgba(255,255,255,90);"
            "  border-radius: 10px; padding: 0 20px; font-weight: bold; }"
            "QPushButton:hover { background-color: rgba(255,255,255,55); }"
            "QPushButton:pressed { background-color: rgba(255,255,255,20); }"
        )

        lay.addWidget(self._lbl_from)
        lay.addWidget(arrow)
        lay.addWidget(self._lbl_to)
        lay.addStretch()
        lay.addWidget(btn_modify)

        return hdr

    # ── Data ─────────────────────────────────────────────────
    def _load_flights(self):
        if fetchall:
            try:
                origin = self.search_params.get("from_code", "")
                dest   = self.search_params.get("to_code", "")
                date   = self.search_params.get("date", "")

                sql = """
                    SELECT f.id, f.flight_number, f.departure_time, f.arrival_time,
                           f.price_eco, f.price_business, f.status,
                           a1.code AS origin_code, a1.city AS origin_city,
                           a2.code AS dest_code,   a2.city AS dest_city,
                           ac.model AS airline
                    FROM flights f
                    JOIN airports a1 ON a1.id = f.origin_id
                    JOIN airports a2 ON a2.id = f.destination_id
                    JOIN aircraft  ac ON ac.id  = f.aircraft_id
                    WHERE f.status != 'cancelled'
                """
                params = []
                if origin:
                    sql += " AND a1.code = ?"
                    params.append(origin)
                if dest:
                    sql += " AND a2.code = ?"
                    params.append(dest)
                if date:
                    sql += " AND f.departure_time LIKE ?"
                    params.append(f"{date}%")
                sql += " ORDER BY f.price_eco ASC"

                rows = fetchall(sql, tuple(params))
                self._all_flights = [self._row_to_flight(r) for r in rows]
            except Exception as e:
                print(f"[FlightWidget] DB error: {e}")
                self._all_flights = self._mock_flights()
        else:
            self._all_flights = self._mock_flights()

        airlines = sorted({f["airline"] for f in self._all_flights})
        self._filter._airlines = airlines
        self._apply_filters()

    def _row_to_flight(self, row) -> dict:
        dep = str(row["departure_time"])
        arr = str(row["arrival_time"])
        try:
            from datetime import datetime
            d1 = datetime.strptime(dep, "%Y-%m-%d %H:%M")
            d2 = datetime.strptime(arr, "%Y-%m-%d %H:%M")
            diff = d2 - d1
            h, m = divmod(diff.seconds // 60, 60)
            duration = f"{h}h {m}m"
        except Exception:
            duration = "--"

        return {
            "id":             row["id"],
            "flight_number":  row["flight_number"],
            "airline":        row["airline"],
            "departure_time": dep,
            "arrival_time":   arr,
            "origin_code":    row["origin_code"],
            "origin_city":    row["origin_city"],
            "dest_code":      row["dest_code"],
            "dest_city":      row["dest_city"],
            "price_eco":      row["price_eco"],
            "price_business": row["price_business"],
            "status":         row["status"],
            "duration":       duration,
            "stops":          "NON-STOP",
        }

    @staticmethod
    def _mock_flights() -> list[dict]:
        """Dữ liệu mẫu giống ảnh mockup."""
        return [
            {
                "id": 1, "flight_number": "SF104",
                "airline": "SkyFlow Airlines",
                "departure_time": "09:00", "arrival_time": "10:30",
                "origin_code": "CDG", "dest_code": "LHR",
                "price_eco": 95, "price_business": 133,
                "duration": "1h 30m", "stops": "NON-STOP", "status": "scheduled",
            },
            {
                "id": 2, "flight_number": "OA202",
                "airline": "Oceanic Airways",
                "departure_time": "08:30", "arrival_time": "10:30",
                "origin_code": "LHR", "dest_code": "CDG",
                "price_eco": 120, "price_business": 168,
                "duration": "2h 0m", "stops": "NON-STOP", "status": "scheduled",
            },
            {
                "id": 3, "flight_number": "EA505",
                "airline": "Emerald Air",
                "departure_time": "11:00", "arrival_time": "15:00",
                "origin_code": "DUB", "dest_code": "FCO",
                "price_eco": 180, "price_business": 252,
                "duration": "3h 0m", "stops": "NON-STOP", "status": "scheduled",
            },
            {
                "id": 4, "flight_number": "SF101",
                "airline": "SkyFlow Airlines",
                "departure_time": "10:00", "arrival_time": "13:00",
                "origin_code": "LHR", "dest_code": "JFK",
                "price_eco": 450, "price_business": 630,
                "duration": "8h 0m", "stops": "NON-STOP", "status": "scheduled",
            },
            {
                "id": 5, "flight_number": "GW303",
                "airline": "Global Wings",
                "departure_time": "15:00", "arrival_time": "18:00",
                "origin_code": "JFK", "dest_code": "NRT",
                "price_eco": 850, "price_business": 1190,
                "duration": "14h 0m", "stops": "1STOP", "status": "scheduled",
            },
        ]

    # ── Filters & Sort ───────────────────────────────────────
    def _apply_filters(self):
        checked = self._airline_group_checked()
        max_price = self._filter._slider.value()
        sort_idx  = self._sort_combo.currentIndex()

        flights = [
            f for f in self._all_flights
            if (checked == "All" or f["airline"] == checked)
            and f["price_eco"] <= max_price
        ]

        key_map = {
            0: lambda f: f["price_eco"],
            1: lambda f: f.get("duration", "99h"),
            2: lambda f: f["departure_time"],
            3: lambda f: f["departure_time"],
        }
        reverse = sort_idx == 3
        flights.sort(key=key_map.get(sort_idx, key_map[0]), reverse=reverse)

        self._render_cards(flights)

    def _airline_group_checked(self) -> str:
        btn = self._filter._airline_group.checkedButton()
        return btn.text() if btn else "All"

    def _render_cards(self, flights: list[dict]):
        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        count = len(flights)
        self._result_lbl.setText(
            f"Showing <b>{count}</b> flight{'s' if count != 1 else ''}"
        )

        for f in flights:
            card = FlightCard(f, self)
            card.book_clicked.connect(self.book_clicked)
            self._cards_layout.insertWidget(
                self._cards_layout.count() - 1, card
            )

    def update_search(self, params: dict):
        """Nhận params từ dashboard → cập nhật header + reload."""
        self.search_params = params
        origin = params.get("from_code", "Anywhere")
        dest   = params.get("to_code",   "Anywhere")
        if hasattr(self, "_lbl_from"):
            self._lbl_from.setText(origin)
            self._lbl_to.setText(dest)
        self._load_flights()


# ─────────────────────────────────────────────────────────────
#  Standalone test
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    try:
        with open("assets/styles/style.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    win = FlightWidget(
        search_params={"from_code": "Anywhere", "to_code": "Anywhere"},
        user_info={"first_name": "John", "last_name": "Doe"},
    )
    win.resize(1280, 860)
    win.show()
    sys.exit(app.exec())