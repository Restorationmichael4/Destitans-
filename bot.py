import json
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

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

# Command to Send a Joke
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joke = random.choice(JOKES)
    await update.message.reply_text(joke)

# Command to Send a Quote
async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(QUOTES)
    await update.message.reply_text(quote)

# Meme Command
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meme = random.choice(MEMES)
    await update.message.reply_photo(meme)

# Horoscope Command
import datetime

# Dictionary to store user birth dates
USER_BIRTH_DATES = {}

# Dictionary to store user's last horoscope retrieval date
USER_LAST_REQUEST_DATE = {}

# Dictionary to store user's exhausted horoscopes
USER_HOROSCOPE_HISTORY = {}

async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today_date = datetime.date.today()

    # Check if user's birth date is stored
    if user_id not in USER_BIRTH_DATES:
        await update.message.reply_text(
            "Please provide your birth month and day in dd/mm format. For example, 14/03 for March 14th."
        )
        context.user_data['awaiting_birth_date'] = True
        return

    # Check if user requested a horoscope today
    if USER_LAST_REQUEST_DATE.get(user_id) == today_date:
        await update.message.reply_text("You've already received today's horoscope. Try again tomorrow.")
        return

    day, month = map(int, USER_BIRTH_DATES[user_id].split('/'))
    zodiac = get_zodiac_sign(day, month)

    # Get or create user's horoscope history
    user_history = USER_HOROSCOPE_HISTORY.get(user_id, {})
    exhausted_indices = user_history.get(zodiac, [])

    # Get available horoscopes for that zodiac sign
    horoscopes_list = HOROSCOPES.get(zodiac, [])

    # Ensure no repeated horoscope until all 30 are exhausted
    available_indices = list(range(len(horoscopes_list)))
    remaining_indices = list(set(available_indices) - set(exhausted_indices))

    if not remaining_indices:
        # Reset exhausted indices for reshuffling after all are exhausted
        exhausted_indices = []
        remaining_indices = available_indices

    selected_index = random.choice(remaining_indices)
    selected_horoscope = horoscopes_list[selected_index]

    # Save horoscope in user's exhausted history
    exhausted_indices.append(selected_index)
    USER_HOROSCOPE_HISTORY[user_id] = {zodiac: exhausted_indices}

    # Save today's request timestamp
    USER_LAST_REQUEST_DATE[user_id] = today_date

    await update.message.reply_text(f"{zodiac}'s Horoscope: {selected_horoscope}")

# Function to determine zodiac sign from birth month and day
def get_zodiac_sign(day, month):
    for sign, (m1, d1, m2, d2) in ZODIAC_SIGNS.items():
        if (month == m1 and day >= d1) or (month == m2 and day <= d2):
            return sign
    return "Capricorn"

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

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
