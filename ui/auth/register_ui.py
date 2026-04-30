"""
ui/register_ui.py
Màn hình đăng ký — SkyBoundAir
Thiết kế theo mockup: card trắng trên nền #EEF0F5
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy,
    QSpacerItem, QGraphicsDropShadowEffect,
)
from PySide6.QtGui import (
    QFont, QIcon, QPixmap, QPainter, QColor,
    QLinearGradient, QBrush, QPen, QPolygonF,
)
from PySide6.QtCore import Qt, QSize, QPointF, Signal
from PySide6.QtSvgWidgets import QSvgWidget
import os


# ─── Icon helpers ───────────────────────────────────────────────────────────

def _make_icon_pixmap(svg_path_data: str, size=18, color="#C0C7D3") -> QPixmap:
    """Tạo pixmap từ SVG string đơn giản bằng QPainter."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    return pix


def _logo_pixmap(size=52) -> QPixmap:
    """Tạo logo gradient hình tròn bo."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    grad = QLinearGradient(0, 0, size, size)
    grad.setColorAt(0, QColor("#3B82F6"))
    grad.setColorAt(1, QColor("#2563EB"))
    painter.setBrush(QBrush(grad))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, size, size, size * 0.27, size * 0.27)

    # Vẽ icon mũi tên (paper plane)
    painter.setPen(QPen(Qt.white, 1.8))
    painter.setBrush(Qt.NoBrush)
    scale = size / 52
    painter.scale(scale, scale)
    pts_arrow = QPolygonF([QPointF(40, 8), QPointF(20, 26)])
    pts_body  = QPolygonF([QPointF(40, 8), QPointF(28, 42),
                            QPointF(20, 26), QPointF(6, 18), QPointF(40, 8)])
    painter.drawPolyline(pts_arrow)
    painter.drawPolygon(pts_body)
    painter.end()
    return pix


# ─── InputRow: icon + QLineEdit gộp trong 1 QFrame ─────────────────────────

class IconLineEdit(QFrame):
    """QLineEdit có icon ở bên trái, viền bo tròn."""

    def __init__(self, icon_char: str, placeholder: str,
                 echo=QLineEdit.Normal, parent=None):
        super().__init__(parent)
        self.setObjectName("InputFrame")
        self.setFixedHeight(46)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 14, 0)
        lay.setSpacing(8)

        icon_lbl = QLabel(icon_char)
        icon_lbl.setFixedWidth(18)
        icon_lbl.setFont(QFont("Segoe UI Emoji", 13))
        icon_lbl.setStyleSheet("color: #C0C7D3; background: transparent; border: none;")
        icon_lbl.setAlignment(Qt.AlignCenter)

        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        self.edit.setEchoMode(echo)
        self.edit.setStyleSheet(
            "QLineEdit {"
            "  border: none; background: transparent;"
            "  font-size: 14px; color: #111111; padding: 0;"
            "}"
            "QLineEdit::placeholder { color: #B8BEC9; }"
        )

        lay.addWidget(icon_lbl)
        lay.addWidget(self.edit)

    def text(self):
        return self.edit.text()

    def setFocus(self):
        self.edit.setFocus()


# ─── Divider ────────────────────────────────────────────────────────────────

class HLineDivider(QWidget):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 4)
        lay.setSpacing(10)

        def _line():
            f = QFrame()
            f.setFrameShape(QFrame.HLine)
            f.setStyleSheet("color: #E8EBF0;")
            f.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            return f

        lay.addWidget(_line())
        if text:
            lbl = QLabel(text.upper())
            lbl.setObjectName("DividerLabel")
            lbl.setAlignment(Qt.AlignCenter)
            lay.addWidget(lbl)
        lay.addWidget(_line())


# ─── RegisterWidget ──────────────────────────────────────────────────────────

class RegisterWidget(QWidget):
    """
    Màn hình đăng ký SkyBoundAir.

    Signals:
        go_login()      — người dùng bấm "Log in"
        registered(dict) — đăng ký thành công, truyền user_info
    """

    go_login   = Signal()
    registered = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AuthWindow")
        self._build_ui()

    # ── Build ────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(24, 24, 24, 24)

        card = self._make_card()
        root.addWidget(card, alignment=Qt.AlignCenter)

    def _make_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("AuthCard")
        card.setFixedWidth(420)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

        # Drop shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 30))
        card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(32, 36, 32, 36)
        lay.setSpacing(0)

        # ── Brand ──
        lay.addWidget(self._brand_section())
        lay.addSpacing(24)

        # ── First / Last name ──
        name_row = QHBoxLayout()
        name_row.setSpacing(12)

        self._first = self._plain_field("FIRST NAME", "John")
        self._last  = self._plain_field("LAST NAME", "Doe")
        name_row.addWidget(self._first)
        name_row.addWidget(self._last)

        lay.addLayout(name_row)
        lay.addSpacing(14)

        # ── Email ──
        lay.addWidget(self._label("EMAIL ADDRESS"))
        lay.addSpacing(6)
        self._email = IconLineEdit("✉", "name@example.com")
        lay.addWidget(self._email)
        lay.addSpacing(14)

        # ── Password ──
        lay.addWidget(self._label("PASSWORD"))
        lay.addSpacing(6)
        self._password = IconLineEdit("🔒", "••••••••", QLineEdit.Password)
        lay.addWidget(self._password)
        lay.addSpacing(20)

        # ── Error label ──
        self._error_lbl = QLabel("")
        self._error_lbl.setObjectName("ErrorLabel")
        self._error_lbl.setWordWrap(True)
        self._error_lbl.setVisible(False)
        lay.addWidget(self._error_lbl)

        # ── Create Account button ──
        self._btn_create = QPushButton("  Create Account  ›")
        self._btn_create.setObjectName("BtnPrimary")
        self._btn_create.setFixedHeight(50)
        self._btn_create.setCursor(Qt.PointingHandCursor)
        self._btn_create.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        self._btn_create.clicked.connect(self._on_register)
        lay.addWidget(self._btn_create)
        lay.addSpacing(20)

        # ── Footer ──
        foot = QHBoxLayout()
        foot.setAlignment(Qt.AlignCenter)
        foot.setSpacing(4)

        foot_lbl = QLabel("Already have an account?")
        foot_lbl.setObjectName("FooterText")

        link = QPushButton("Log in")
        link.setObjectName("LinkBtn")
        link.setCursor(Qt.PointingHandCursor)
        link.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        link.clicked.connect(self.go_login)

        foot.addWidget(foot_lbl)
        foot.addWidget(link)
        lay.addLayout(foot)

        return card

    # ── Sub-builders ─────────────────────────────────────────────────────

    def _brand_section(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setAlignment(Qt.AlignCenter)
        lay.setSpacing(10)
        lay.setContentsMargins(0, 0, 0, 0)

        # Logo
        logo_lbl = QLabel()
        logo_lbl.setPixmap(_logo_pixmap(52))
        logo_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(logo_lbl)

        # Title row "SkyBound" + "Air"
        title_row = QHBoxLayout()
        title_row.setSpacing(0)
        title_row.setAlignment(Qt.AlignCenter)

        t1 = QLabel("SkyBound")
        t1.setFont(QFont("Segoe UI", 20, QFont.Bold))
        t1.setStyleSheet("color: #111111;")

        t2 = QLabel("Air")
        t2.setFont(QFont("Segoe UI", 20, QFont.Bold))
        t2.setStyleSheet("color: #3B82F6;")

        title_row.addWidget(t1)
        title_row.addWidget(t2)
        lay.addLayout(title_row)

        sub = QLabel("Create an account to start booking.")
        sub.setObjectName("BrandSub")
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)

        return w

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("FieldLabel")
        lbl.setFont(QFont("Segoe UI", 8, QFont.DemiBold))
        return lbl

    def _plain_field(self, label_text: str, placeholder: str) -> QWidget:
        """Tạo 1 field gồm label + input (không có icon)."""
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        lay.addWidget(self._label(label_text))

        edit = QLineEdit()
        edit.setPlaceholderText(placeholder)
        edit.setFixedHeight(46)
        edit.setObjectName("PlainInput")
        edit.setStyleSheet(
            "QLineEdit#PlainInput {"
            "  border: 1.5px solid #E8EBF0;"
            "  border-radius: 10px;"
            "  padding: 11px 14px;"
            "  font-size: 14px;"
            "  color: #111111;"
            "  background: #FAFBFC;"
            "}"
            "QLineEdit#PlainInput:focus {"
            "  border: 1.5px solid #3B82F6;"
            "  background: #FFFFFF;"
            "}"
            "QLineEdit#PlainInput::placeholder { color: #B8BEC9; }"
        )
        lay.addWidget(edit)
        w._edit = edit          # expose để lấy text
        return w

    # ── Logic ────────────────────────────────────────────────────────────

    def _show_error(self, msg: str):
        self._error_lbl.setText(msg)
        self._error_lbl.setVisible(True)

    def _hide_error(self):
        self._error_lbl.setVisible(False)

    def _on_register(self):
        self._hide_error()

        first    = self._first._edit.text().strip()
        last     = self._last._edit.text().strip()
        email    = self._email.text().strip()
        password = self._password.text()

        # Validate UI (gọi thêm modules/auth.py nếu muốn)
        if not first or not last:
            self._show_error("Vui lòng nhập đầy đủ họ và tên.")
            return
        if not email or "@" not in email:
            self._show_error("Địa chỉ email không hợp lệ.")
            return
        if len(password) < 6:
            self._show_error("Mật khẩu phải có ít nhất 6 ký tự.")
            return

        # Gọi auth module
        try:
            from modules.auth import register_user
            ok, msg = register_user(first, last, email, password)
            if ok:
                self.registered.emit({
                    "first_name": first,
                    "last_name":  last,
                    "email":      email,
                    "initials":   f"{first[0]}{last[0]}".upper(),
                    "full_name":  f"{first} {last}",
                })
            else:
                self._show_error(msg)
        except ImportError:
            # Nếu chưa có DB, vẫn cho chuyển màn hình để test UI
            self.registered.emit({
                "first_name": first, "last_name": last,
                "email": email,
                "initials": f"{first[0]}{last[0]}".upper(),
                "full_name": f"{first} {last}",
            })
             