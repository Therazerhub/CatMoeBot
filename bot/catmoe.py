import os
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler
)

# --- CONFIG ---
BOT_TOKEN = os.getenv("BOT_TOKEN")  # set in environment or use hardcoded token
BANNER_IMAGE_URL = "https://files.catbox.moe/banner.jpeg"


# --- COMMAND: /start ---
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Step 1: Send banner image
    sent_photo = context.bot.send_photo(
        chat_id=chat_id,
        photo=BANNER_IMAGE_URL
    )

    # Step 2: Reply with bold welcome text + buttons
    message_text = (
        "<b>🐱 Welcome to Catmoe Uploader Bot!</b>\n\n"
        "Just send me any file and I'll upload it to <a href='https://catbox.moe/'>Catbox.moe</a> "
        "and give you a cool link 😼\n\n"
        "<i>Bot by @Therazerhub – Made for the lazy legends who hate storage limits.</i>"
    )

    keyboard = [
        [
            InlineKeyboardButton("🔄 Updates", url="https://t.me/yourchannel"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=chat_id,
        text=message_text,
        parse_mode=ParseMode.HTML,
        reply_to_message_id=sent_photo.message_id,
        reply_markup=reply_markup
    )


# --- COMMAND: /help or button ---
def help_command(update: Update, context: CallbackContext):
    query = update.callback_query
    if query:
        query.answer()
        query.edit_message_text(
            text="❓ <b>How to use:</b>\n\n"
                 "1. Just send any file (max 200MB).\n"
                 "2. Bot uploads to Catbox.moe.\n"
                 "3. Get your permanent telegraph-style link.\n\n"
                 "Try it now!",
            parse_mode=ParseMode.HTML
        )


# --- HANDLE FILE UPLOADS ---
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document or update.message.video or update.message.audio

    if not file:
        update.message.reply_text("⚠️ Unsupported file type.")
        return

    # Download
    file_path = file.get_file().download()

    # Upload to Catbox
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://catbox.moe/user/api.php',
            data={'reqtype': 'fileupload'},
            files={'fileToUpload': f}
        )

    # Clean up temp file
    os.remove(file_path)

    if response.status_code == 200:
        update.message.reply_text(f"✅ Uploaded!\n🔗 {response.text}")
    else:
        update.message.reply_text("❌ Upload failed. Try again later.")


# --- MAIN BOT SETUP ---
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(help_command, pattern="help"))
    dp.add_handler(MessageHandler(Filters.document | Filters.video | Filters.audio, handle_file))

    print("🤖 CatmoeBot is running...")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
