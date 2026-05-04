"""
database/db.py
Kết nối SQLite + khởi tạo schema.
Chỉ dùng thư viện có sẵn của Python — không cần cài thêm gì.
"""

import sqlite3
import os

_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_ROOT, "database", "airline.db")

# ─── Schema (toàn bộ DDL) ───────────────────────────────────────────────────

_SCHEMA = """
PRAGMA foreign_keys = ON;
PRAGMA journal_mode  = WAL;

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    TEXT    NOT NULL,
    last_name     TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    salt          TEXT    NOT NULL,
    phone         TEXT,
    role          TEXT    NOT NULL DEFAULT 'customer',
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS airports (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    code    TEXT    NOT NULL UNIQUE,
    name    TEXT    NOT NULL,
    city    TEXT    NOT NULL,
    country TEXT    NOT NULL DEFAULT 'Vietnam'
);

CREATE TABLE IF NOT EXISTS aircraft (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    model       TEXT    NOT NULL,
    total_seats INTEGER NOT NULL,
    seat_layout TEXT    NOT NULL DEFAULT '3-3'
);

CREATE TABLE IF NOT EXISTS flights (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_number  TEXT    NOT NULL UNIQUE,
    aircraft_id    INTEGER NOT NULL REFERENCES aircraft(id),
    origin_id      INTEGER NOT NULL REFERENCES airports(id),
    destination_id INTEGER NOT NULL REFERENCES airports(id),
    departure_time TEXT    NOT NULL,
    arrival_time   TEXT    NOT NULL,
    price_eco      REAL    NOT NULL,
    price_business REAL    NOT NULL,
    status         TEXT    NOT NULL DEFAULT 'scheduled',
    CHECK (origin_id != destination_id),
    CHECK (price_eco > 0),
    CHECK (price_business >= price_eco)
);

CREATE TABLE IF NOT EXISTS bookings (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_code TEXT    NOT NULL UNIQUE,
    user_id      INTEGER NOT NULL REFERENCES users(id),
    flight_id    INTEGER NOT NULL REFERENCES flights(id),
    class        TEXT    NOT NULL DEFAULT 'eco',
    total_price  REAL    NOT NULL,
    status       TEXT    NOT NULL DEFAULT 'pending',
    booked_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS passengers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id    INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    full_name     TEXT    NOT NULL,
    id_number     TEXT    NOT NULL,
    date_of_birth TEXT,
    nationality   TEXT    NOT NULL DEFAULT 'Vietnamese'
);

CREATE TABLE IF NOT EXISTS tickets (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id   INTEGER NOT NULL REFERENCES bookings(id)   ON DELETE CASCADE,
    passenger_id INTEGER NOT NULL REFERENCES passengers(id) ON DELETE CASCADE,
    seat_number  TEXT    NOT NULL,
    ticket_code  TEXT    NOT NULL UNIQUE,
    status       TEXT    NOT NULL DEFAULT 'active',
    UNIQUE (booking_id, seat_number)
);

CREATE INDEX IF NOT EXISTS idx_flights_route   ON flights(origin_id, destination_id, departure_time);
CREATE INDEX IF NOT EXISTS idx_bookings_user   ON bookings(user_id);
CREATE INDEX IF NOT EXISTS idx_passengers_book ON passengers(booking_id);
CREATE INDEX IF NOT EXISTS idx_tickets_booking ON tickets(booking_id);
"""

# ─── Seed data ───────────────────────────────────────────────────────────────

