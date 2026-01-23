import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "tickers": ["AAPL", "MSFT", "GOOGL", "TSLA", "SPY"],
    "webhook_url": "",
    "groups": [
        {
            "name": "Oversold RSI < 30",
            "logic": "AND",
            "conditions": [
                {"indicator": "RSI", "period": 14, "operator": "<", "value": 30}
            ]
        }
    ]
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        return True
    except Exception:
        return False
