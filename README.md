# NewsBot 🗞

A daily news scraper that pulls headlines + summaries from any website and
forwards them to a Telegram chat. Built with **Scrapling** for fast,
anti-bot-friendly scraping.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
scrapling install        # downloads browser fingerprints
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable          | Where to get it                                      |
|-------------------|------------------------------------------------------|
| `TELEGRAM_TOKEN`  | Message [@BotFather](https://t.me/BotFather) → `/newbot` |
| `TELEGRAM_CHAT_ID`| Message [@userinfobot](https://t.me/userinfobot)     |
| `SEND_TIME`       | HH:MM in your server's local timezone (default 08:00)|
| `MAX_ARTICLES`    | Articles per site per digest (default 5)             |

### 3. Add news sites

```bash
cp sites.json.example sites.json
```

Edit `sites.json`. Each site needs four CSS selectors:

| Key            | What it targets                                  |
|----------------|--------------------------------------------------|
| `article_sel`  | The container wrapping each article card         |
| `title_sel`    | The headline element inside the card             |
| `summary_sel`  | The snippet/description (optional)               |
| `link_sel`     | The `<a>` tag with the article URL               |
| `base_url`     | Prefix for relative links (e.g. `https://site.com`) |

**Tip:** Open DevTools (F12) → Inspector, hover over an article card,
right-click → Copy → CSS Selector to get a starting point, then simplify it.

### 4. Run

```bash
# Run immediately + schedule daily
python main.py

# Run once and exit (for use with cron)
python main.py --now
```

---

## Adding a new site

1. Open the target news page in your browser
2. Press F12 → Inspector, find the repeating article card element
3. Note its CSS class/attribute
4. Add an entry to `sites.json`:

```json
{
  "name":        "My News Site",
  "url":         "https://mynewssite.com/latest",
  "article_sel": ".article-card",
  "title_sel":   "h2.headline",
  "summary_sel": "p.teaser",
  "link_sel":    "a.read-more",
  "base_url":    "https://mynewssite.com",
  "impersonate": "chrome"
}
```

---

## Project structure

```
newsbot/
├── main.py            # Scheduler + job runner
├── scraper.py         # Scrapling-based scraper
├── telegram_sender.py # Telegram Bot API sender
├── config.py          # Env + sites loader
├── requirements.txt
├── .env               # Your credentials (never commit this!)
├── sites.json         # Your site configs
└── newsbot.log        # Auto-created on first run
```

---

## Cron example (Linux)

```cron
# Send digest at 7:55 AM every day
55 7 * * * cd /path/to/newsbot && python main.py --now >> newsbot.log 2>&1
```
