"""Session persistence — save and load browser login states.

Uses Playwright's storage_state to persist cookies, localStorage,
and IndexedDB across sessions.
"""

import json
import os
import logging
import time

logger = logging.getLogger(__name__)

SESSIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sessions")


def ensure_sessions_dir() -> None:
    os.makedirs(SESSIONS_DIR, exist_ok=True)


def get_session_path(name) -> None:
    """Get the file path for a named session."""
    ensure_sessions_dir()
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower())
    return os.path.join(SESSIONS_DIR, f"{safe_name}.json")


async def save_session(context, name) -> None:
    """Save browser session state to disk."""
    path = get_session_path(name)
    state = await context.storage_state()

    with open(path, "w") as f:
        json.dump(state, f, indent=2)

    # Also save metadata
    meta_path = path.replace(".json", "_meta.json")
    meta = {
        "name": name,
        "saved_at": time.time(),
        "saved_at_readable": time.strftime("%Y-%m-%d %H:%M:%S"),
        "cookies_count": len(state.get("cookies", [])),
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)

    logger.info(f"Session saved: {name} ({meta['cookies_count']} cookies)")
    return path


def load_session(name) -> None:
    """Load session state from disk. Returns path or None."""
    path = get_session_path(name)
    if os.path.exists(path):
        logger.info(f"Session loaded: {name}")
        return path
    logger.info(f"No saved session: {name}")
    return None


def list_sessions() -> None:
    """List all saved sessions with metadata."""
    ensure_sessions_dir()
    sessions = []
    for f in os.listdir(SESSIONS_DIR):
        if f.endswith("_meta.json"):
            meta_path = os.path.join(SESSIONS_DIR, f)
            try:
                with open(meta_path) as fh:
                    meta = json.load(fh)
                    sessions.append(meta)
            except Exception:
                pass
    return sorted(sessions, key=lambda s: s.get("saved_at", 0), reverse=True)


def delete_session(name) -> None:
    """Delete a saved session."""
    path = get_session_path(name)
    meta_path = path.replace(".json", "_meta.json")
    for p in [path, meta_path]:
        if os.path.exists(p):
            os.remove(p)
            logger.info(f"Deleted: {p}")


def has_session(name) -> None:
    """Check if a session exists."""
    return os.path.exists(get_session_path(name))
