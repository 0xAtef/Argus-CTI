# src/utils.py

import json
from pathlib import Path
from typing import Set

SEEN_PATH = Path("data/processed/seen.json")

def load_seen_ids() -> Set[str]:
    """
    Load the set of already-processed entry IDs from disk.
    """
    if not SEEN_PATH.exists():
        return set()
    try:
        with SEEN_PATH.open() as f:
            data = json.load(f)
        return set(data)
    except Exception:
        return set()

def save_seen_ids(seen: Set[str]):
    """
    Save the updated set of processed entry IDs back to disk.
    """
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SEEN_PATH.open("w") as f:
        json.dump(sorted(seen), f, indent=2)
