import os
from ftplib import FTP

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

FTP_HOST = os.getenv("FTP_HOST")
FTP_USER = os.getenv("FTP_USER")
FTP_PASS = os.getenv("FTP_PASS")

DOMAIN = os.getenv("DOMAIN")
UPLOAD_DIR = os.getenv("UPLOAD_DIR")

pending_files = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Bot Upload FTP Aktif\n\n"
        "1. Kirim file\n"
        "2. Ketik /upload\n"
        "3. Bot upload ke hosting"
    )


async def file_received(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.document:

        pending_files[update.effective_user.id] = (
            update.message.document
        )

        await update.message.reply_text(
            "📁 File diterima.\n\n"
            "Ketik /upload untuk upload."
        )


async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if user_id not in pending_files:

        await update.message.reply_text(
            "❌ Belum ada file."
        )
        return

    document = pending_files[user_id]

    telegram_file = await document.get_file()

    filename = document.file_name

    os.makedirs("downloads", exist_ok=True)

    local_path = f"downloads/{filename}"

    await telegram_file.download_to_drive(
        local_path
    )

    try:

        ftp = FTP(FTP_HOST)

        ftp.login(
            FTP_USER,
            FTP_PASS
        )

        ftp.cwd(UPLOAD_DIR)

        with open(local_path, "rb") as f:

            ftp.storbinary(
                f"STOR {filename}",
                f
            )

        ftp.quit()

        url = (
            f"{DOMAIN}/uploads/{filename}"
        )

        await update.message.reply_text(
            f"✅ Upload berhasil\n\n{url}"
        )

    except Exception as e:

        await update.message.reply_text(
            f"❌ Error:\n{e}"
        )

    finally:

        if os.path.exists(local_path):
            os.remove(local_path)

        pending_files.pop(
            user_id,
            None
        )


app = (
    Application.builder()
    .token(BOT_TOKEN)
    .build()
)

app.add_handler(
    CommandHandler(
        "start",
        start
    )
)

app.add_handler(
    CommandHandler(
        "upload",
        upload
    )
)

app.add_handler(
    MessageHandler(
        filters.Document.ALL,
        file_received
    )
)

print("BOT ONLINE")

app.run_polling()
