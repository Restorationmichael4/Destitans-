from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
from config import BOT_TOKEN, CHANNEL_ID
from features.jokes import get_joke
from features.quotes import get_quote
from features.trivia import get_trivia
import sqlite3

# Database setup
def setup_database():
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, joined_channel BOOLEAN)"
    )
    conn.commit()
    conn.close()

# Check if user is a member of the channel
def is_member(update: Update) -> bool:
    user_id = update.message.from_user.id
    try:
        member = update.message.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# Add user to the database
def add_user(user_id, joined):
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, joined_channel) VALUES (?, ?)",
        (user_id, joined),
    )
    conn.commit()
    conn.close()

# Welcome message with scrolling text
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not is_member(update):
        add_user(user_id, False)
        keyboard = [
            [
                InlineKeyboardButton("Join Channel", url="https://t.me/destitans"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            "You must join our channel to use this bot.", reply_markup=reply_markup
        )
    else:
        add_user(user_id, True)
        update.message.reply_text(
            "Welcome to Fun Bot! \n🎉 Created by Restoration Michael 🎉"
        )

# Other commands
def joke(update: Update, context: CallbackContext) -> None:
    if is_member(update):
        update.message.reply_text(get_joke())
    else:
        start(update, context)

def quote(update: Update, context: CallbackContext) -> None:
    if is_member(update):
        update.message.reply_text(get_quote())
    else:
        start(update, context)

def trivia(update: Update, context: CallbackContext) -> None:
    if is_member(update):
        question, answer = get_trivia()
        context.user_data["trivia_answer"] = answer
        update.message.reply_text(question)
    else:
        start(update, context)

# Main function
def main():
    setup_database()
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("joke", joke))
    dispatcher.add_handler(CommandHandler("quote", quote))
    dispatcher.add_handler(CommandHandler("trivia", trivia))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
