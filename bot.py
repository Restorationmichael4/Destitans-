import json
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Bot Token from Environment Variable
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Required Channel Settings
REQUIRED_CHANNEL = "@destitans"  # Channel username
REDIRECT_CHANNEL = "https://t.me/destitans"  # Channel link
ADMIN_USER_ID = 6784672039  # Admin ID for /support

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
REFERRALS = {}  # To store referral links

# Check User Membership in Channel
async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        status = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return status.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Generate Referral Link
def get_referral_link(user_id):
    return f"https://t.me/{context.bot.username}?start={user_id}"

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    # Handle referrals
    if context.args:
        referrer_id = context.args[0]
        if referrer_id != str(user_id) and referrer_id not in REFERRALS.get(user_id, []):
            if referrer_id in REFERRALS:
                REFERRALS[referrer_id].append(user_id)
            else:
                REFERRALS[referrer_id] = [user_id]
            await context.bot.send_message(
                chat_id=int(referrer_id),
                text=f"Thanks for sharing! {user.first_name} joined using your link!"
            )

    if await is_user_member(update, context):
        await update.message.reply_text(
            f"Welcome {user.first_name}! 🎉\n\n"
            "Here are the commands you can use:\n"
            "/play - Play Trivia 🎮\n"
            "/joke - Get a Joke 😂\n"
            "/quote - Inspirational Quote ✨\n"
            "/horoscope <sign> 🔮\n"
            "/date <dd/mm> - Find your zodiac sign 🗓️\n"
            "/meme - Random Meme 🖼️\n"
            "/leaderboard - Check your score 📊\n"
            "/support - Send a message to the admin 👤\n"
            "/broadcast - Admin-only command to send a message to all users."
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
    await update.message.reply_text(
        f"{joke}\n\nSupport this bot by sharing it with your friends! {get_referral_link(update.effective_user.id)}"
    )

# Quote Command
async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    quote = random.choice(QUOTES)
    await update.message.reply_text(
        f"{quote}\n\nSupport this bot by sharing it with your friends! {get_referral_link(update.effective_user.id)}"
    )

# Meme Command
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meme = random.choice(MEMES)
    await update.message.reply_photo(
        meme, caption=f"Support this bot by sharing it with your friends! {get_referral_link(update.effective_user.id)}"
    )

# Horoscope Command
async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please provide a zodiac sign! Example: /horoscope aries")
        return

    sign = args[0].lower()
    if sign in HOROSCOPES:
        message = random.choice(HOROSCOPES[sign])
        user_id = update.effective_user.id
        await update.message.reply_text(
            f"{message}\n\nSupport this bot by sharing it with your friends! {get_referral_link(user_id)}"
        )
    else:
        await update.message.reply_text("Invalid zodiac sign. Try again with a valid sign (e.g., Aries, Taurus, Virgo).")

# Date Command to Find Zodiac Sign
async def date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please provide your birth date in dd/mm format! Example: /date 04/09")
        return

    try:
        day, month = map(int, args[0].split("/"))
    except ValueError:
        await update.message.reply_text("Invalid date format. Use dd/mm (e.g., /date 04/09).")
        return

    zodiac_signs = [
        ("capricorn", (1, 20), (2, 18)),
        ("aquarius", (1, 21), (2, 19)),
        ("pisces", (2, 20), (3, 20)),
        ("aries", (3, 21), (4, 19)),
        ("taurus", (4, 20), (5, 20)),
        ("gemini", (5, 21), (6, 20)),
        ("cancer", (6, 21), (7, 22)),
        ("leo", (7, 23), (8, 22)),
        ("virgo", (8, 23), (9, 22)),
        ("libra", (9, 23), (10, 22)),
        ("scorpio", (10, 23), (11, 21)),
        ("sagittarius", (11, 22), (12, 21)),
        ("capricorn", (12, 22), (1, 19)),
    ]

    for sign, (start_month, start_day), (end_month, end_day) in zodiac_signs:
        if (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
            await update.message.reply_text(
                f"Your zodiac sign is {sign.capitalize()}! ♑️\n\n"
                f"Support this bot by sharing it with your friends! {get_referral_link(update.effective_user.id)}"
            )
            return

    await update.message.reply_text("Invalid date. Please check your input!")

# Support Command
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please include your message: /support <message>")
        return

    user = update.effective_user
    message = " ".join(args)
    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"Support message from {user.full_name} (@{user.username}):\n\n{message}"
    )
    await update.message.reply_text("Your message has been sent to the admin. You'll get a reply soon!")

# Broadcast Command (Admin-only)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("You don't have permission to use this command.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Please include a message to broadcast: /broadcast <message>")
        return

    message = " ".join(args)
    for user_id in SCORES.keys():
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
        except Exception:
            continue

    await update.message.reply_text("Broadcast sent to all users!")

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
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("broadcast", broadcast))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
