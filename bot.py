from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import random
from config import BOT_TOKEN
from datetime import datetime

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
BOT_USERNAME = "destitansfunbot"  # Replace with your bot's username


# Check User Membership in Channel
async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member_status = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member_status.status in ["member", "administrator", "creator"]
    except Exception:
        return False


# Start Command with Referral Handling
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    referred_by = context.args[0] if context.args else None

    # Handle referral if present
    if referred_by and referred_by.isdigit():
        referred_by = int(referred_by)
        if referred_by != user_id:  # Prevent self-referrals
            REFERRALS[referred_by] = REFERRALS.get(referred_by, 0) + 1
            await update.message.reply_text(
                f"Referral accepted! {referred_by} has gained extra horoscope tries."
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
            f"/refer - Get your referral link\n"
            f"\nShare your referral link to get extra horoscope tries: {referral_link}"
        )
    else:
        await update.message.reply_text(
            f"Hi {user.first_name}, you need to join our channel first to use this bot.\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, come back and type /start again!"
        )


# Command to Get a Meme
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get memes!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /meme again!"
        )
        return

    if not MEMES:
        await update.message.reply_text("No memes available at the moment. Try again later!")
        return

    random_meme = random.choice(MEMES)

    try:
        if random_meme.startswith("http"):
            await update.message.reply_photo(random_meme)
        else:
            await update.message.reply_text("Invalid meme format in memes.json.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")


# Command to Get a Joke
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get jokes!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /joke again!"
        )
        return

    if not JOKES:
        await update.message.reply_text("No jokes available at the moment. Try again later!")
        return

    random_joke = random.choice(JOKES)
    await update.message.reply_text(random_joke)


# Command to Get a Quote
async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get quotes!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /quote again!"
        )
        return

    if not QUOTES:
        await update.message.reply_text("No quotes available at the moment. Try again later!")
        return

    random_quote = random.choice(QUOTES)
    await update.message.reply_text(random_quote)


# Command to Show Leaderboard
async def leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to view the leaderboard!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /leaderboard again!"
        )
        return

    if not SCORES:
        await update.message.reply_text("No scores yet! Play some games to get started.")
        return

    leaderboard_text = "🏆 Leaderboard 🏆\n\n"
    sorted_scores = sorted(SCORES.items(), key=lambda x: x[1], reverse=True)
    for user_id, score in sorted_scores:
        leaderboard_text += f"User {user_id}: {score}\n"

    await update.message.reply_text(leaderboard_text)


# Command to Get a Daily Horoscope
async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    today = datetime.now().date()

    # Check if user has already used their daily horoscope
    if DAILY_HOROSCOPE.get(user_id) == today and REFERRALS.get(user_id, 0) <= 0:
        await update.message.reply_text(
            f"You've already used your daily horoscope. Refer a friend to get extra tries!"
        )
        return

    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get horoscopes!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /horoscope again!"
        )
        return

    if not HOROSCOPES:
        await update.message.reply_text("No horoscopes available at the moment. Try again later!")
        return

    random_horoscope = random.choice(HOROSCOPES)
    DAILY_HOROSCOPE[user_id] = today
    if REFERRALS.get(user_id, 0) > 0:
        REFERRALS[user_id] -= 1

    await update.message.reply_text(random_horoscope)


# Command to Get Referral Link
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
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("joke", joke))
app.add_handler(CommandHandler("quote", quote))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("horoscope", horoscope))
app.add_handler(CommandHandler("refer", refer))

if __name__ == "__main__":
    app.run_polling()
