"""
database/user_dao.py
Data Access Object — bảng users.
Mọi truy vấn liên quan đến users đều đi qua file này.
"""

from database.db import get_connection, execute_one, execute_write


# ── Kiểu trả về gọn ─────────────────────────────────────────

def _row_to_dict(row) -> dict | None:
    """Chuyển sqlite3.Row thành dict thường."""
    return dict(row) if row else None


# ── CREATE ──────────────────────────────────────────────────

def create_user(first_name: str, last_name: str, email: str,
                password_hash: str, salt: str,
                phone: str = None, role: str = "customer") -> int:
    """
    Thêm user mới vào DB.
    Trả về id vừa tạo, hoặc raise Exception nếu email đã tồn tại.
    """
    return execute_write(
        """
        INSERT INTO users (first_name, last_name, email,
                           password_hash, salt, phone, role)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (first_name, last_name, email.lower().strip(),
         password_hash, salt, phone, role)
    )


# ── READ ────────────────────────────────────────────────────

def get_user_by_id(user_id: int) -> dict | None:
    row = execute_one("SELECT * FROM users WHERE id = ?", (user_id,))
    return _row_to_dict(row)


def get_user_by_email(email: str) -> dict | None:
    row = execute_one(
        "SELECT * FROM users WHERE email = ?",
        (email.lower().strip(),)
    )
    return _row_to_dict(row)


def email_exists(email: str) -> bool:
    row = execute_one(
        "SELECT 1 FROM users WHERE email = ?",
        (email.lower().strip(),)
    )
    return row is not None


def get_all_users() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, first_name, last_name, email, phone, role, created_at "
            "FROM users ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


# ── UPDATE ──────────────────────────────────────────────────

def update_profile(user_id: int, first_name: str,
                   last_name: str, phone: str) -> bool:
    """Cập nhật thông tin cá nhân. Trả về True nếu thành công."""
    rows_affected = execute_write(
        """
        UPDATE users
        SET first_name = ?, last_name = ?, phone = ?
        WHERE id = ?
        """,
        (first_name, last_name, phone, user_id)
    )
    return rows_affected > 0


def update_password(user_id: int,
                    new_hash: str, new_salt: str) -> bool:
    rows_affected = execute_write(
        "UPDATE users SET password_hash = ?, salt = ? WHERE id = ?",
        (new_hash, new_salt, user_id)
    )
    return rows_affected > 0


def update_role(user_id: int, role: str) -> bool:
    """Thay đổi quyền: 'customer' hoặc 'admin'."""
    if role not in ("customer", "admin"):
        raise ValueError(f"Role không hợp lệ: {role}")
    rows_affected = execute_write(
        "UPDATE users SET role = ? WHERE id = ?",
        (role, user_id)
    )
    return rows_affected > 0


# ── DELETE ──────────────────────────────────────────────────

def delete_user(user_id: int) -> bool:
    rows_affected = execute_write(
        "DELETE FROM users WHERE id = ?", (user_id,)
    )
    return rows_affected > 0


# ── STATS (dùng cho admin dashboard) ───────────────────────

def count_users() -> int:
    row = execute_one("SELECT COUNT(*) AS cnt FROM users")
    return row["cnt"] if row else 0


def count_users_by_role() -> dict:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, COUNT(*) AS cnt FROM users GROUP BY role"
        ).fetchall()
    return {r["role"]: r["cnt"] for r in rows}