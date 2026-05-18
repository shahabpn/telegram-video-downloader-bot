import logging
import os
import re
import tempfile
from pathlib import Path

import yt_dlp
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_IDS = {
    int(x.strip())
    for x in os.environ.get("ALLOWED_USER_IDS", "").split(",")
    if x.strip()
}

URL_RE = re.compile(r"https?://\S+")
# Telegram bot upload limit is 50 MB; keep a small safety margin.
MAX_BYTES = 49 * 1024 * 1024


def is_allowed(update: Update) -> bool:
    if not ALLOWED_IDS:
        return True
    return bool(update.effective_user and update.effective_user.id in ALLOWED_IDS)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        return
    await update.message.reply_text(
        "Hi! Send me a link from Instagram, TikTok, YouTube, etc. "
        "and I'll send the video back so you can save it to your phone."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_allowed(update):
        logger.info("Blocked user %s", update.effective_user and update.effective_user.id)
        return

    text = update.message.text or ""
    match = URL_RE.search(text)
    if not match:
        await update.message.reply_text("Send me a video link and I'll fetch it.")
        return

    url = match.group(0)
    status = await update.message.reply_text("Got it — downloading…")

    with tempfile.TemporaryDirectory() as tmp:
        ydl_opts = {
            "outtmpl": str(Path(tmp) / "%(id)s.%(ext)s"),
            "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "retries": 3,
        }
        cookies = os.environ.get("YT_DLP_COOKIES_FILE")
        if cookies and Path(cookies).exists():
            ydl_opts["cookiefile"] = cookies

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filepath = Path(ydl.prepare_filename(info))
                if not filepath.exists():
                    mp4 = filepath.with_suffix(".mp4")
                    if mp4.exists():
                        filepath = mp4
        except Exception as e:
            logger.exception("download failed for %s", url)
            await status.edit_text(
                f"Couldn't download that one. ({e.__class__.__name__})"
            )
            return

        if not filepath.exists():
            await status.edit_text("Download finished but no file came out — that link might not have a video.")
            return

        size = filepath.stat().st_size
        if size > MAX_BYTES:
            mb = size // (1024 * 1024)
            await status.edit_text(
                f"That video is {mb} MB. Telegram bots can only send files up to 50 MB."
            )
            return

        await status.edit_text("Uploading…")
        caption = (info.get("title") or "")[:1024]
        with filepath.open("rb") as f:
            await update.message.reply_video(
                video=f,
                caption=caption,
                supports_streaming=True,
            )
        try:
            await status.delete()
        except Exception:
            pass


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Bot starting (whitelist size: %d)", len(ALLOWED_IDS))
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