_SEED = """
INSERT OR IGNORE INTO airports (code, name, city, country) VALUES
    ('SGN', 'Tân Sơn Nhất', 'Hồ Chí Minh', 'Vietnam'),
    ('HAN', 'Nội Bài',      'Hà Nội',       'Vietnam'),
    ('DAD', 'Đà Nẵng',      'Đà Nẵng',      'Vietnam'),
    ('CXR', 'Cam Ranh',     'Nha Trang',    'Vietnam'),
    ('HPH', 'Cát Bi',       'Hải Phòng',    'Vietnam'),
    ('PQC', 'Phú Quốc',     'Phú Quốc',     'Vietnam'),
    ('BKK', 'Suvarnabhumi', 'Bangkok',      'Thailand'),
    ('SIN', 'Changi',       'Singapore',    'Singapore'),
    ('NRT', 'Narita',       'Tokyo',        'Japan');

INSERT OR IGNORE INTO aircraft (model, total_seats, seat_layout) VALUES
    ('Airbus A321',  180, '3-3'),
    ('Boeing 737',   162, '3-3'),
    ('Airbus A350',  306, '2-4-2'),
    ('ATR 72',        70, '2-2');

INSERT OR IGNORE INTO flights
    (flight_number, aircraft_id, origin_id, destination_id,
     departure_time, arrival_time, price_eco, price_business, status)
SELECT 'SBA001', a.id, o.id, d.id,
       '2026-10-24 06:00', '2026-10-24 08:10', 899000, 2500000, 'scheduled'
FROM aircraft a, airports o, airports d
WHERE a.model='Airbus A321' AND o.code='SGN' AND d.code='HAN';

INSERT OR IGNORE INTO flights
    (flight_number, aircraft_id, origin_id, destination_id,
     departure_time, arrival_time, price_eco, price_business, status)
SELECT 'SBA002', a.id, o.id, d.id,
       '2026-10-24 09:00', '2026-10-24 11:10', 899000, 2500000, 'scheduled'
FROM aircraft a, airports o, airports d
WHERE a.model='Airbus A321' AND o.code='HAN' AND d.code='SGN';

INSERT OR IGNORE INTO flights
    (flight_number, aircraft_id, origin_id, destination_id,
     departure_time, arrival_time, price_eco, price_business, status)
SELECT 'SBA003', a.id, o.id, d.id,
       '2026-10-24 07:30', '2026-10-24 08:50', 650000, 1800000, 'scheduled'
FROM aircraft a, airports o, airports d
WHERE a.model='Boeing 737' AND o.code='SGN' AND d.code='DAD';

INSERT OR IGNORE INTO flights
    (flight_number, aircraft_id, origin_id, destination_id,
     departure_time, arrival_time, price_eco, price_business, status)
SELECT 'SBA004', a.id, o.id, d.id,
       '2026-10-24 23:00', '2026-10-25 07:30', 4500000, 12000000, 'scheduled'
FROM aircraft a, airports o, airports d
WHERE a.model='Airbus A350' AND o.code='SGN' AND d.code='NRT';
"""


# ─── Khởi tạo DB ─────────────────────────────────────────────────────────────

def init_db(seed: bool = True) -> None:
    """
    Tạo tất cả bảng nếu chưa có.
    Gọi 1 lần trong main.py khi app khởi động.

    Args:
        seed: Nếu True, chèn dữ liệu mẫu airports / aircraft / flights.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(_SCHEMA)
        if seed:
            conn.executescript(_SEED)
        conn.commit()
        print(f"[db] Database sẵn sàng: {DB_PATH}")
    except Exception as e:
        print(f"[db] Lỗi khởi tạo: {e}")
        raise
    finally:
        conn.close()


# ─── Helpers kết nối ─────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """Trả về Connection mới, row_factory = sqlite3.Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def fetchall(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    """Chạy SELECT, trả về danh sách Row (truy cập theo tên cột)."""
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def fetchone(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    """Chạy SELECT, trả về 1 Row hoặc None."""
    with get_connection() as conn:
        return conn.execute(sql, params).fetchone()


def execute(sql: str, params: tuple = ()) -> int:
    """
    Chạy INSERT / UPDATE / DELETE.
    Trả về lastrowid (INSERT) hoặc rowcount (UPDATE/DELETE).
    """
    with get_connection() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid or cur.rowcount


# ─── Chạy thử trực tiếp ──────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db(seed=True)

    print("\n── Airports ──────────────────────────")
    for r in fetchall("SELECT code, city FROM airports ORDER BY code"):
        print(f"  {r['code']}  {r['city']}")

    print("\n── Flights ───────────────────────────")
    for r in fetchall("SELECT flight_number, status FROM flights"):
        print(f"  {r['flight_number']}  {r['status']}")

