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
#  Route Line
# ─────────────────────────────────────────────────────────────
class _RouteLine(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(16)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(QPen(QColor("#CBD5E1"), 1.5))
        p.setBrush(QColor("#CBD5E1"))
        h, w, r = self.height() // 2, self.width(), 4
        p.drawEllipse(0, h - r, r * 2, r * 2)
        p.drawLine(r * 2, h, w - r * 2, h)
        p.drawEllipse(w - r * 2, h - r, r * 2, r * 2)
        p.end()


# ─────────────────────────────────────────────────────────────
#  Price Button
# ─────────────────────────────────────────────────────────────
class PriceButton(QPushButton):
    _STYLES = {
        "ECO":     {"bg": "#DCFCE7", "hv": "#BBF7D0", "tc": "#166534", "pc": "#15803D"},
        "DELUXE":  {"bg": "#FEF3C7", "hv": "#FDE68A", "tc": "#92400E", "pc": "#B45309"},
        "SKYBOSS": {"bg": "#1E293B", "hv": "#334155", "tc": "#94A3B8", "pc": "#FFFFFF"},
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

        t = QLabel(tier)
        t.setAlignment(Qt.AlignCenter)
        t.setFont(QFont("Segoe UI", 8, QFont.Bold))
        t.setStyleSheet(f"color:{s['tc']};background:transparent;")

        p_lbl = QLabel(price)
        p_lbl.setAlignment(Qt.AlignCenter)
        p_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        p_lbl.setStyleSheet(f"color:{s['pc']};background:transparent;")

        lay.addWidget(t)
        lay.addWidget(p_lbl)

        self.setStyleSheet(
            f"QPushButton{{background-color:{s['bg']};border-radius:10px;border:none;}}"
            f"QPushButton:hover{{background-color:{s['hv']};}}"
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

        # Icon bubble
        bubble = QFrame()
        bubble.setFixedSize(44, 44)
        bubble.setStyleSheet(
            "QFrame{background-color:#EFF6FF;border-radius:22px;border:none;}"
        )
        blay = QHBoxLayout(bubble)
        blay.setContentsMargins(0, 0, 0, 0)
        ico = QLabel("✈")
        ico.setFont(QFont("Segoe UI Emoji", 15))
        ico.setAlignment(Qt.AlignCenter)
        ico.setStyleSheet("color:#2563EB;background:transparent;")
        blay.addWidget(ico)
        root.addWidget(bubble, alignment=Qt.AlignVCenter)
        root.addSpacing(14)

        # Airline + flight number
        info_lay = QVBoxLayout()
        info_lay.setSpacing(2)
        info_lay.setAlignment(Qt.AlignVCenter)

        al = QLabel(self.flight.get("airline", "").upper())
        al.setFont(QFont("Segoe UI", 8, QFont.Bold))
        al.setStyleSheet("color:#94A3B8;")

        fn = QLabel(self.flight.get("flight_number", "---"))
        fn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        fn.setStyleSheet("color:#0F172A;")

        info_lay.addWidget(al)
        info_lay.addWidget(fn)

        info_w = QWidget()
        info_w.setFixedWidth(130)
        info_w.setLayout(info_lay)
        root.addWidget(info_w)

        # Times & route
        root.addWidget(self._time_col(
            self._hhmm(self.flight.get("departure_time", "--:--")),
            self.flight.get("origin_code", "---")
        ))
        root.addSpacing(6)
        root.addWidget(self._route_col(
            self.flight.get("duration", "--"),
            self.flight.get("stops", "NON-STOP")
        ), stretch=1)
        root.addSpacing(6)
        root.addWidget(self._time_col(
            self._hhmm(self.flight.get("arrival_time", "--:--")),
            self.flight.get("dest_code", "---")
        ))
        root.addSpacing(20)

        # Price buttons
        eco  = self.flight.get("price_eco", 0)
        dlx  = self.flight.get("price_business", 0)
        boss = int(dlx * 1.56)

        btn_e = PriceButton("ECO",     self._fmt(eco))
        btn_d = PriceButton("DELUXE",  self._fmt(dlx))
        btn_b = PriceButton("SKYBOSS", self._fmt(boss))

        btn_e.clicked.connect(lambda: self.book_clicked.emit({**self.flight, "class": "eco"}))
        btn_d.clicked.connect(lambda: self.book_clicked.emit({**self.flight, "class": "business"}))
        btn_b.clicked.connect(lambda: self.book_clicked.emit({**self.flight, "class": "skyboss"}))

        prow = QHBoxLayout()
        prow.setSpacing(6)
        for b in (btn_e, btn_d, btn_b):
            prow.addWidget(b)

        pw = QWidget()
        pw.setLayout(prow)
        root.addWidget(pw, alignment=Qt.AlignVCenter)

    @staticmethod
    def _hhmm(t: str) -> str:
        return t[-5:] if len(t) >= 5 else t

    @staticmethod
    def _fmt(v) -> str:
        v = int(v)
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        if v >= 10_000:
            return f"{v // 1_000}K"
        return f"${v}"

    def _time_col(self, time_str: str, code: str) -> QWidget:
        w = QWidget()
        w.setFixedWidth(74)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        lay.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        t = QLabel(time_str)
        t.setFont(QFont("Segoe UI", 18, QFont.Bold))
        t.setStyleSheet("color:#0F172A;")
        t.setAlignment(Qt.AlignCenter)

        c = QLabel(code)
        c.setFont(QFont("Segoe UI", 11))
        c.setStyleSheet("color:#64748B;")
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
        dur.setStyleSheet("color:#64748B;")
        dur.setAlignment(Qt.AlignCenter)

        stp = QLabel(stops)
        stp.setFont(QFont("Segoe UI", 9, QFont.Bold))
        stp.setStyleSheet(
            f"color:{'#16A34A' if stops == 'NON-STOP' else '#EF4444'};"
        )
        stp.setAlignment(Qt.AlignCenter)

        lay.addWidget(dur)
        lay.addWidget(_RouteLine())
        lay.addWidget(stp)
        return w


# ─────────────────────────────────────────────────────────────
#  Filter Panel
# ─────────────────────────────────────────────────────────────
class FilterPanel(QFrame):
    filter_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FilterPanel")
        self.setFixedWidth(300)
        self._airline_group: QButtonGroup | None = None
        self._slider: QSlider | None = None
        self._price_val: QLabel | None = None
        self._airline_container: QVBoxLayout | None = None
        self._build()

    def _build(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(0)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("FILTERS")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color:#0F172A;")
        icon = QLabel("⚙")
        icon.setFont(QFont("Segoe UI Emoji", 15))
        icon.setStyleSheet("color:#2563EB;")
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(icon)
        main.addLayout(hdr)
        main.addSpacing(24)

        # Airlines section label
        al_lbl = QLabel("AIRLINES")
        al_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        al_lbl.setStyleSheet("color:#94A3B8;")
        main.addWidget(al_lbl)
        main.addSpacing(8)

        # ── Container: rebuild_airlines() fills this ──────────
        self._airline_container_widget = QWidget()
        self._airline_container = QVBoxLayout(self._airline_container_widget)
        self._airline_container.setContentsMargins(0, 0, 0, 0)
        self._airline_container.setSpacing(0)
        main.addWidget(self._airline_container_widget)

        # Khởi tạo group + nút "All" trước
        self._airline_group = QButtonGroup(self)
        self._airline_group.setExclusive(True)
        self._add_radio_row("All", 0, checked=True)
        self._airline_group.buttonClicked.connect(self._emit)

        main.addSpacing(24)

        # Price Range
        ph = QHBoxLayout()
        pr_lbl = QLabel("PRICE RANGE")
        pr_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        pr_lbl.setStyleSheet("color:#94A3B8;")

        self._price_val = QLabel("MAX")
        self._price_val.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._price_val.setStyleSheet("color:#2563EB;")
        self._price_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        ph.addWidget(pr_lbl)
        ph.addStretch()
        ph.addWidget(self._price_val)
        main.addLayout(ph)
        main.addSpacing(10)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 100)   # sẽ được cập nhật bởi set_price_range()
        self._slider.setValue(100)
        self._slider.setStyleSheet(
            "QSlider::groove:horizontal{height:4px;background:#E2E8F0;border-radius:2px;}"
            "QSlider::sub-page:horizontal{background:#2563EB;border-radius:2px;}"
            "QSlider::handle:horizontal{background:#2563EB;width:18px;height:18px;"
            "margin:-7px 0;border-radius:9px;border:2px solid #FFFFFF;}"
        )
        self._slider.valueChanged.connect(self._on_price)
        main.addWidget(self._slider)
        main.addSpacing(6)

        mm = QHBoxLayout()
        self._min_lbl = QLabel("MIN")
        self._min_lbl.setFont(QFont("Segoe UI", 9))
        self._min_lbl.setStyleSheet("color:#94A3B8;")
        max_lbl = QLabel("MAX")
        max_lbl.setFont(QFont("Segoe UI", 9))
        max_lbl.setStyleSheet("color:#94A3B8;")
        max_lbl.setAlignment(Qt.AlignRight)
        mm.addWidget(self._min_lbl)
        mm.addStretch()
        mm.addWidget(max_lbl)
        main.addLayout(mm)
        main.addStretch()

    def _add_radio_row(self, name: str, btn_id: int, checked=False, count: str = ""):
        row = QHBoxLayout()
        row.setSpacing(0)

        rb = QRadioButton(name)
        rb.setFont(QFont("Segoe UI", 12))
        rb.setChecked(checked)
        rb.setStyleSheet(
            "QRadioButton{color:#334155;spacing:10px;}"
            "QRadioButton::indicator{width:16px;height:16px;border-radius:8px;"
            "border:2px solid #CBD5E1;background:white;}"
            "QRadioButton::indicator:checked{border:2px solid #2563EB;background:#2563EB;}"
        )

        cnt_lbl = QLabel(count)
        cnt_lbl.setFont(QFont("Segoe UI", 11))
        cnt_lbl.setStyleSheet("color:#94A3B8;")
        cnt_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._airline_group.addButton(rb, btn_id)
        row.addWidget(rb, stretch=1)
        row.addWidget(cnt_lbl)

        row_w = QWidget()
        row_w.setFixedHeight(36)
        row_w.setLayout(row)
        self._airline_container.addWidget(row_w)

    # ── PUBLIC API ────────────────────────────────────────────

    def rebuild_airlines(self, airlines: list[str], counts: dict = None):
        """
        Xoá radio cũ, build lại từ danh sách airlines thực tế.
        Gọi sau khi _load_flights() xong.
        counts = {"Airbus A321": 3, ...} — tuỳ chọn
        """
        counts = counts or {}

        # Xoá buttons khỏi group
        for btn in self._airline_group.buttons():
            self._airline_group.removeButton(btn)

        # Xoá widgets trong container
        while self._airline_container.count():
            item = self._airline_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Build lại
        all_names = ["All"] + sorted(airlines)
        for i, name in enumerate(all_names):
            c = str(counts.get(name, "")) if name != "All" else ""
            self._add_radio_row(name, i, checked=(i == 0), count=c)

    def set_price_range(self, min_price: int, max_price: int):
        """
        Cập nhật slider range theo giá thực tế từ data.
        Tự động format VND (≥10,000) hoặc USD.
        """
        if self._slider is None:
            return
        self._slider.setRange(min_price, max_price)
        self._slider.setValue(max_price)
        self._min_lbl.setText(self._fmt_price(min_price))
        self._price_val.setText(self._fmt_price(max_price))

    @staticmethod
    def _fmt_price(v: int) -> str:
        if v >= 1_000_000:
            return f"{v / 1_000_000:.1f}M"
        if v >= 10_000:
            return f"{v // 1_000}K"
        return f"${v}"

    def _on_price(self, val: int):
        self._price_val.setText(self._fmt_price(val))
        self._emit()

    def _emit(self):
        btn = self._airline_group.checkedButton()
        self.filter_changed.emit({
            "airline":   btn.text() if btn else "All",
            "max_price": self._slider.value() if self._slider else 999_999_999,
        })

    # Properties dùng trong FlightWidget
    @property
    def selected_airline(self) -> str:
        btn = self._airline_group.checkedButton()
        return btn.text() if btn else "All"

    @property
    def max_price(self) -> int:
        return self._slider.value() if self._slider else 999_999_999


# ─────────────────────────────────────────────────────────────
#  Flight Widget
# ─────────────────────────────────────────────────────────────
class FlightWidget(QWidget):
    book_clicked = Signal(dict)
    nav_home     = Signal()   # ← kết nối từ main_window: flight_widget.nav_home.connect(show_dashboard)

    def __init__(self, search_params: dict = None,
                 user_info: dict = None, parent=None):
        super().__init__(parent)
        self.setObjectName("FlightPage")
        self.search_params = search_params or {}
        self.user_info = user_info or {"first_name": "John", "last_name": "Doe"}
        self._all_flights: list[dict] = []
        self._build_ui()
        self._load_flights()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_navbar())
        self._header_frame = self._build_header()
        root.addWidget(self._header_frame)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Filter panel
        self._filter = FilterPanel(parent=self)
        self._filter.filter_changed.connect(self._apply_filters)
        body.addWidget(self._filter)

        # Right area
        right = QVBoxLayout()
        right.setContentsMargins(24, 20, 24, 20)
        right.setSpacing(14)

        bar = QHBoxLayout()
        self._result_lbl = QLabel("Đang tải...")
        self._result_lbl.setFont(QFont("Segoe UI", 13))
        self._result_lbl.setStyleSheet("color:#64748B;")

        sort_lbl = QLabel("SORT BY:")
        sort_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        sort_lbl.setStyleSheet("color:#64748B;")

        self._sort_combo = QComboBox()
        self._sort_combo.addItems([
            "Cheapest First", "Fastest First", "Departure ↑", "Departure ↓"
        ])
        self._sort_combo.setFixedHeight(40)
        self._sort_combo.setStyleSheet(
            "QComboBox{border:1px solid #E2E8F0;border-radius:10px;"
            "padding:4px 14px;font-size:13px;font-weight:bold;"
            "color:#2563EB;background:#EFF6FF;min-width:170px;}"
            "QComboBox::drop-down{border:none;width:24px;}"
            "QComboBox QAbstractItemView{border:1px solid #E2E8F0;}"
        )
        self._sort_combo.currentIndexChanged.connect(self._apply_filters)

        bar.addWidget(self._result_lbl)
        bar.addStretch()
        bar.addWidget(sort_lbl)
        bar.addSpacing(8)
        bar.addWidget(self._sort_combo)
        right.addLayout(bar)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setStyleSheet(
            "QScrollArea{border:none;background:transparent;}"
        )

        self._cards_widget = QWidget()
        self._cards_widget.setStyleSheet("background:transparent;")
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(12)
        self._cards_layout.addStretch()

        self._scroll.setWidget(self._cards_widget)
        right.addWidget(self._scroll)

        right_w = QWidget()
        right_w.setStyleSheet("background-color:#F1F5F9;")
        right_w.setLayout(right)
        body.addWidget(right_w, stretch=1)

        body_w = QWidget()
        body_w.setLayout(body)
        root.addWidget(body_w, stretch=1)

    def _build_navbar(self) -> QFrame:
        nav = QFrame()
        nav.setObjectName("NavBar")
        nav.setFixedHeight(62)

        lay = QHBoxLayout(nav)
        lay.setContentsMargins(32, 0, 32, 0)
        lay.setSpacing(0)

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

        for name in ["Home", "Flights", "Status", "Check-in", "Manage"]:
            btn = QPushButton(name)
            btn.setObjectName("NavBtnActive" if name == "Flights" else "NavBtn")
            btn.setCursor(Qt.PointingHandCursor)
            if name == "Home":
                # FIX: phát signal nav_home để main_window bắt và chuyển trang
                btn.clicked.connect(self.nav_home)
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

    def _build_header(self) -> QFrame:
        hdr = QFrame()
        hdr.setObjectName("FlightHeader")
        hdr.setFixedHeight(90)
        hdr.setStyleSheet(
            "QFrame#FlightHeader{background-color:#1a2c6e;border:none;}"
        )

        lay = QHBoxLayout(hdr)
        lay.setContentsMargins(32, 0, 32, 0)

        self._lbl_from = QLabel(self.search_params.get("from_code", "Anywhere"))
        self._lbl_from.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self._lbl_from.setStyleSheet("color:#FFFFFF;background:transparent;")

        arrow = QLabel("  ✈  ")
        arrow.setFont(QFont("Segoe UI Emoji", 18))
        arrow.setStyleSheet("color:#60A5FA;background:transparent;")

        self._lbl_to = QLabel(self.search_params.get("to_code", "Anywhere"))
        self._lbl_to.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self._lbl_to.setStyleSheet("color:#FFFFFF;background:transparent;")

        btn_mod = QPushButton("  🔍  Modify Search")
        btn_mod.setFixedHeight(42)
        btn_mod.setFont(QFont("Segoe UI", 12, QFont.Bold))
        btn_mod.setCursor(Qt.PointingHandCursor)
        btn_mod.setStyleSheet(
            "QPushButton{background-color:rgba(255,255,255,35);color:#FFFFFF;"
            "border:1px solid rgba(255,255,255,90);border-radius:10px;padding:0 20px;}"
            "QPushButton:hover{background-color:rgba(255,255,255,55);}"
        )
        btn_mod.clicked.connect(self.nav_home)  # Modify Search → quay về dashboard

        lay.addWidget(self._lbl_from)
        lay.addWidget(arrow)
        lay.addWidget(self._lbl_to)
        lay.addStretch()
        lay.addWidget(btn_mod)
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
                    JOIN aircraft  ac ON ac.id = f.aircraft_id
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

        # FIX 1: Rebuild airline radio buttons từ data thực tế
        airlines = sorted({f["airline"] for f in self._all_flights})
        counts   = {}
        for f in self._all_flights:
            counts[f["airline"]] = counts.get(f["airline"], 0) + 1
        self._filter.rebuild_airlines(airlines, counts)

        # FIX 2: Cập nhật slider range theo giá thực tế
        if self._all_flights:
            min_p = int(min(f["price_eco"] for f in self._all_flights))
            max_p = int(max(f["price_eco"] for f in self._all_flights))
            self._filter.set_price_range(min_p, max_p)

        self._apply_filters()

    def _row_to_flight(self, row) -> dict:
        dep = str(row["departure_time"])
        arr = str(row["arrival_time"])
        try:
            from datetime import datetime
            d1 = datetime.strptime(dep, "%Y-%m-%d %H:%M")
            d2 = datetime.strptime(arr, "%Y-%m-%d %H:%M")
            # FIX 3: dùng total_seconds() để đúng cho chuyến bay qua đêm
            total_min = int((d2 - d1).total_seconds()) // 60
            h, m = divmod(total_min, 60)
            duration = f"{h}h {m}m"
        except Exception:
            duration = "--"

        return {
            "id": row["id"], "flight_number": row["flight_number"],
            "airline": row["airline"],
            "departure_time": dep, "arrival_time": arr,
            "origin_code": row["origin_code"], "origin_city": row["origin_city"],
            "dest_code": row["dest_code"],     "dest_city": row["dest_city"],
            "price_eco": row["price_eco"],     "price_business": row["price_business"],
            "status": row["status"],
            "duration": duration,
            "stops": "NON-STOP",
        }

    @staticmethod
    def _mock_flights() -> list[dict]:
        return [
            {"id":1,"flight_number":"SF104","airline":"SkyFlow Airlines",
             "departure_time":"09:00","arrival_time":"10:30",
             "origin_code":"CDG","dest_code":"LHR",
             "price_eco":95,"price_business":133,
             "duration":"1h 30m","stops":"NON-STOP","status":"scheduled"},
            {"id":2,"flight_number":"OA202","airline":"Oceanic Airways",
             "departure_time":"08:30","arrival_time":"10:30",
             "origin_code":"LHR","dest_code":"CDG",
             "price_eco":120,"price_business":168,
             "duration":"2h 0m","stops":"NON-STOP","status":"scheduled"},
            {"id":3,"flight_number":"EA505","airline":"Emerald Air",
             "departure_time":"11:00","arrival_time":"15:00",
             "origin_code":"DUB","dest_code":"FCO",
             "price_eco":180,"price_business":252,
             "duration":"3h 0m","stops":"NON-STOP","status":"scheduled"},
            {"id":4,"flight_number":"SF101","airline":"SkyFlow Airlines",
             "departure_time":"10:00","arrival_time":"13:00",
             "origin_code":"LHR","dest_code":"JFK",
             "price_eco":450,"price_business":630,
             "duration":"8h 0m","stops":"NON-STOP","status":"scheduled"},
            {"id":5,"flight_number":"GW303","airline":"Global Wings",
             "departure_time":"15:00","arrival_time":"18:00",
             "origin_code":"JFK","dest_code":"NRT",
             "price_eco":850,"price_business":1190,
             "duration":"14h 0m","stops":"1STOP","status":"scheduled"},
        ]

    # ── Filters & Sort ───────────────────────────────────────
    def _apply_filters(self):
        airline  = self._filter.selected_airline
        max_p    = self._filter.max_price
        sort_idx = self._sort_combo.currentIndex()

        flights = [
            f for f in self._all_flights
            if (airline == "All" or f["airline"] == airline)
            and f["price_eco"] <= max_p
        ]

        sort_keys = [
            lambda f: f["price_eco"],
            lambda f: f.get("duration", "99h"),
            lambda f: f["departure_time"],
            lambda f: f["departure_time"],
        ]
        flights.sort(key=sort_keys[sort_idx], reverse=(sort_idx == 3))
        self._render_cards(flights)

    def _render_cards(self, flights: list[dict]):
        while self._cards_layout.count() > 1:
            item = self._cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        n = len(flights)
        self._result_lbl.setText(
            f"Showing <b>{n}</b> flight{'s' if n != 1 else ''}"
        )
        for i, f in enumerate(flights):
            card = FlightCard(f, self)
            card.book_clicked.connect(self.book_clicked)
            self._cards_layout.insertWidget(i, card)

    def update_search(self, params: dict):
        """Gọi từ main_window khi dashboard search xong."""
        self.search_params = params
        self._lbl_from.setText(params.get("from_code", "Anywhere"))
        self._lbl_to.setText(params.get("to_code",   "Anywhere"))
        self._load_flights()


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

    win = FlightWidget()
    win.resize(1280, 860)
    win.show()
    sys.exit(app.exec())