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
MAX_MSG_LEN = 4096   # Telegram hard limit per message


def _escape(text: str) -> str:
    """Escape special chars for Telegram MarkdownV2."""
    special = r"\_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special else c for c in text)


def _build_digest(site_name: str, articles: list[dict]) -> str:
    """Format one site's articles as a MarkdownV2 string."""
    lines = [f"📰 *{_escape(site_name)}*\n"]
    for i, art in enumerate(articles, 1):
        title   = _escape(art["title"])
        summary = _escape(art["summary"]) if art["summary"] else ""
        link    = art["link"]

        block = f"*{i}\\. [{title}]({link})*"
        if summary:
            block += f"\n_{summary}_"
        lines.append(block)

    return "\n\n".join(lines)


def _send(text: str) -> bool:
    """POST a single message. Returns True on success."""
    payload = {
        "chat_id":                  TELEGRAM_CHAT_ID,
        "text":                     text,
        "parse_mode":               "MarkdownV2",
        "disable_web_page_preview": True,
    }
    resp = requests.post(API_URL, json=payload, timeout=15)
    if resp.status_code == 200:
        return True
    log.error(f"Telegram API error {resp.status_code}: {resp.text}")
    return False


def send_news_digest(all_articles: list[tuple[str, list[dict]]]) -> None:
    """
    Send the full digest to Telegram.

    all_articles: list of (site_name, articles) tuples
    Messages are split per-site so we never exceed Telegram's 4096-char limit.
    """
    today = date.today().strftime("%A, %d %B %Y")
    header = f"🗞 *Daily News Digest*\n_{_escape(today)}_"
    _send(header)

    for site_name, articles in all_articles:
        if not articles:
            log.info(f"  Skipping '{site_name}' — no articles to send.")
            continue

        body = _build_digest(site_name, articles)

        # Split into chunks if somehow over the limit
        for chunk in _chunk(body, MAX_MSG_LEN):
            _send(chunk)


def _chunk(text: str, size: int) -> list[str]:
    """Split text into chunks of at most `size` characters."""
    return [text[i:i + size] for i in range(0, len(text), size)]
