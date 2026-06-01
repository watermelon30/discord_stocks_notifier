import json
import os
from dotenv import load_dotenv

load_dotenv()

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


def load_config() -> dict:
    """Load config from config.json, with webhook_url sourced from .env."""
    if not os.path.exists(CONFIG_FILE):
        config = DEFAULT_CONFIG.copy()
    else:
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        except Exception:
            config = DEFAULT_CONFIG.copy()

    # Always prefer .env for webhook_url (keeps secrets out of config.json)
    env_webhook = os.getenv("DISCORD_WEBHOOK_URL", "")
    if env_webhook:
        config["webhook_url"] = env_webhook

    return config


def save_config(config: dict) -> bool:
    """Save config to config.json, excluding webhook_url (stored in .env)."""
    # Don't persist webhook_url to config.json — it lives in .env
    config_to_save = {k: v for k, v in config.items() if k != "webhook_url"}
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_to_save, f, indent=4)
        return True
    except Exception:
        return False
