import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "localhub.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name;
""")

tables = cursor.fetchall()

for table in tables:
    table_name = table[0]

    if table_name == "sqlite_sequence":
        continue

    print(f"\n[{table_name}] 테이블 구조")
    print("-" * 40)

    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    for column in columns:
        cid, name, col_type, notnull, default_value, pk = column
        pk_text = "PK" if pk else ""
        notnull_text = "NOT NULL" if notnull else ""
        print(f"{name:25} {col_type:15} {notnull_text:10} {pk_text}")

conn.close()