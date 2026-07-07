# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#          ✨ AYAAN AI ✨
#       User Data Persistence
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

import os
import json
import threading
import config

_lock = threading.Lock()


def _user_path(user_id: str) -> str:
    """Get the file path for a user's data."""
    os.makedirs(config.USERS_DIR, exist_ok=True)
    return os.path.join(config.USERS_DIR, f"{user_id}.json")


def _default_data(username: str = "unknown") -> dict:
    """Default user data template."""
    return {
        "username": username,
        "trivia_wins": 0,
        "trivia_played": 0,
        "guess_wins": 0,
        "guess_played": 0,
        "scramble_wins": 0,
        "scramble_played": 0,
        "rps_wins": 0,
        "rps_played": 0,
        "total_score": 0,
        "streak": 0,
        "messages": 0,
        "joined": "",
    }


def get_user(user_id: str, username: str = "unknown") -> dict:
    """Load user data from disk, creating if needed."""
    path = _user_path(user_id)
    with _lock:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Merge any new default keys
                for k, v in _default_data(username).items():
                    if k not in data:
                        data[k] = v
                return data
        else:
            data = _default_data(username)
            _save_raw(path, data)
            return data


def save_user(user_id: str, data: dict):
    """Persist user data to disk."""
    path = _user_path(user_id)
    with _lock:
        _save_raw(path, data)


def _save_raw(path: str, data: dict):
    """Write data to file (must be called within lock)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_score(user_id: str, game: str, points: int = 1, username: str = "unknown"):
    """Increment a game's win count and total score."""
    data = get_user(user_id, username)
    win_key = f"{game}_wins"
    play_key = f"{game}_played"
    if win_key in data:
        data[win_key] += 1
    if play_key in data:
        data[play_key] += 1
    data["total_score"] += points
    data["streak"] += 1
    save_user(user_id, data)
    return data


def add_loss(user_id: str, game: str, username: str = "unknown"):
    """Increment played count and reset streak."""
    data = get_user(user_id, username)
    play_key = f"{game}_played"
    if play_key in data:
        data[play_key] += 1
    data["streak"] = 0
    save_user(user_id, data)
    return data


def get_leaderboard(limit: int = 10) -> list:
    """Get top players sorted by total_score."""
    os.makedirs(config.USERS_DIR, exist_ok=True)
    players = []
    for fname in os.listdir(config.USERS_DIR):
        if not fname.endswith(".json"):
            continue
        try:
            with open(os.path.join(config.USERS_DIR, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("total_score", 0) > 0:
                    players.append((data.get("username", "???"), data["total_score"]))
        except Exception:
            continue

    players.sort(key=lambda x: x[1], reverse=True)
    return players[:limit]
