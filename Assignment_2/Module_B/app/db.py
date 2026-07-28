import os
import shutil
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
ASSIGNMENT1_DB = BASE_DIR / "Assignment_1" / "project.db"
LOCAL_DB = Path(__file__).resolve().parent / "sports_club.db"
DUMP_PATH = Path(__file__).resolve().parent.parent / "sql" / "project_dump.sql"
SCHEMA_PATH = Path(__file__).resolve().parent.parent / "sql" / "core_tables.sql"
INDEX_PATH = Path(__file__).resolve().parent.parent / "sql" / "indexes.sql"


def _local_db_has_current_schema() -> bool:
    if not LOCAL_DB.exists():
        return False

    try:
        conn = sqlite3.connect(str(LOCAL_DB), timeout=1)
        columns = [row[1] for row in conn.execute("PRAGMA table_info(Event)").fetchall()]
        conn.close()
        return "Status" in columns and "Facility_ID" not in columns
    except sqlite3.DatabaseError:
        return False


def get_db_path():
    if ASSIGNMENT1_DB.exists():
        try:
            if (not LOCAL_DB.exists()) or not _local_db_has_current_schema():
                shutil.copy2(ASSIGNMENT1_DB, LOCAL_DB)
                print(f"[DB] Copied Assignment 1 database to {LOCAL_DB}")
        except Exception as e:
            print(f"[DB] Copy warning: {e}")

    if LOCAL_DB.exists():
        try:
            conn = sqlite3.connect(str(LOCAL_DB), timeout=1)
            conn.execute("SELECT 1")
            conn.close()
            return str(LOCAL_DB)
        except sqlite3.OperationalError:
            pass

    return str(LOCAL_DB)


def get_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("PRAGMA busy_timeout = 30000")

    try:
        existing = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='Member'"
        ).fetchone()

        if not existing and os.path.exists(DUMP_PATH):
            with open(DUMP_PATH, "r", encoding="utf-8") as f:
                sql = f.read()
            try:
                conn.executescript(sql)
                print("[DB] Project dump loaded.")
            except Exception as e:
                print(f"[DB] Dump error: {e}")

        if os.path.exists(SCHEMA_PATH):
            with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
                sql = f.read()
            try:
                conn.executescript(sql)
            except Exception as e:
                print(f"[DB] Core tables error: {e}")

        if os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, "r", encoding="utf-8") as f:
                sql = f.read()
            try:
                conn.executescript(sql)
            except Exception as e:
                print(f"[DB] Index error: {e}")

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS Attendance (
            Member_ID TEXT NOT NULL,
            Session TEXT NOT NULL,
            Date TEXT NOT NULL,
            Status TEXT NOT NULL CHECK(Status IN ('Present','Absent')),
            PRIMARY KEY(Member_ID, Session, Date),
            FOREIGN KEY(Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
        );

        CREATE VIEW IF NOT EXISTS Player_Stat AS
        SELECT Member_ID, Event_ID, Metric_Name, Metric_Value, Recorded_Date
        FROM Performance;

        CREATE TABLE IF NOT EXISTS RevokedToken (
            Token      TEXT PRIMARY KEY,
            Revoked_At TEXT DEFAULT (datetime('now')),
            Expires_At TEXT NOT NULL
        );
        """)

        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
        print(f"[DB] Database initialized successfully at {db_path}.")
    finally:
        conn.close()


def ensure_revoked_token_table():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS RevokedToken (
                Token      TEXT PRIMARY KEY,
                Revoked_At TEXT DEFAULT (datetime('now')),
                Expires_At TEXT NOT NULL
            );
        """)
        conn.commit()
    finally:
        conn.close()
