import os
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)

# ⬇️ Replace this with your actual banner uploaded via Catbox
BANNER_IMAGE_URL = "https://files.catbox.moe/your_uploaded_banner.jpeg"

# ⬇️ Set your bot token here
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# --------- Handlers ---------

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Step 1: Send the banner image
    msg = context.bot.send_photo(chat_id=chat_id, photo=BANNER_IMAGE_URL)

    # Step 2: Send welcome message as a reply to the image
    message_text = (
        "<b>🐱 Welcome to Catmoe Uploader Bot!</b>\n\n"
        "Just send me any file and I'll upload it to <a href='https://catbox.moe/'>Catbox.moe</a> "
        "and give you a cool link 😼\n\n"
        "<i>Bot by @Therazerhub – Made for the lazy legends who hate storage limits.</i>"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 Updates", url="https://t.me/yourchannel")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=chat_id,
        text=message_text,
        reply_to_message_id=msg.message_id,
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

def help_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    help_text = (
        "<b>📦 How to use CatmoeBot:</b>\n\n"
        "1. Send me any file (image, zip, video, audio, etc.)\n"
        "2. I’ll upload it to <a href='https://catbox.moe/'>Catbox.moe</a>\n"
        "3. Get a sharable download link instantly 💡\n\n"
        "<i>Max file size: 200MB</i>\n"
    )

    query.edit_message_text(text=help_text, parse_mode=ParseMode.HTML)

def handle_file(update: Update, context: CallbackContext):
    file = update.message.document or update.message.photo[-1] if update.message.photo else None

    if not file:
        update.message.reply_text("❌ No valid file found.")
        return

    file_path = file.get_file().download()

    with open(file_path, "rb") as f:
        files = {"fileToUpload": f}
        response = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files=files)

    os.remove(file_path)

    if response.ok:
        update.message.reply_text(f"✅ Uploaded!\n\n🔗 {response.text}")
    else:
        update.message.reply_text("❌ Upload failed. Try again later.")

# --------- Main ---------

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(help_callback))
    dispatcher.add_handler(MessageHandler(Filters.document | Filters.photo, handle_file))

    print("🚀 Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
