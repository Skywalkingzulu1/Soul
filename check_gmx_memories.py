import sqlite3
import os

db_path = "memory.db"
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("--- RECENT GMX MEMORIES ---")
cur.execute("SELECT type, content, timestamp FROM memories WHERE content LIKE '%gmx%' OR type LIKE '%gmx%' ORDER BY timestamp DESC LIMIT 10")
for row in cur.fetchall():
    print(f"[{row[2]}] Type: {row[0]}")
    print(f"Content: {row[1][:200]}...")
    print("-" * 20)

print("\n--- RECENT GMX CONVERSATIONS ---")
cur.execute("SELECT role, content, timestamp FROM conversations WHERE content LIKE '%gmx%' ORDER BY timestamp DESC LIMIT 10")
for row in cur.fetchall():
    print(f"[{row[2]}] Role: {row[0]}")
    print(f"Content: {row[1][:200]}...")
    print("-" * 20)

conn.close()
