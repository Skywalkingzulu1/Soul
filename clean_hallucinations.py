import sqlite3

db_path = "memory.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Delete the hallucination
cursor.execute("DELETE FROM memories WHERE content LIKE '%integrating blockchain technology with chess AI%'")
deleted_count = cursor.rowcount
conn.commit()

# Also check for any other 'chess AI' or 'chess platform' claims
cursor.execute("DELETE FROM memories WHERE content LIKE '%decentralized chess platform%'")
deleted_count += cursor.rowcount
conn.commit()

print(f"Cleaned up {deleted_count} hallucinated memories.")
conn.close()
