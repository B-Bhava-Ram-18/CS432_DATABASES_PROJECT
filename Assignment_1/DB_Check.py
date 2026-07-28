import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "project.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
SELECT name FROM sqlite_master
WHERE type='table' AND name NOT LIKE 'sqlite_%'
ORDER BY name;
""")

tables = cursor.fetchall()

for (table_name,) in tables:
    print("\n" + "=" * 60)
    print(f"TABLE: {table_name}")
    print("=" * 60)

    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()

    column_names = [description[0] for description in cursor.description]
    print("Columns:", column_names)
    for row in rows:
        print(row)

print("\n" + "=" * 60)
print("FOREIGN KEY CHECK")
print("=" * 60)

for violation in cursor.execute("PRAGMA foreign_key_check;").fetchall():
    print(violation)


conn.close()
