import json
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import datetime

# Bot Token from Environment Variable
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Required Channel Settings
REQUIRED_CHANNEL = "@destitans"  # Channel username
REDIRECT_CHANNEL = "https://t.me/cybrpnk7"  # Channel link

# Load Data from JSON Files
with open("questions.json", "r") as file:
    QUESTIONS = json.load(file)

with open("jokes.json", "r") as file:
    JOKES = json.load(file)

with open("quotes.json", "r") as file:
    QUOTES = json.load(file)

with open("horoscopes.json", "r") as file:
    HOROSCOPES = json.load(file)

with open("memes.json", "r") as file:
    MEMES = json.load(file)

SCORES = {}

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
        await update.message.reply_text(
            f"Welcome {user.first_name}! 🎉\n\n"
            "Here are the commands you can use:\n"
            "/play - Play Trivia 🎮\n"
            "/joke - Get a Joke 😂\n"
            "/quote - Inspirational Quote ✨\n"
            "/horoscope <sign> 🔮\n"
            "/date <dd/mm> - Find your Zodiac Sign 🌟\n"
            "/meme - Random Meme 🖼️\n"
            "/leaderboard - Check your score 📊"
        )
    else:
        await update.message.reply_text(
            f"Hi {user.first_name}, you need to join our channel first to use this bot.\n\n"
            f"Join here: {REDIRECT_CHANNEL}\n\n"
            "Then type /start again!"
        )

# Trivia Command
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to play trivia!\n\nJoin here: {REDIRECT_CHANNEL}"
        )
        return

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

# Joke Command
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = random.choice(JOKES)
    await update.message.reply_text(joke)

# Quote Command
async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(QUOTES)
    await update.message.reply_text(quote)

# Meme Command
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meme = random.choice(MEMES)
    await update.message.reply_photo(meme)

# Horoscope Command
async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please provide a zodiac sign! Example: /horoscope aries")
        return

    sign = args[0].lower()
    if sign in HOROSCOPES:
        horoscope_list = HOROSCOPES[sign]
        if horoscope_list:
            selected_horoscope = random.choice(horoscope_list)
            await update.message.reply_text(f"**{sign.capitalize()} Horoscope:**\n{selected_horoscope}", parse_mode="Markdown")
        else:
            await update.message.reply_text(f"No horoscope found for {sign}.")
    else:
        await update.message.reply_text("Invalid sign. Please use a valid zodiac sign like Aries, Taurus, Virgo, etc.")

# Date Command to Determine Zodiac Sign
ZODIAC_DATES = {
    "Aquarius": (datetime.date(2000, 1, 20), datetime.date(2000, 2, 18)),
    "Pisces": (datetime.date(2000, 2, 19), datetime.date(2000, 3, 20)),
    "Aries": (datetime.date(2000, 3, 21), datetime.date(2000, 4, 19)),
    "Taurus": (datetime.date(2000, 4, 20), datetime.date(2000, 5, 20)),
    "Gemini": (datetime.date(2000, 5, 21), datetime.date(2000, 6, 20)),
    "Cancer": (datetime.date(2000, 6, 21), datetime.date(2000, 7, 22)),
    "Leo": (datetime.date(2000, 7, 23), datetime.date(2000, 8, 22)),
    "Virgo": (datetime.date(2000, 8, 23), datetime.date(2000, 9, 22)),
    "Libra": (datetime.date(2000, 9, 23), datetime.date(2000, 10, 22)),
    "Scorpio": (datetime.date(2000, 10, 23), datetime.date(2000, 11, 21)),
    "Sagittarius": (datetime.date(2000, 11, 22), datetime.date(2000, 12, 21)),
    "Capricorn": (datetime.date(2000, 12, 22), datetime.date(2001, 1, 19))
}

async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Please send your birth date in dd/mm format. Example: /date 04/09")
        return

    try:
        day, month = map(int, context.args[0].split('/'))
        birth_date = datetime.date(2000, month, day)

        zodiac_sign = None
        for sign, (start_date, end_date) in ZODIAC_DATES.items():
            if start_date <= birth_date <= end_date:
                zodiac_sign = sign
                break

        if zodiac_sign:
            await update.message.reply_text(f"You're a {zodiac_sign}! ♒")
        else:
            await update.message.reply_text("Could not determine your zodiac sign.")

    except ValueError:
        await update.message.reply_text("Invalid date format! Use dd/mm. Example: /date 04/09")

# Main Function to Run Bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CallbackQueryHandler(handle_answer))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CommandHandler("horoscope", horoscope))
    app.add_handler(CommandHandler("date", date))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
