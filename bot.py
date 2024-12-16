from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json
import random
from config import BOT_TOKEN

# Owner's User ID
OWNER_ID = 6784672039
ALL_USERS = set()  # Store all user IDs that interact with the bot

# Load Data from JSON Files
def load_data(filename, default):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default

QUESTIONS = load_data("questions.json", [])
JOKES = load_data("jokes.json", [])
QUOTES = load_data("quotes.json", [])
HOROSCOPES = load_data("horoscopes.json", [])
MEMES = load_data("memes.json", [])

# Globals
REQUIRED_CHANNEL = "@destitans"
BOT_USERNAME = "destitansfunbot"
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
    ALL_USERS.add(user.id)  # Add user ID to the set of users
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
            f"/support - Send a message to the bot owner\n"
            f"/broadcast (Owner only) - Broadcast a message to all users\n"
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


# /joke Command
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if JOKES:
        await update.message.reply_text(random.choice(JOKES))
    else:
        await update.message.reply_text("No jokes available. Try again later!")


# /quote Command
async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if QUOTES:
        await update.message.reply_text(random.choice(QUOTES))
    else:
        await update.message.reply_text("No quotes available. Try again later!")


# /horoscope Command
async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if HOROSCOPES:
        await update.message.reply_text(random.choice(HOROSCOPES))
    else:
        await update.message.reply_text("No horoscopes available. Try again later!")


# /meme Command
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if MEMES:
        await update.message.reply_photo(random.choice(MEMES))
    else:
        await update.message.reply_text("No memes available. Try again later!")


# /refer Command
async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referral_link = f"http://t.me/{BOT_USERNAME}?start={user_id}"
    await update.message.reply_text(f"Your referral link is:\n{referral_link}")


# /support Command
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if len(context.args) == 0:
        await update.message.reply_text(
            "To send a message to the bot owner, use /support followed by your message.\nExample:\n/support I need help with trivia."
        )
        return

    message = " ".join(context.args)
    if OWNER_ID:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"Message from {user.full_name} (ID: {user.id}):\n\n{message}",
        )
        await update.message.reply_text("Your message has been sent to the bot owner.")
    else:
        await update.message.reply_text("Support is not available at the moment.")


# Reply to a support request
async def reply_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "To reply, use: /reply <user_id> <message>"
        )
        return

    user_id = int(context.args[0])
    message = " ".join(context.args[1:])
    await context.bot.send_message(chat_id=user_id, text=f"Reply from the bot owner:\n\n{message}")
    await update.message.reply_text("Your reply has been sent.")


# /broadcast Command
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) == 0:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    message = " ".join(context.args)
    for user_id in ALL_USERS:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception:
            pass

    await update.message.reply_text("Broadcast sent successfully!")


# Main Application Setup
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Register Command Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("joke", joke))
app.add_handler(CommandHandler("quote", quote))
app.add_handler(CommandHandler("horoscope", horoscope))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("leaderboard", leaderboard))
app.add_handler(CommandHandler("refer", refer))
app.add_handler(CommandHandler("support", support))
app.add_handler(CommandHandler("reply", reply_support))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CallbackQueryHandler(handle_answer))

if __name__ == "__main__":
    app.run_polling()
