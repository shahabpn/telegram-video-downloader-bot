# mom-video-bot

A small Telegram bot. Send it a link from Instagram, TikTok, YouTube, etc. and it sends the video back so you can save it to your phone.

- **Language:** Python 3.12
- **Downloader:** `yt-dlp` (1000+ sites)
- **Host:** Fly.io (cheapest VM, ~$2-3/mo — Fly's free tier ended Oct 2024)
- **Access:** whitelist of Telegram user IDs (you + mom + family)

---

## One-time setup

### 1. Create the bot in Telegram

1. Open Telegram, message **@BotFather**.
2. Send `/newbot`. Pick a name and a username (must end in `bot`).
3. BotFather replies with a token like `1234567890:AAAA...`. Save it.

### 2. Get the Telegram user IDs to whitelist

Each person who should be allowed to use the bot:
1. Opens Telegram and messages **@userinfobot**.
2. It replies with their numeric ID (e.g. `987654321`).

Collect all the IDs into a comma-separated string: `111,222,333`.

### 3. Test locally (optional but recommended)

```bash
cd ~/Desktop/mom-video-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Mac: install ffmpeg if you don't have it
brew install ffmpeg

export TELEGRAM_BOT_TOKEN="paste-token-here"
export ALLOWED_USER_IDS="your-id,moms-id"
python bot.py
```

Open the bot in Telegram, send `/start`, then paste any Instagram reel link.

### 4. Deploy to Fly.io

```bash
# Install Fly CLI (Mac)
brew install flyctl

# Sign in / sign up
fly auth signup   # or: fly auth login

# From the project directory
cd ~/Desktop/mom-video-bot

# First-time launch — accepts the fly.toml as-is; pick a region near you ('sea' = Seattle is set as default)
fly launch --no-deploy --copy-config

# Set secrets (these never go in code or git)
fly secrets set \
  TELEGRAM_BOT_TOKEN="paste-token-here" \
  ALLOWED_USER_IDS="your-id,moms-id"

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
2. Log into a **throwaway** Instagram account in your browser.
3. Export cookies for `instagram.com` → `cookies.txt`.
4. Deploy the cookies file to Fly:

   ```bash
   # Add cookies.txt to the project (it's gitignored)
   cp ~/Downloads/cookies.txt ./cookies.txt

   # Tell the bot where it lives
   fly secrets set YT_DLP_COOKIES_FILE=/app/cookies.txt
   ```

   Then add `COPY cookies.txt .` to the Dockerfile and redeploy.

Don't use your real Instagram account — IG can ban it for automation.

---

## Limits

- **50 MB max per video** — Telegram bot API hard limit. Most reels are 5-20 MB so this is rarely an issue. To send larger files you'd need to switch to the local Bot API server or MTProto (Telethon), which is a much bigger build.
- **One video per message.** Playlists/multi-image posts only return the first video.

---

## Files

- `bot.py` — main bot logic
- `requirements.txt` — Python deps
- `Dockerfile` — container build
- `fly.toml` — Fly.io app config
- `.env.example` — env var template
- `.gitignore` — keeps secrets and downloaded files out of git
