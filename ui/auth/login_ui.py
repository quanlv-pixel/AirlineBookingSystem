"""
ui/login_ui.py
Màn hình đăng nhập — SkyBoundAir
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import (
    QFont, QPixmap, QPainter, QColor,
    QLinearGradient, QBrush, QPen, QPolygonF,
)
from PySide6.QtCore import Qt, QPointF, Signal

# ─── Reuse helpers từ register_ui ──────────────────────────────────────────
from ui.auth.register_ui import IconLineEdit, HLineDivider, _logo_pixmap


# ─── LoginWidget ────────────────────────────────────────────────────────────

class LoginWidget(QWidget):
    """
    Màn hình đăng nhập SkyBoundAir.

    Signals:
        go_register()       — người dùng bấm "Sign up for free"
        logged_in(dict)     — đăng nhập thành công, truyền user_info
    """

    go_register = Signal()
    logged_in   = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AuthWindow")
        self._build_ui()

    # ── Build ────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(24, 24, 24, 24)
        root.addWidget(self._make_card(), alignment=Qt.AlignCenter)

    def _make_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("AuthCard")
        card.setFixedWidth(420)
        card.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)

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
        lay.addSpacing(28)

        # ── Email ──
        lay.addWidget(self._label("EMAIL ADDRESS"))
        lay.addSpacing(6)
        self._email = IconLineEdit("✉", "name@example.com")
        lay.addWidget(self._email)
        lay.addSpacing(14)

        # ── Password row (label + FORGOT?) ──
        pw_header = QHBoxLayout()
        pw_header.addWidget(self._label("PASSWORD"))
        pw_header.addStretch()

        forgot_btn = QPushButton("FORGOT?")
        forgot_btn.setObjectName("ForgotBtn")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.setFont(QFont("Segoe UI", 8, QFont.DemiBold))
        forgot_btn.clicked.connect(self._on_forgot)
        pw_header.addWidget(forgot_btn)

        lay.addLayout(pw_header)
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

        # ── Sign In button ──
        self._btn_signin = QPushButton("  Sign In  ›")
        self._btn_signin.setObjectName("BtnPrimary")
        self._btn_signin.setFixedHeight(50)
        self._btn_signin.setCursor(Qt.PointingHandCursor)
        self._btn_signin.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        self._btn_signin.clicked.connect(self._on_login)
        lay.addWidget(self._btn_signin)
        lay.addSpacing(20)

        # ── Divider ──
        lay.addWidget(HLineDivider("Or explore as guest"))
        lay.addSpacing(14)

        # ── Social buttons ──
        social_row = QHBoxLayout()
        social_row.setSpacing(12)

        btn_google = self._social_btn("G  Google")
        btn_github = self._social_btn("🐙  Github")

        btn_google.clicked.connect(lambda: self._on_social("Google"))
        btn_github.clicked.connect(lambda: self._on_social("Github"))

        social_row.addWidget(btn_google)
        social_row.addWidget(btn_github)
        lay.addLayout(social_row)
        lay.addSpacing(20)

        # ── Footer ──
        foot = QHBoxLayout()
        foot.setAlignment(Qt.AlignCenter)
        foot.setSpacing(4)

        foot_lbl = QLabel("Don't have an account?")
        foot_lbl.setObjectName("FooterText")

        link = QPushButton("Sign up for free")
        link.setObjectName("LinkBtn")
        link.setCursor(Qt.PointingHandCursor)
        link.setFont(QFont("Segoe UI", 13, QFont.DemiBold))
        link.clicked.connect(self.go_register)

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

        logo_lbl = QLabel()
        logo_lbl.setPixmap(_logo_pixmap(52))
        logo_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(logo_lbl)

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

        sub = QLabel("Log in to manage your journeys.")
        sub.setObjectName("BrandSub")
        sub.setAlignment(Qt.AlignCenter)
        lay.addWidget(sub)

        return w

    def _label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("FieldLabel")
        lbl.setFont(QFont("Segoe UI", 8, QFont.DemiBold))
        return lbl

    def _social_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setObjectName("BtnSocial")
        btn.setFixedHeight(42)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Segoe UI", 12))
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return btn

    # ── Logic ────────────────────────────────────────────────────────────

    def _show_error(self, msg: str):
        self._error_lbl.setText(msg)
        self._error_lbl.setVisible(True)

    def _hide_error(self):
        self._error_lbl.setVisible(False)

    def _on_login(self):
        self._hide_error()

        email    = self._email.text().strip()
        password = self._password.text()

        if not email or not password:
            self._show_error("Vui lòng nhập email và mật khẩu.")
            return

        # Gọi auth module
        try:
            from modules.auth import login_user
            ok, msg, user_info = login_user(email, password)
            if ok:
                self.logged_in.emit(user_info)
            else:
                self._show_error(msg)
        except ImportError:
            # Test UI khi chưa có DB
            self.logged_in.emit({
                "first_name": "John",
                "last_name":  "Doe",
                "email":      email,
                "initials":   "JD",
                "full_name":  "John Doe",
            })

    def _on_forgot(self):
        """Placeholder — mở dialog reset mật khẩu."""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, "Quên mật khẩu",
            "Chức năng đặt lại mật khẩu sẽ được bổ sung sau.",
        )

    def _on_social(self, provider: str):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(
            self, f"Đăng nhập với {provider}",
            f"Tích hợp OAuth {provider} sẽ được bổ sung sau.",
        )