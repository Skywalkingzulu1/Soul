import sqlite3
import os

db_path = "memory.db"
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- RECENT MEMORIES ---")
cursor.execute("SELECT type, content FROM memories WHERE content LIKE '%chess%' OR content LIKE '%blockchain%' LIMIT 10")
for row in cursor.fetchall():
    print(f"[{row[0]}] {row[1]}")

print("\n--- RECENT CONVERSATIONS ---")
cursor.execute("SELECT role, content FROM conversations WHERE content LIKE '%chess%' OR content LIKE '%blockchain%' LIMIT 10")
for row in cursor.fetchall():
    print(f"[{row[0]}] {row[1]}")

print("\n--- IDENTITY ENTRIES ---")
cursor.execute("SELECT key, value FROM identity WHERE value LIKE '%chess%' OR value LIKE '%blockchain%'")
for row in cursor.fetchall():
    print(f"[{row[0]}] {row[1]}")

conn.close()
