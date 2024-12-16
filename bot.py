from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Load your JSON files (as before)
import json
import os
import random

BOT_TOKEN = os.environ["BOT_TOKEN"]

with open("questions.json", "r") as file:
    QUESTIONS = json.load(file)

with open("jokes.json", "r") as file:
    JOKES = json.load(file)

with open("quotes.json", "r") as file:
    QUOTES = json.load(file)

with open("memes.json", "r") as file:
    MEMES = json.load(file)

SCORES = {}

# Required Channel Settings
REQUIRED_CHANNEL = "@destitans"
REDIRECT_CHANNEL = "https://t.me/cybrpnk7"


# Check User Membership in Channel
async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        status = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return status.status in ["member", "administrator", "creator"]
    except Exception:
        return False


# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if await is_user_member(update, context):
        # Define the keyboard layout
        keyboard = [
            [KeyboardButton("/play 🎮"), KeyboardButton("/joke 😂")],
            [KeyboardButton("/quote ✨"), KeyboardButton("/horoscope 🔮")],
            [KeyboardButton("/meme 🖼️"), KeyboardButton("/leaderboard 📊")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        # Send a welcome message with the keyboard buttons
        await update.message.reply_text(
            f"Welcome {user.first_name}! 🎉\n\nChoose a command from the menu below:",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f"Hi {user.first_name}, you need to join our channel first to use this bot.\n\n"
            f"Join here: {REDIRECT_CHANNEL}\n\nThen type /start again!"
        )


# Trivia Command
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to play trivia!\n\nJoin here: {REDIRECT_CHANNEL}"
        )
        return

    # Select a random question
    question = random.choice(QUESTIONS)
    context.user_data["current_question"] = question

    options = [
        InlineKeyboardButton(text=option, callback_data=option)
        for option in question["options"]
    ]
    keyboard = InlineKeyboardMarkup.from_column(options)

    await update.message.reply_text(question["question"], reply_markup=keyboard)


# Handle Trivia Answer Callback
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    question = context.user_data.get("current_question")
    user_id = query.from_user.id

    if not question:
        await query.answer("No active question. Use /play to start!")
        return

    selected_option = query.data
    correct_answer = question["answer"]

    if selected_option == correct_answer:
        SCORES[user_id] = SCORES.get(user_id, 0) + 1
        await query.answer("Correct! 🎉")
    else:
        await query.answer("Wrong! 😢")

    await query.edit_message_text(
        f"The correct answer was: {correct_answer}\n"
        f"Your current score: {SCORES.get(user_id, 0)}"
    )

    context.user_data["current_question"] = None


# Command to Send a Joke
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = random.choice(JOKES)
    await update.message.reply_text(joke)


# Command to Send a Quote
async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(QUOTES)
    await update.message.reply_text(quote)


# Command to Send a Meme
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meme = random.choice(MEMES)
    await update.message.reply_photo(meme)


# Leaderboard Command
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not SCORES:
        await update.message.reply_text("No scores yet! Start playing with /play 🎮")
        return

    leaderboard_text = "🏆 Leaderboard 🏆\n\n"
    for user_id, score in sorted(SCORES.items(), key=lambda x: x[1], reverse=True):
        user = await context.bot.get_chat(user_id)
        leaderboard_text += f"{user.first_name}: {score} points\n"

    await update.message.reply_text(leaderboard_text)


# Main Function
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CallbackQueryHandler(handle_answer))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
