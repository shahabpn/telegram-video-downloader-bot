# Telegram Video Downloader Bot

A small, private Telegram bot for personal video saving. Send it a link from Instagram, TikTok, YouTube, etc. and it sends the video back so you can save it to your camera roll.

Built for people who don't want to use sketchy popup-ridden downloader websites. Whitelist your own Telegram user IDs so only you (and people you choose) can use it.

- **Language:** Python 3.12
- **Downloader:** [`yt-dlp`](https://github.com/yt-dlp/yt-dlp) (~1,900 supported sites)
- **Host:** Fly.io (~$2-3/month for 24/7 uptime)
- **Access:** Whitelist of Telegram user IDs — not public-facing

> **Personal use only.** This is intended for saving content you have the right to save — your own posts, content shared with you, public-domain or Creative Commons material, personal reference clips. You're responsible for complying with each platform's Terms of Service and the copyright laws in your jurisdiction. Don't use this for redistribution, monetization, or anything you don't have permission to download.

---

## One-time setup

### 1. Clone the repo

```bash
git clone https://github.com/shahabpn/telegram-video-downloader-bot.git
cd telegram-video-downloader-bot
```

### 2. Create the bot in Telegram

1. Open Telegram, message **@BotFather**.
2. Send `/newbot`. Pick a name and a username (must end in `bot`).
3. BotFather replies with a token like `1234567890:AAAA...`. Save it.

### 3. Get the Telegram user IDs to whitelist

Each person who should be allowed to use the bot:
1. Opens Telegram and messages **@userinfobot**.
2. It replies with their numeric ID (e.g. `987654321`).

Collect the IDs into a comma-separated string: `111,222,333`.

### 4. Test locally (optional but recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Mac: install ffmpeg if you don't have it
brew install ffmpeg

export TELEGRAM_BOT_TOKEN="paste-token-here"
export ALLOWED_USER_IDS="your-id,family-member-id"
python bot.py
```

Open the bot in Telegram, send `/start`, then paste a video link.

### 5. Deploy to Fly.io

```bash
# Install Fly CLI (Mac)
brew install flyctl

# Sign in / sign up
fly auth signup   # or: fly auth login

# First-time launch — accepts the fly.toml as-is; pick a region near you
fly launch --no-deploy --copy-config

# Set secrets (these never go in code or git)
fly secrets set \
  TELEGRAM_BOT_TOKEN="paste-token-here" \
  ALLOWED_USER_IDS="your-id,family-member-id"

# Deploy
fly deploy
```

Check it's running:

```bash
fly logs
fly status
```

---

## If Instagram starts blocking downloads

Instagram tightens anonymous access from time to time. If the bot starts failing on IG links specifically:

1. Install the **"Get cookies.txt LOCALLY"** browser extension (Chrome/Firefox).
2. Log into a **throwaway** Instagram account in your browser (never your real one).
3. Export cookies for `instagram.com` → `cookies.txt`.
4. Deploy the cookies file to Fly:

   ```bash
   cp ~/Downloads/cookies.txt ./cookies.txt
   fly secrets set YT_DLP_COOKIES_FILE=/app/cookies.txt
   ```

   Then add `COPY cookies.txt .` to the Dockerfile and redeploy.

Don't use your real Instagram account — IG can ban it for automation.

---

## Limits

- **50 MB max per video** — Telegram bot API hard limit. Most reels are 5-20 MB so this rarely matters. For larger files you'd need to switch to MTProto (Telethon), which is a much bigger build.
- **One video per message.** Playlists/multi-image posts only return the first video.

---

## Files

- `bot.py` — main bot logic
- `requirements.txt` — Python deps
- `Dockerfile` — container build
- `fly.toml` — Fly.io app config
- `.env.example` — env var template
- `.gitignore` — keeps secrets and downloaded files out of git

---

## Background

I built this in about 30 minutes with AI assistance because I was tired of using sketchy ad-laden downloader websites every time I needed to save a video. Full story and step-by-step build writeup: [How I Built a Telegram Bot That Downloads Videos From Instagram, TikTok, and YouTube — for $3 a Month](https://shahabpapoon.com/blog/how-i-built-a-telegram-bot-video-downloader/).

---

## License

MIT — do what you want with the code. The personal-use disclaimer above still applies to how you actually run it.
