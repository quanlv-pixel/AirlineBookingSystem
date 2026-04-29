"""
modules/auth.py
Xử lý đăng ký, đăng nhập và quản lý phiên người dùng.
"""

import hashlib
import secrets
import re
from database.db import get_connection


# ─── Helpers ───────────────────────────────────────────────────────────────

def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Trả về (hashed_password, salt)."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt


def _validate_email(email: str) -> bool:
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def _validate_password(password: str) -> tuple[bool, str]:
    """Trả về (is_valid, error_message)."""
    if len(password) < 6:
        return False, "Mật khẩu phải có ít nhất 6 ký tự."
    return True, ""


# ─── Database Setup ────────────────────────────────────────────────────────

def ensure_users_table():
    """Tạo bảng users nếu chưa tồn tại."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name    TEXT    NOT NULL,
            last_name     TEXT    NOT NULL,
            email         TEXT    NOT NULL UNIQUE,
            password_hash TEXT    NOT NULL,
            salt          TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()


# ─── Register ──────────────────────────────────────────────────────────────

def register_user(first_name: str, last_name: str,
                  email: str, password: str) -> tuple[bool, str]:
    """
    Đăng ký người dùng mới.
    Trả về (success: bool, message: str).
    """
    first_name = first_name.strip()
    last_name  = last_name.strip()
    email      = email.strip().lower()

    if not first_name or not last_name:
        return False, "Vui lòng nhập đầy đủ họ và tên."

    if not _validate_email(email):
        return False, "Địa chỉ email không hợp lệ."

    valid_pw, pw_err = _validate_password(password)
    if not valid_pw:
        return False, pw_err

    hashed, salt = _hash_password(password)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, password_hash, salt)
            VALUES (?, ?, ?, ?, ?)
        """, (first_name, last_name, email, hashed, salt))
        conn.commit()
        conn.close()
        return True, "Đăng ký thành công!"
    except Exception as e:
        if "UNIQUE" in str(e):
            return False, "Email này đã được đăng ký."
        return False, f"Lỗi hệ thống: {e}"


# ─── Login ─────────────────────────────────────────────────────────────────

def login_user(email: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Đăng nhập người dùng.
    Trả về (success, message, user_info_dict | None).
    """
    email = email.strip().lower()

    if not email or not password:
        return False, "Vui lòng nhập email và mật khẩu.", None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, first_name, last_name, email, password_hash, salt "
            "FROM users WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return False, "Email hoặc mật khẩu không đúng.", None

        user_id, first, last, db_email, db_hash, salt = row
        hashed, _ = _hash_password(password, salt)

        if hashed != db_hash:
            return False, "Email hoặc mật khẩu không đúng.", None

        user_info = {
            "id":         user_id,
            "first_name": first,
            "last_name":  last,
            "email":      db_email,
            "full_name":  f"{first} {last}",
            "initials":   f"{first[0]}{last[0]}".upper(),
        }
        return True, "Đăng nhập thành công!", user_info

    except Exception as e:
        return False, f"Lỗi hệ thống: {e}", None