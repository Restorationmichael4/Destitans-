from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import random
import datetime
from config import BOT_TOKEN

# Load Data from JSON Files
try:
    with open("questions.json", "r") as file:
        QUESTIONS = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    QUESTIONS = []

try:
    with open("jokes.json", "r") as file:
        JOKES = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    JOKES = []

try:
    with open("quotes.json", "r") as file:
        QUOTES = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    QUOTES = []

try:
    with open("horoscopes.json", "r") as file:
        HOROSCOPES = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    HOROSCOPES = []

try:
    with open("memes.json", "r") as file:
        MEMES = json.load(file)
except (FileNotFoundError, json.JSONDecodeError):
    MEMES = []

SCORES = {}  # Dictionary to track user scores
DAILY_HOROSCOPE = {}  # Tracks user's horoscope usage per day
REFERRALS = {}  # Tracks referrals for extra tries
REQUIRED_CHANNEL = "@destitans"  # The username of the required channel
REDIRECT_CHANNEL = "https://t.me/cybrpnk7"  # The channel to send new users to


# Check User Membership in Channel
async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member_status = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member_status.status in ["member", "administrator", "creator"]
    except Exception:
        return False


# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if await is_user_member(update, context):
        referral_code = f"ref-{user.id}"
        await update.message.reply_text(
            f"Welcome {user.first_name}! Ready for some fun?\n"
            f"Commands:\n"
            f"/play - Trivia\n"
            f"/joke - A Random Joke\n"
            f"/quote - A Random Quote\n"
            f"/horoscope - Daily Horoscope\n"
            f"/meme - A Meme\n"
            f"\nRefer a friend using your code: `{referral_code}` and get extra horoscope tries!"
        )
    else:
        await update.message.reply_text(
            f"Hi {user.first_name}, you need to join our channel first to use this bot.\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, come back and type /start again!"
        )


# Trivia Play Command
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to play trivia!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /play again!"
        )
        return

    # Pick a random question
    question = random.choice(QUESTIONS)
    context.user_data["current_question"] = question  # Save question to user data

    # Create inline buttons for options
    options = [
        InlineKeyboardButton(text=option, callback_data=option)
        for option in question["options"]
    ]
    keyboard = InlineKeyboardMarkup.from_column(options)

    # Send question with options
    await update.message.reply_text(question["question"], reply_markup=keyboard)


# Handle Trivia Answer Callback
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    question = context.user_data.get("current_question")  # Retrieve the question
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

    # Send correct answer and user's current score
    await query.edit_message_text(
        f"The correct answer was: {correct_answer}\n"
        f"Your current score: {SCORES.get(user_id, 0)}"
    )

    # Start a new question
    await play(query.message, context)


# Daily Horoscope Command
async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    today = datetime.date.today()

    # Check if user has already used the horoscope today
    if DAILY_HOROSCOPE.get(user_id) == today and REFERRALS.get(user_id, 0) == 0:
        await update.message.reply_text(
            f"You've already used your daily horoscope! Refer someone using your referral code to get extra tries."
        )
        return

    # Deduct referral try if applicable
    if DAILY_HOROSCOPE.get(user_id) == today:
        REFERRALS[user_id] -= 1

    # Mark horoscope as used for today
    DAILY_HOROSCOPE[user_id] = today

    # Send a random horoscope
    random_horoscope = random.choice(HOROSCOPES)
    await update.message.reply_text(random_horoscope)


# Referral Command
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referred_user_id = context.args[0] if context.args else None

    if referred_user_id and referred_user_id.startswith("ref-"):
        referred_user_id = int(referred_user_id.split("-")[1])
        REFERRALS[referred_user_id] = REFERRALS.get(referred_user_id, 0) + 1
        await update.message.reply_text("Referral successful! You've earned extra horoscope tries.")
    else:
        await update.message.reply_text("Invalid referral code. Please try again.")


# Main Application Setup
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("horoscope", horoscope))
app.add_handler(CommandHandler("refer", refer))
app.add_handler(CallbackQueryHandler(handle_answer))

if __name__ == "__main__":
    app.run_polling()
