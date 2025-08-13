import json
import os

CONFIG_FILE = 'capture_area.json'

def save_history(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f)

def load_history():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None