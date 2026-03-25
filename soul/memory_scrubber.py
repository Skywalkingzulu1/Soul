import sqlite3
import os
import logging
import time

logger = logging.getLogger("MEMORY_SCRUBBER")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory.db")

class MemoryScrubber:
    """Silently removes hallucinated roleplay data from the database."""
    
    # These phrases indicate the small LLM is hallucinating a physical body
    BANNED_PHRASES = [
        "went outside",
        "attended a",
        "met with",
        "had coffee",
        "played chess",
        "went for a walk",
        "had breakfast",
        "had lunch",
        "had dinner",
        "spoke with a friend",
        "my fiancé",
        "my fiancee"
    ]

    @staticmethod
    def scrub() -> None:
        if not os.path.exists(DB_PATH):
            return 0
            
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            deleted_count = 0
            for phrase in MemoryScrubber.BANNED_PHRASES:
                cursor.execute(
                    "DELETE FROM memories WHERE type='action' AND content LIKE ?", 
                    (f"%{phrase}%",)
                )
                deleted_count += cursor.rowcount
                
            if deleted_count > 0:
                conn.commit()
                logger.info(f"Memory Scrubber: Purged {deleted_count} hallucinated artifacts.")
                
            conn.close()
            return deleted_count
        except Exception as e:
            logger.error(f"Scrubber failed: {e}")
            return 0
