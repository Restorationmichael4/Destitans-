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
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Dictionary to store user birth dates
USER_BIRTH_DATES = {}
USER_LAST_REQUEST_DATE = {}
USER_HOROSCOPE_HISTORY = {}

# Load Horoscope Data from JSON
with open("horoscopes.json", "r") as file:
    HOROSCOPES = json.load(file)

async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today_date = datetime.date.today()

    # If user provides a birth date in dd/mm format
    if context.args:
        birth_date = context.args[0]

        if len(birth_date) == 5 and "/" in birth_date:
            # Save birth date tied to the user's ID
            USER_BIRTH_DATES[user_id] = birth_date
            await update.message.reply_text(
                f"Got your birth date as {birth_date}. Now use /horoscope to get your personalized horoscope."
            )
            return

        await update.message.reply_text("Invalid date format. Please use /horoscope dd/mm (e.g., /horoscope 04/09).")
        return

    # If birth date is not provided, check if it's already stored
    if user_id not in USER_BIRTH_DATES:
        await update.message.reply_text(
            "You need to provide your birth date first in dd/mm format.\nFor example, send: /horoscope 04/09"
        )
        return

    # Determine zodiac sign from birth month and day
    day, month = map(int, USER_BIRTH_DATES[user_id].split('/'))
    zodiac = get_zodiac_sign(day, month)

    # Check if horoscope was already requested today
    if USER_LAST_REQUEST_DATE.get(user_id) == today_date:
        await update.message.reply_text("You've already received today's horoscope. Try again tomorrow.")
        return

    exhausted_indices = USER_HOROSCOPE_HISTORY.get(user_id, {}).get(zodiac, [])
    horoscopes_list = HOROSCOPES.get(zodiac, [])

    available_indices = list(range(len(horoscopes_list)))
    remaining_indices = list(set(available_indices) - set(exhausted_indices))

    if not remaining_indices:
        exhausted_indices = []
        remaining_indices = available_indices

    selected_index = random.choice(remaining_indices)
    selected_horoscope = horoscopes_list[selected_index]

    exhausted_indices.append(selected_index)
    USER_HOROSCOPE_HISTORY.setdefault(user_id, {})[zodiac] = exhausted_indices
    USER_LAST_REQUEST_DATE[user_id] = today_date

    await update.message.reply_text(f"{zodiac}'s Horoscope: {selected_horoscope}")

def get_zodiac_sign(day, month):
    zodiac_ranges = {
        "Aquarius": ((20, 1), (18, 2)),
        "Pisces": ((19, 2), (20, 3)),
        "Aries": ((20, 3), (19, 4)),
        "Taurus": ((19, 4), (20, 5)),
        "Gemini": ((20, 5), (21, 6)),
        "Cancer": ((21, 6), (22, 7)),
        "Leo": ((22, 7), (22, 8)),
        "Virgo": ((22, 8), (22, 9)),
        "Libra": ((22, 9), (23, 10)),
        "Scorpio": ((23, 10), (22, 11)),
        "Sagittarius": ((22, 11), (21, 12)),
        "Capricorn": ((21, 12), (19, 1)),
    }

    for sign, ((start_day, start_month), (end_day, end_month)) in zodiac_ranges.items():
        if (month == start_month and day >= start_day) or \
           (month == end_month and day <= end_day):
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
