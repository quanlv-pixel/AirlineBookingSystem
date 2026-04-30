# database/user_dao.py
import sqlite3
from models.user import User

class UserDAO:
    def __init__(self, db_path="airline.db"):
        self.db_path = db_path

    def insert_user(self, user: User) -> bool:
        """Thêm user mới vào database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (first_name, last_name, email, password_hash, role)
                VALUES (?, ?, ?, ?, ?)
            """, (user.first_name, user.last_name, user.email, user.password_hash, user.role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Email đã tồn tại
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> User:
        """Tìm user bằng email để phục vụ Login"""
        # ... Thực thi SELECT * FROM users WHERE email = ?
        # ... Parse dữ liệu trả về thành object User() và return.