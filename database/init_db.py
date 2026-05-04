"""
database/init_db.py
Khởi tạo airline.db từ schema.sql.
Chạy 1 lần duy nhất khi cài đặt dự án.
"""

import sqlite3
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH    = os.path.join(_ROOT, "database", "airline.db")
SCHEMA_PATH = os.path.join(_ROOT, "database", "schema.sql")


def init_database(force: bool = False) -> None:
    """
    Tạo database và chạy schema.sql.

    Args:
        force: Nếu True, xoá DB cũ rồi tạo lại từ đầu.
    """
    if force and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"[init_db] Đã xoá DB cũ: {DB_PATH}")

    if not os.path.exists(SCHEMA_PATH):
        print(f"[init_db] Không tìm thấy schema.sql tại: {SCHEMA_PATH}")
        sys.exit(1)

    with open(SCHEMA_PATH, encoding="utf-8") as f:
        sql_script = f.read()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.executescript(sql_script)
        conn.commit()
        print(f"[init_db] ✅ Database khởi tạo thành công: {DB_PATH}")
        _print_summary(conn)
    except Exception as e:
        print(f"[init_db] ❌ Lỗi: {e}")
        raise
    finally:
        conn.close()


def _print_summary(conn: sqlite3.Connection) -> None:
    """In tóm tắt số bản ghi seed."""
    tables = ["users", "airports", "aircraft", "flights",
              "bookings", "passengers", "tickets"]
    print("\n── Tóm tắt dữ liệu ──────────────────")
    for t in tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            print(f"  {t:<15} {count:>4} bản ghi")
        except Exception:
            pass
    print("─────────────────────────────────────\n")


if __name__ == "__main__":
    # python database/init_db.py          → tạo mới nếu chưa có
    # python database/init_db.py --force  → xoá và tạo lại
    force_flag = "--force" in sys.argv
    init_database(force=force_flag)