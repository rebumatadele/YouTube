import json
import os

# This file will store persistent state (transcripts grouped by channel, progress, etc.)
PERSISTENCE_FILE = "data/state.json"

def load_persistent_state():
    print("DEBUG: Looking for persistence file at:", os.path.abspath(PERSISTENCE_FILE))
    if os.path.exists(PERSISTENCE_FILE):
        with open(PERSISTENCE_FILE, "r") as f:
            return json.load(f)
    else:
        return {
            "transcripts": {},  # structure: {channel: {video_title: transcript_text}}
            "download_progress": {"downloaded": 0, "total": 0},
            "failed_downloads": []
        }

def save_persistent_state(state: dict):
    target_dir = os.path.dirname(PERSISTENCE_FILE)
    os.makedirs(target_dir, exist_ok=True)
    abs_path = os.path.abspath(PERSISTENCE_FILE)
    print("DEBUG: Saving persistent state to:", abs_path)
    with open(PERSISTENCE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    if os.path.exists(PERSISTENCE_FILE):
        print("DEBUG: Saved file size (bytes):", os.path.getsize(PERSISTENCE_FILE))

def clear_persistent_state():
    """Empties the persistent state file (resets transcripts)."""
    state = {
        "transcripts": {},
        "download_progress": {"downloaded": 0, "total": 0},
        "failed_downloads": []
    }
    save_persistent_state(state)
    return state
