from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import random
from datetime import datetime
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

REQUIRED_CHANNEL = "@destitans"
BOT_USERNAME = "destitansfunbot"

REFERRALS = {}  # Tracks referrals for extra tries
DAILY_HOROSCOPE = {}  # Tracks horoscope usage
LEADERBOARD = {}  # User scores for the leaderboard


# Check if user is a member of the required channel
async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member_status = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member_status.status in ["member", "administrator", "creator"]
    except Exception:
        return False


# /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    referred_by = context.args[0] if context.args else None

    # Handle referral
    if referred_by and referred_by.isdigit():
        referred_by = int(referred_by)
        if referred_by != user_id:  # Prevent self-referrals
            REFERRALS[referred_by] = REFERRALS.get(referred_by, 0) + 1
            await update.message.reply_text(
                f"Referral accepted! User {referred_by} has gained an extra horoscope try."
            )

    referral_link = f"http://t.me/{BOT_USERNAME}?start={user_id}"

    if await is_user_member(update, context):
        await update.message.reply_text(
            f"Welcome {user.first_name}! Ready for some fun?\n"
            f"Commands:\n"
            f"/play - Trivia\n"
            f"/joke - A Random Joke\n"
            f"/quote - A Random Quote\n"
            f"/horoscope - Daily Horoscope\n"
            f"/meme - A Meme\n"
            f"/leaderboard - View the leaderboard\n"
            f"/refer - Get your referral link\n\n"
            f"Share your referral link to earn extra horoscope tries: {referral_link}"
        )
    else:
        await update.message.reply_text(
            f"Hi {user.first_name}, you need to join our channel first to use this bot.\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, come back and type /start again!"
        )


# /play Command
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to play trivia!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /play again!"
        )
        return

    if not QUESTIONS:
        await update.message.reply_text("No trivia questions available. Try again later!")
        return

    # Get a random question
    question = random.choice(QUESTIONS)
    context.user_data["current_question"] = question

    # Create inline buttons for options
    options = [
        InlineKeyboardButton(text=option, callback_data=option)
        for option in question["options"]
    ]
    keyboard = InlineKeyboardMarkup.from_column(options)

    # Send question with options
    await update.message.reply_text(
        f"{question['question']}", reply_markup=keyboard
    )


# Callback to handle trivia answers
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    question = context.user_data.get("current_question")
    if not question:
        await query.answer("No active question! Use /play to start.")
        return

    selected_option = query.data
    correct_answer = question["answer"]

    if selected_option == correct_answer:
        LEADERBOARD[user_id] = LEADERBOARD.get(user_id, 0) + 1
        await query.answer("Correct! 🎉")
    else:
        await query.answer("Wrong! 😢")

    # Send correct answer and user's current score
    await query.edit_message_text(
        f"The correct answer was: {correct_answer}\n"
        f"Your current score: {LEADERBOARD.get(user_id, 0)}"
    )

    # Clear the current question to prevent repeated answers
    context.user_data["current_question"] = None


# /leaderboard Command
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to view the leaderboard!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /leaderboard again!"
        )
        return

    if not LEADERBOARD:
        await update.message.reply_text("No scores yet! Play some games to get started.")
        return

    sorted_scores = sorted(LEADERBOARD.items(), key=lambda x: x[1], reverse=True)
    leaderboard_text = "🏆 Leaderboard 🏆\n\n"
    for user_id, score in sorted_scores:
        leaderboard_text += f"User {user_id}: {score}\n"

    await update.message.reply_text(leaderboard_text)


# /refer Command
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referral_link = f"http://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(
        f"Share this link with your friends to get extra horoscope tries:\n{referral_link}"
    )


# Main Application Setup
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Register Command Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("refer", refer))
app.add_handler(CallbackQueryHandler(handle_answer))

if __name__ == "__main__":
    app.run_polling()
