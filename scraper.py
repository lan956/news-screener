"""
scraper.py  —  Fetch & parse news articles using Scrapling.

Scrapling's Fetcher automatically sets realistic browser headers and
supports TLS fingerprint impersonation, so most news sites work without
extra configuration.

Each entry in sites.json must provide CSS selectors tuned for that site.
See sites.json.example for guidance on finding the right selectors.
"""

import logging
from scrapling.fetchers import Fetcher
from config import MAX_ARTICLES_PER_SITE

log = logging.getLogger(__name__)


def scrape_site(site: dict) -> list[dict]:
    """
    Scrape one site and return up to MAX_ARTICLES_PER_SITE articles.

    Expected site config keys
    ─────────────────────────
    name          Display name shown in the Telegram digest
    url           URL of the page to scrape (listing / homepage)
    article_sel   CSS selector that matches each article card/block
    title_sel     CSS selector for the headline inside the card
    summary_sel   CSS selector for the snippet/description (optional)
    link_sel      CSS selector for the <a> element inside the card
                  (omit to use the first <a> found)
    base_url      Prepended to relative hrefs  (optional, e.g. "https://example.com")
    impersonate   Browser fingerprint to spoof: "chrome", "firefox", etc.
                  (optional, defaults to "chrome")
    """
    url         = site["url"]
    article_sel = site["article_sel"]
    title_sel   = site["title_sel"]
    summary_sel = site.get("summary_sel")
    link_sel    = site.get("link_sel", "a")
    base_url    = site.get("base_url", "").rstrip("/")
    impersonate = site.get("impersonate", "chrome")

    # ── Fetch ────────────────────────────────────────────────────────────────
    page = Fetcher.get(
        url,
        stealthy_headers=True,   # randomise Accept-Language, sec-ch-ua, etc.
        impersonate=impersonate,  # match TLS fingerprint to the chosen browser
        timeout=20,
    )

    articles_raw = page.css(article_sel)
    if not articles_raw:
        log.warning(f"[{site['name']}] article_sel '{article_sel}' matched 0 elements.")
        return []

    results = []
    for card in articles_raw[:MAX_ARTICLES_PER_SITE]:
        # ── Headline ─────────────────────────────────────────────────────────
        title_el = card.css(title_sel)
        title    = title_el.get_text(separator=" ").strip() if title_el else None
        if not title:
            continue                              # skip cards without a headline

        # ── Summary (optional) ───────────────────────────────────────────────
        summary = None
        if summary_sel:
            summary_el = card.css(summary_sel)
            summary    = summary_el.get_text(separator=" ").strip() if summary_el else None

        # ── Link ─────────────────────────────────────────────────────────────
        link = None
        link_el = card.css(link_sel)
        if link_el:
            href = link_el.attrib.get("href", "")
            if href:
                link = href if href.startswith("http") else f"{base_url}/{href.lstrip('/')}"

        results.append({
            "title":   title,
            "summary": summary or "",
            "link":    link    or url,    # fall back to section URL if no link found
        })

    return results
