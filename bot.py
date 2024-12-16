from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import random
from config import BOT_TOKEN

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

SCORES = {}  # Dictionary to track user scores
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
        await update.message.reply_text(
            f"Welcome {user.first_name}! Ready for some fun? Type /play for trivia, /joke for a joke, /quote for a quote, /horoscope for a horoscope, or /meme for a meme!"
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

# Command to Get a Random Joke
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get jokes!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /joke again!"
        )
        return

    random_joke = random.choice(JOKES)
    await update.message.reply_text(random_joke)

# Command to Get a Random Quote
async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get quotes!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /quote again!"
        )
        return

    random_quote = random.choice(QUOTES)
    await update.message.reply_text(random_quote)

# Command to Get a Horoscope
async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get horoscopes!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /horoscope again!"
        )
        return

    random_horoscope = random.choice(HOROSCOPES)
    await update.message.reply_text(random_horoscope)

# Command to Get a Meme
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get memes!\n\n"
            f"Join here: {REQUIRED_CHANNEL}\n\n"
            f"Once you've joined, type /meme again!"
        )
        return

    random_meme = random.choice(MEMES)
    await update.message.reply_photo(random_meme)

# Main Application Setup
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("joke", joke))
app.add_handler(CommandHandler("quote", quote))
app.add_handler(CommandHandler("horoscope", horoscope))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CallbackQueryHandler(handle_answer))

if __name__ == "__main__":
    app.run_polling()
