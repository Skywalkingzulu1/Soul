import sqlite3
import uuid
import time

db_path = "memory.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

actions = [
    "Built a modern web interface for Andile using FastAPI and Vanilla JS.",
    "Integrated a dynamic image avatar using super_agent_test.png.",
    "Corrected AI hallucinations about a 'chess blockchain project'.",
    "Enhanced long-term memory to specifically track and recall my daily actions.",
    "Cleaned up memory.db to remove inaccurate chess-related project claims."
]

for action in actions:
    mem_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO memories (id, type, content, importance, timestamp) VALUES (?, ?, ?, ?, ?)",
        (mem_id, "action", action, 0.9, time.time())
    )

conn.commit()
print(f"Injected {len(actions)} recent actions into memory.")
conn.close()
