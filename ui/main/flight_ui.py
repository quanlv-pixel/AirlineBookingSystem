"""
ui/main/flight_ui.py
Trang tìm kiếm & danh sách chuyến bay — SkyBoundAir
Thiết kế theo mockup: header xanh, filter panel trái, danh sách phải.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QSizePolicy, QButtonGroup,
    QRadioButton, QSlider, QComboBox, QSpacerItem,
)
from PySide6.QtGui import QFont, QColor, QPainter, QPen
from PySide6.QtCore import Qt, Signal, QSize

try:
    from database.db import fetchall
except ImportError:
    fetchall = None


# ─── FlightCard ──────────────────────────────────────────────────────────────

class PriceButton(QPushButton):
    """Nút giá ECO / DELUXE / SKYBOSS."""
    def __init__(self, tier: str, price: str, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(QSize(88, 64))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 8, 6, 8)
        lay.setSpacing(2)
        lay.setAlignment(Qt.AlignCenter)

        tier_lbl = QLabel(tier)
        tier_lbl.setAlignment(Qt.AlignCenter)
        tier_lbl.setFont(QFont("Segoe UI", 8, QFont.Bold))

        price_lbl = QLabel(price)
        price_lbl.setAlignment(Qt.AlignCenter)
        price_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))

        lay.addWidget(tier_lbl)
        lay.addWidget(price_lbl)

        # Màu theo tier
        if tier == "ECO":
            style = (
                "QPushButton { background-color: #DCFCE7; border-radius: 8px; border: none; }"
                "QPushButton:hover { background-color: #BBF7D0; }"
            )
            for lbl in [tier_lbl, price_lbl]:
                lbl.setStyleSheet("color: #15803D; background: transparent;")
        elif tier == "DELUXE":
            style = (
                "QPushButton { background-color: #FEF3C7; border-radius: 8px; border: none; }"
                "QPushButton:hover { background-color: #FDE68A; }"
            )
            for lbl in [tier_lbl, price_lbl]:
                lbl.setStyleSheet("color: #B45309; background: transparent;")
        else:  # SKYBOSS
            style = (
                "QPushButton { background-color: #1E293B; border-radius: 8px; border: none; }"
                "QPushButton:hover { background-color: #334155; }"
            )
            for lbl in [tier_lbl, price_lbl]:
                lbl.setStyleSheet("color: #FFFFFF; background: transparent;")

        self.setStyleSheet(style)


class FlightCard(QFrame):
    """Card hiển thị 1 chuyến bay."""
    book_clicked = Signal(dict)

    def __init__(self, flight: dict, parent=None):
        super().__init__(parent)
        self.flight = flight
        self.setObjectName("FlightCard")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(100)
        self._build()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(20, 0, 20, 0)
        root.setSpacing(0)

        # ── Icon máy bay ──
        icon = QLabel("✈")
        icon.setFont(QFont("Segoe UI Emoji", 20))
        icon.setFixedWidth(48)
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("color: #005088;")
        root.addWidget(icon)

        # ── Tên hãng + số hiệu ──
        airline_col = QVBoxLayout()
        airline_col.setSpacing(2)
        airline_col.setAlignment(Qt.AlignVCenter)

        airline_lbl = QLabel(self.flight.get("airline", "SkyBound Air"))
        airline_lbl.setFont(QFont("Segoe UI", 9))
        airline_lbl.setStyleSheet("color: #64748B;")

        fn_lbl = QLabel(self.flight.get("flight_number", "SBA001"))
        fn_lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        fn_lbl.setStyleSheet("color: #0F172A;")

        airline_col.addWidget(airline_lbl)
        airline_col.addWidget(fn_lbl)

        col_w = QWidget()
        col_w.setFixedWidth(130)
        col_w.setLayout(airline_col)
        root.addWidget(col_w)

        # ── Giờ khởi hành + sân bay ──
        root.addWidget(self._time_col(
            self.flight.get("departure_time", "00:00")[-5:] if len(self.flight.get("departure_time",""))>5
            else self.flight.get("departure_time","--:--"),
            self.flight.get("origin_code", "???")
        ))

        # ── Đường kẻ + thời gian bay + NON-STOP ──
        root.addWidget(self._route_col(
            self.flight.get("duration", "2h 0m"),
            self.flight.get("stops", "NON-STOP")
        ), stretch=1)

        # ── Giờ đến + sân bay ──
        root.addWidget(self._time_col(
            self.flight.get("arrival_time", "00:00")[-5:] if len(self.flight.get("arrival_time",""))>5
            else self.flight.get("arrival_time","--:--"),
            self.flight.get("dest_code", "???")
        ))

        root.addSpacing(20)

        # ── Nút giá ──
        price_eco      = self._fmt(self.flight.get("price_eco", 0))
        price_business = self._fmt(self.flight.get("price_business", 0))
        price_boss     = self._fmt(int(self.flight.get("price_business", 0) * 1.5))

        btn_eco  = PriceButton("ECO",     price_eco)
        btn_dlx  = PriceButton("DELUXE",  price_business)
        btn_boss = PriceButton("SKYBOSS", price_boss)

        btn_eco.clicked.connect(lambda: self.book_clicked.emit({**self.flight, "class": "eco"}))
        btn_dlx.clicked.connect(lambda: self.book_clicked.emit({**self.flight, "class": "business"}))
        btn_boss.clicked.connect(lambda: self.book_clicked.emit({**self.flight, "class": "skyboss"}))

        price_row = QHBoxLayout()
        price_row.setSpacing(6)
        price_row.addWidget(btn_eco)
        price_row.addWidget(btn_dlx)
        price_row.addWidget(btn_boss)

        price_w = QWidget()
        price_w.setLayout(price_row)
        root.addWidget(price_w)

    def _time_col(self, time_str: str, code: str) -> QWidget:
        w = QWidget()
        w.setFixedWidth(80)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(2)
        lay.setAlignment(Qt.AlignVCenter)

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

    @staticmethod
    def _fmt(price: float) -> str:
        """Format giá: 899000 → 899K hoặc 4,500,000 → 4.5M"""
        if price >= 1_000_000:
            return f"{price/1_000_000:.1f}M"
        if price >= 1_000:
            return f"{int(price/1_000)}K"
        return str(int(price))


class _RouteLine(QWidget):
    """Đường kẻ ngang có chấm tròn 2 đầu."""
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


# ─── FilterPanel ─────────────────────────────────────────────────────────────

class FilterPanel(QFrame):
    filter_changed = Signal(dict)

    def __init__(self, airlines: list[str], parent=None):
        super().__init__(parent)
        self.setObjectName("FilterPanel")
        self.setFixedWidth(280)
        self._airlines = airlines
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 24, 20, 24)
        lay.setSpacing(0)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("FILTERS")
        title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        title.setStyleSheet("color: #0F172A;")

        icon = QLabel("⚙")
        icon.setFont(QFont("Segoe UI Emoji", 14))
        icon.setStyleSheet("color: #005088;")

        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(icon)
        lay.addLayout(hdr)
        lay.addSpacing(24)

        # ── Airlines ──
        al_lbl = QLabel("AIRLINES")
        al_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        al_lbl.setStyleSheet("color: #94A3B8;")
        lay.addWidget(al_lbl)
        lay.addSpacing(12)

        self._airline_group = QButtonGroup(self)
        self._airline_group.setExclusive(True)

        all_airlines = ["All"] + self._airlines
        for i, name in enumerate(all_airlines):
            row = QHBoxLayout()
            row.setSpacing(8)

            rb = QRadioButton(name)
            rb.setFont(QFont("Segoe UI", 12))
            rb.setStyleSheet(
                "QRadioButton { color: #334155; spacing: 8px; }"
                "QRadioButton::indicator { width: 16px; height: 16px; border-radius: 8px;"
                "  border: 2px solid #CBD5E1; background: white; }"
                "QRadioButton::indicator:checked { border: 2px solid #005088;"
                "  background: #005088; }"
            )
            if i == 0:
                rb.setChecked(True)

            cnt = QLabel("—" if name == "All" else "12")
            cnt.setFont(QFont("Segoe UI", 11))
            cnt.setStyleSheet("color: #94A3B8;")
            cnt.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            self._airline_group.addButton(rb, i)
            row.addWidget(rb, stretch=1)
            row.addWidget(cnt)

            w = QWidget()
            w.setLayout(row)
            w.setFixedHeight(36)
            lay.addWidget(w)

        self._airline_group.buttonClicked.connect(self._emit)
        lay.addSpacing(28)

        # ── Price Range ──
        pr_lbl = QLabel("PRICE RANGE")
        pr_lbl.setFont(QFont("Segoe UI", 9, QFont.Bold))
        pr_lbl.setStyleSheet("color: #94A3B8;")
        lay.addWidget(pr_lbl)
        lay.addSpacing(12)

        self._price_val = QLabel("Tối đa: 12,000,000đ")
        self._price_val.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self._price_val.setStyleSheet("color: #005088;")
        lay.addWidget(self._price_val)
        lay.addSpacing(8)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(500_000, 15_000_000)
        self._slider.setValue(12_000_000)
        self._slider.setStyleSheet(
            "QSlider::groove:horizontal { height: 4px; background: #E2E8F0; border-radius: 2px; }"
            "QSlider::sub-page:horizontal { background: #005088; border-radius: 2px; }"
            "QSlider::handle:horizontal { background: #005088; width: 16px; height: 16px;"
            "  margin: -6px 0; border-radius: 8px; }"
        )
        self._slider.valueChanged.connect(self._on_price_changed)
        lay.addWidget(self._slider)

        minmax = QHBoxLayout()
        mn = QLabel("500K")
        mn.setFont(QFont("Segoe UI", 9))
        mn.setStyleSheet("color: #94A3B8;")
        mx = QLabel("MAX")
        mx.setFont(QFont("Segoe UI", 9))
        mx.setStyleSheet("color: #94A3B8;")
        mx.setAlignment(Qt.AlignRight)
        minmax.addWidget(mn)
        minmax.addStretch()
        minmax.addWidget(mx)
        lay.addLayout(minmax)

        lay.addStretch()

    def _on_price_changed(self, val: int):
        if val >= 1_000_000:
            text = f"Tối đa: {val/1_000_000:.1f}M đ"
        else:
            text = f"Tối đa: {val//1_000}K đ"
        self._price_val.setText(text)
        self._emit()

    def _emit(self):
        checked = self._airline_group.checkedButton()
        self.filter_changed.emit({
            "airline": checked.text() if checked else "All",
            "max_price": self._slider.value(),
        })


# ─── FlightWidget ─────────────────────────────────────────────────────────────

class FlightWidget(QWidget):
    """
    Trang danh sách chuyến bay.

    Signals:
        book_clicked(dict) — người dùng chọn 1 chuyến để đặt
    """
    book_clicked = Signal(dict)

    def __init__(self, search_params: dict = None, parent=None):
        super().__init__(parent)
        self.setObjectName("FlightPage")
        self.search_params = search_params or {}
        self._all_flights: list[dict] = []
        self._build_ui()
        self._load_flights()

    # ── Build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header xanh ──
        root.addWidget(self._build_header())

        # ── Body: filter + danh sách ──
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)

        # Dữ liệu airline tạm — sẽ cập nhật sau khi load
        self._filter = FilterPanel(airlines=[], parent=self)
        self._filter.filter_changed.connect(self._apply_filters)
        body.addWidget(self._filter)

        # Vùng danh sách bên phải
        right = QVBoxLayout()
        right.setContentsMargins(24, 20, 24, 20)
        right.setSpacing(16)

        # Thanh kết quả + sort
        bar = QHBoxLayout()
        self._result_lbl = QLabel("Đang tải...")
        self._result_lbl.setObjectName("ResultLabel")
        self._result_lbl.setFont(QFont("Segoe UI", 13))
        self._result_lbl.setStyleSheet("color: #64748B;")

        sort_lbl = QLabel("SORT BY:")
        sort_lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        sort_lbl.setStyleSheet("color: #64748B;")

        self._sort_combo = QComboBox()
        self._sort_combo.setObjectName("SortCombo")
        self._sort_combo.addItems([
            "Cheapest First", "Fastest First",
            "Departure ↑", "Departure ↓",
        ])
        self._sort_combo.setFixedHeight(36)
        self._sort_combo.setStyleSheet(
            "QComboBox { border: 1px solid #E2E8F0; border-radius: 8px;"
            "  padding: 4px 12px; font-size: 13px; font-weight: 600;"
            "  color: #005088; background: #EFF6FF; min-width: 160px; }"
            "QComboBox::drop-down { border: none; width: 24px; }"
            "QComboBox QAbstractItemView { border: 1px solid #E2E8F0; border-radius: 8px; }"
        )
        self._sort_combo.currentIndexChanged.connect(self._apply_filters)

        bar.addWidget(self._result_lbl)
        bar.addStretch()
        bar.addWidget(sort_lbl)
        bar.addSpacing(8)
        bar.addWidget(self._sort_combo)
        right.addLayout(bar)

        # Scroll area chứa các FlightCard
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setObjectName("FlightScroll")
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

    def _build_header(self) -> QWidget:
        hdr = QFrame()
        hdr.setObjectName("FlightHeader")
        hdr.setFixedHeight(80)
        hdr.setStyleSheet(
            "QFrame#FlightHeader { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #003366,stop:1 #005088); }"
        )

        lay = QHBoxLayout(hdr)
        lay.setContentsMargins(28, 0, 28, 0)

        origin = self.search_params.get("from_code", "Anywhere")
        dest   = self.search_params.get("to_code",   "Anywhere")

        lbl_from = QLabel(origin)
        lbl_from.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lbl_from.setStyleSheet("color: white;")

        arrow = QLabel("  ✈  ")
        arrow.setFont(QFont("Segoe UI Emoji", 18))
        arrow.setStyleSheet("color: #11CAA0;")

        lbl_to = QLabel(dest)
        lbl_to.setFont(QFont("Segoe UI", 22, QFont.Bold))
        lbl_to.setStyleSheet("color: white;")

        btn_modify = QPushButton("  🔍  Modify Search")
        btn_modify.setFixedHeight(40)
        btn_modify.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        btn_modify.setCursor(Qt.PointingHandCursor)
        btn_modify.setStyleSheet(
            "QPushButton { background: rgba(255,255,255,30); color: white;"
            "  border: 1px solid rgba(255,255,255,80); border-radius: 8px; padding: 0 20px; }"
            "QPushButton:hover { background: rgba(255,255,255,50); }"
        )

        lay.addWidget(lbl_from)
        lay.addWidget(arrow)
        lay.addWidget(lbl_to)
        lay.addStretch()
        lay.addWidget(btn_modify)

        return hdr

    # ── Data ──────────────────────────────────────────────────────────────

    def _load_flights(self):
        """Load chuyến bay từ DB hoặc dùng dữ liệu mẫu."""
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
                    JOIN aircraft ac ON ac.id = f.aircraft_id
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
                print(f"[FlightWidget] Lỗi load flights: {e}")
                self._all_flights = self._mock_flights()
        else:
            self._all_flights = self._mock_flights()

        # Cập nhật filter airlines
        airlines = sorted({f["airline"] for f in self._all_flights})
        self._filter._airlines = airlines

        self._apply_filters()

    def _row_to_flight(self, row) -> dict:
        dep = str(row["departure_time"])
        arr = str(row["arrival_time"])

        # Tính thời gian bay
        try:
            from datetime import datetime
            fmt = "%Y-%m-%d %H:%M"
            d1  = datetime.strptime(dep, fmt)
            d2  = datetime.strptime(arr, fmt)
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
        return [
            {"id":1,"flight_number":"SBA001","airline":"Airbus A321",
             "departure_time":"2026-10-24 06:00","arrival_time":"2026-10-24 08:10",
             "origin_code":"SGN","origin_city":"Ho Chi Minh",
             "dest_code":"HAN","dest_city":"Ha Noi",
             "price_eco":899000,"price_business":2500000,
             "status":"scheduled","duration":"2h 10m","stops":"NON-STOP"},
            {"id":2,"flight_number":"SBA002","airline":"Airbus A321",
             "departure_time":"2026-10-24 09:00","arrival_time":"2026-10-24 11:10",
             "origin_code":"HAN","origin_city":"Ha Noi",
             "dest_code":"SGN","dest_city":"Ho Chi Minh",
             "price_eco":899000,"price_business":2500000,
             "status":"scheduled","duration":"2h 10m","stops":"NON-STOP"},
            {"id":3,"flight_number":"SBA003","airline":"Boeing 737",
             "departure_time":"2026-10-24 07:30","arrival_time":"2026-10-24 08:50",
             "origin_code":"SGN","origin_city":"Ho Chi Minh",
             "dest_code":"DAD","dest_city":"Da Nang",
             "price_eco":650000,"price_business":1800000,
             "status":"scheduled","duration":"1h 20m","stops":"NON-STOP"},
            {"id":4,"flight_number":"SBA004","airline":"Airbus A350",
             "departure_time":"2026-10-24 23:00","arrival_time":"2026-10-25 07:30",
             "origin_code":"SGN","origin_city":"Ho Chi Minh",
             "dest_code":"NRT","dest_city":"Tokyo",
             "price_eco":4500000,"price_business":12000000,
             "status":"scheduled","duration":"8h 30m","stops":"NON-STOP"},
        ]

    # ── Filters & Sort ────────────────────────────────────────────────────

    def _apply_filters(self):
        checked = self._filter._airline_group.checkedButton()
        airline_filter = checked.text() if checked else "All"
        max_price      = self._filter._slider.value()
        sort_idx       = self._sort_combo.currentIndex()

        flights = [
            f for f in self._all_flights
            if (airline_filter == "All" or f["airline"] == airline_filter)
            and f["price_eco"] <= max_price
        ]

        if sort_idx == 0:   # Cheapest
            flights.sort(key=lambda f: f["price_eco"])
        elif sort_idx == 1: # Fastest
            flights.sort(key=lambda f: f.get("duration", "99h"))
        elif sort_idx == 2: # Departure ↑
            flights.sort(key=lambda f: f["departure_time"])
        elif sort_idx == 3: # Departure ↓
            flights.sort(key=lambda f: f["departure_time"], reverse=True)

        self._render_cards(flights)

    def _render_cards(self, flights: list[dict]):
        # Xoá cards cũ
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
        """Cập nhật params từ dashboard và reload."""
        self.search_params = params
        # Cập nhật header
        origin = params.get("from_code", "Anywhere")
        dest   = params.get("to_code",   "Anywhere")
        # Tìm lại label trong header và cập nhật
        self._load_flights()