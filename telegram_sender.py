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


def _escape(text: str) -> str:
    """Escape special HTML characters."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_digest(site_name: str, articles: list[dict]) -> str:
    """Format one site's articles as an HTML string."""
    lines = [f"📰 <b>{_escape(site_name)}</b>\n"]
    for i, art in enumerate(articles, 1):
        title   = _escape(art["title"])
        summary = _escape(art["summary"]) if art["summary"] else ""
        link    = art["link"]

        block = f'<b>{i}. <a href="{link}">{title}</a></b>'
        if summary:
            block += f"\n<i>{summary}</i>"
        lines.append(block)

    return "\n\n".join(lines)


def _send(text: str) -> bool:
    """POST a single message. Returns True on success."""
    payload = {
        "chat_id":                  TELEGRAM_CHAT_ID,
        "text":                     text,
        "parse_mode":               "HTML",
        "disable_web_page_preview": True,
    }
    resp = requests.post(API_URL, json=payload, timeout=15)
    if resp.status_code == 200:
        return True
    log.error(f"Telegram API error {resp.status_code}: {resp.text}")
    return False


def send_news_digest(all_articles: list[tuple[str, list[dict]]]) -> None:
    today = date.today().strftime("%A, %d %B %Y")
    _send(f"🗞 <b>Daily News Digest</b>\n<i>{_escape(today)}</i>")

    for site_name, articles in all_articles:
        if not articles:
            log.info(f"  Skipping '{site_name}' — no articles to send.")
            continue

        body = _build_digest(site_name, articles)
        for chunk in _chunk(body, MAX_MSG_LEN):
            _send(chunk)


def _chunk(text: str, size: int) -> list[str]:
    return [text[i:i + size] for i in range(0, len(text), size)]
