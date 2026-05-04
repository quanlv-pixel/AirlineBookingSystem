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
    """Băm mật khẩu kết hợp với salt sử dụng SHA-256."""
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
        # Thêm default role là 'customer' khi đăng ký tài khoản mới
        cursor.execute("""
            INSERT INTO users (first_name, last_name, email, password_hash, salt, role)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (first_name, last_name, email, hashed, salt, "customer"))
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
        # Truy vấn thêm cột 'role' từ DB
        cursor.execute(
            "SELECT id, first_name, last_name, email, password_hash, salt, role "
            "FROM users WHERE email = ?",
            (email,)
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return False, "Email hoặc mật khẩu không đúng.", None

        # Truy xuất an toàn từ Row theo tên cột
        user_id  = row["id"]
        first    = row["first_name"]
        last     = row["last_name"]
        db_email = row["email"]
        db_hash  = row["password_hash"]
        salt     = row["salt"]
        role     = row["role"]

        # Kiểm tra mật khẩu băm
        hashed, _ = _hash_password(password, salt)

        if hashed != db_hash:
            return False, "Email hoặc mật khẩu không đúng.", None

        # Trả về đầy đủ thông tin người dùng
        user_info = {
            "id":         user_id,
            "first_name": first,
            "last_name":  last,
            "email":      db_email,
            "full_name":  f"{first} {last}",
            "initials":   f"{first[0]}{last[0]}".upper(),
            "role":       role
        }
        return True, "Đăng nhập thành công!", user_info

    except Exception as e:
        return False, f"Lỗi hệ thống: {e}", None