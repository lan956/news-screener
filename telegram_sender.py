"""
telegram_sender.py  —  Format and send the news digest via Telegram Bot API.

Uses plain requests (no extra library needed) to POST to the sendMessage endpoint.
Messages are formatted in Markdown V2 so titles are bold and links are clickable.
"""

import logging
import requests
from datetime import date
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

log = logging.getLogger(__name__)

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
MAX_MSG_LEN = 4096


def _build_digest(site_name: str, articles: list[dict]) -> str:
    """Format one site's articles as plain text."""
    lines = [f"📰 {site_name}\n{'─' * 30}"]
    for i, art in enumerate(articles, 1):
        block = f"{i}. {art['title']}\n🔗 {art['link']}"
        if art["summary"]:
            block += f"\n{art['summary']}"
        lines.append(block)
    return "\n\n".join(lines)


def _send(text: str) -> bool:
    """POST a single message. Returns True on success."""
    payload = {
        "chat_id":                  TELEGRAM_CHAT_ID,
        "text":                     text,
        "disable_web_page_preview": True,
    }
    resp = requests.post(API_URL, json=payload, timeout=15)
    if resp.status_code == 200:
        return True
    log.error(f"Telegram API error {resp.status_code}: {resp.text}")
    return False


def send_news_digest(all_articles: list[tuple[str, list[dict]]]) -> None:
    today = date.today().strftime("%A, %d %B %Y")
    _send(f"🗞 Daily News Digest\n{today}")

    for site_name, articles in all_articles:
        if not articles:
            log.info(f"  Skipping '{site_name}' — no articles to send.")
            continue

        # Send each article individually to avoid length issues
        header = f"📰 {site_name}\n{'─' * 30}"
        _send(header)

        for i, art in enumerate(articles, 1):
            block = f"{i}. {art['title']}\n🔗 {art['link']}"
            if art["summary"]:
                block += f"\n{art['summary']}"
            _send(block)
