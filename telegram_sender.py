import time
import logging
import requests
from datetime import date
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

log = logging.getLogger(__name__)

API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"


def _send(text: str) -> bool:
    """POST a single message, retrying once if rate-limited."""
    payload = {
        "chat_id":                  TELEGRAM_CHAT_ID,
        "text":                     text,
        "disable_web_page_preview": True,
    }
    resp = requests.post(API_URL, json=payload, timeout=15)

    if resp.status_code == 200:
        return True

    if resp.status_code == 429:
        retry_after = resp.json().get("parameters", {}).get("retry_after", 30)
        log.warning(f"Rate limited — waiting {retry_after}s then retrying…")
        time.sleep(retry_after + 1)
        retry = requests.post(API_URL, json=payload, timeout=15)
        if retry.status_code == 200:
            return True
        log.error(f"Retry failed {retry.status_code}: {retry.text}")
        return False

    log.error(f"Telegram API error {resp.status_code}: {resp.text}")
    return False


def send_news_digest(all_articles: list[tuple[str, list[dict]]]) -> None:
    today = date.today().strftime("%A, %d %B %Y")
    _send(f"🗞 Daily News Digest\n{today}")

    for site_name, articles in all_articles:
        if not articles:
            log.info(f"  Skipping '{site_name}' — no articles to send.")
            continue

        _send(f"📰 {site_name}\n{'─' * 30}")
        time.sleep(1)

        for i, art in enumerate(articles, 1):
            block = f"{i}. {art['title']}\n🔗 {art['link']}"
            if art["summary"]:
                block += f"\n{art['summary']}"
            _send(block)
            time.sleep(1)  # 1s between messages stays well under Telegram's limit
