import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_STORE = os.path.join(BASE_DIR, 'json_store')

def load_watchlist():
    filepath = os.path.join(JSON_STORE, 'watchlist.json')
    if not os.path.exists(filepath):
        return []  # No watchlist exists yet
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_watchlist(watchlist):
    filepath = os.path.join(JSON_STORE, 'watchlist.json')
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(watchlist, f, indent=2)
