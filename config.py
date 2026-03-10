"""
Configuration loader.
Credentials are read from .env — never hardcode them here.
Site definitions are in sites.json.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Telegram (fill in .env) ─────────────────────────────────────────────────
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Schedule ─────────────────────────────────────────────────────────────────
SEND_TIME = os.getenv("SEND_TIME", "08:00")          # 24-hour HH:MM

# ── Scraping limits ──────────────────────────────────────────────────────────
MAX_ARTICLES_PER_SITE = int(os.getenv("MAX_ARTICLES", "5"))

# ── Validation ───────────────────────────────────────────────────────────────
if not TELEGRAM_TOKEN:
    raise EnvironmentError("❌  TELEGRAM_TOKEN is missing from your .env file.")
if not TELEGRAM_CHAT_ID:
    raise EnvironmentError("❌  TELEGRAM_CHAT_ID is missing from your .env file.")


def load_sites() -> list[dict]:
    """Load site selector configs from sites.json."""
    path = Path(__file__).parent / "sites.json"
    if not path.exists():
        raise FileNotFoundError("sites.json not found. Copy sites.json.example → sites.json and edit it.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)
