"""
main.py  —  NewsBot entry point.

Usage
─────
  python main.py              # runs immediately, then every day at SEND_TIME
  python main.py --now        # run once and exit (useful for cron jobs)

Scheduling
──────────
  Set SEND_TIME=HH:MM in your .env (default: 08:00).
  Or use your OS scheduler (cron / Task Scheduler) with --now flag.
"""

import sys
import logging
import schedule
import time

from config     import load_sites, SEND_TIME
from scraper    import scrape_site
from telegram_sender import send_news_digest

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(message)s",
    handlers=[
        logging.FileHandler("newsbot.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


# ── Core job ──────────────────────────────────────────────────────────────────
def run_job() -> None:
    log.info("═" * 50)
    log.info("Starting daily news digest…")

    sites        = load_sites()
    all_articles = []

    for site in sites:
        log.info(f"  Scraping → {site['name']}  ({site['url']})")
        try:
            articles = scrape_site(site)
            log.info(f"    ✓ {len(articles)} article(s) found")
            all_articles.append((site["name"], articles))
        except Exception as exc:
            log.error(f"    ✗ Failed: {exc}", exc_info=True)

    if any(arts for _, arts in all_articles):
        send_news_digest(all_articles)
        log.info("Digest sent to Telegram.")
    else:
        log.warning("No articles scraped — nothing sent.")

    log.info("═" * 50)


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    one_shot = "--now" in sys.argv

    if one_shot:
        run_job()
    else:
        log.info(f"NewsBot started. Daily digest scheduled at {SEND_TIME}.")
        run_job()                                   # run immediately on start

        schedule.every().day.at(SEND_TIME).do(run_job)
        while True:
            schedule.run_pending()
            time.sleep(30)
