import json
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Bot Token from Environment Variable
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Required Channel Settings
REQUIRED_CHANNEL = "@destitans"  # Channel username
REDIRECT_CHANNEL = "https://t.me/destitans"  # Channel link

# Bot Owner ID (for Support Messages)
BOT_OWNER_ID = 6784672039

# Referral Tracking
REFERRALS = {}

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

# Send Referral Message
async def send_referral_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    ref_link = f"https://t.me/{context.bot.username}?start={user.id}"
    await update.message.reply_text(
        "Support this bot by sharing it with your friends! Use your unique referral link:\n\n"
        f"{ref_link}\n\n"
        "For every friend that joins through your link, you'll receive a thank-you message!"
    )

# Referral Start Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    # Check for referral
    if args and args[0].isdigit():
        referrer_id = int(args[0])
        if referrer_id != user.id:
            if referrer_id not in REFERRALS:
                REFERRALS[referrer_id] = []
            if user.id not in REFERRALS[referrer_id]:
                REFERRALS[referrer_id].append(user.id)
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f"Thanks for sharing! {user.first_name} joined using your referral link."
                    )
                except Exception:
                    pass

    # Check if user is a channel member
    if await is_user_member(update, context):
        await update.message.reply_text(
            f"Welcome {user.first_name}! 🎉\n\n"
            "Here are the commands you can use:\n"
            "/play - Play Trivia 🎮\n"
            "/joke - Get a Joke 😂\n"
            "/quote - Inspirational Quote ✨\n"
            "/horoscope <sign> 🔮\n"
            "/meme - Random Meme 🖼️\n"
            "/support - Send a message to the bot admin 🛠️\n"
            "/leaderboard - Check your score 📊"
        )
        await send_referral_message(update, context)
    else:
        await update.message.reply_text(
            f"Hi {user.first_name}, you need to join our channel first to use this bot.\n\n"
            f"Join here: {REDIRECT_CHANNEL}\n\n"
            "Then type /start again!"
        )

# Support Command
async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(f"Join our channel first to use this feature: {REDIRECT_CHANNEL}")
        return

    user = update.effective_user
    message = " ".join(context.args)
    if not message:
        await update.message.reply_text("Please provide a message! Example: /support I need help.")
        return

    support_message = f"Message from {user.first_name} (ID: {user.id}):\n\n{message}"
    await context.bot.send_message(chat_id=BOT_OWNER_ID, text=support_message)
    await update.message.reply_text("Your message has been sent to the admin!")
    await send_referral_message(update, context)

# Reply Command (Admin Only)
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != BOT_OWNER_ID:
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /reply <user_id> <message>")
        return

    user_id = args[0]
    message = " ".join(args[1:])
    try:
        await context.bot.send_message(chat_id=user_id, text=message)
        await update.message.reply_text("Reply sent successfully!")
    except Exception:
        await update.message.reply_text("Failed to send reply. Please check the user ID.")

# Trivia Command
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(f"Join our channel to play trivia: {REDIRECT_CHANNEL}")
        return

    question = random.choice(QUESTIONS)
    context.user_data["current_question"] = question

    options = [
        InlineKeyboardButton(text=option, callback_data=option)
        for option in question["options"]
    ]
    keyboard = InlineKeyboardMarkup.from_column(options)

    await update.message.reply_text(question["question"], reply_markup=keyboard)
    await send_referral_message(update, context)

# Other Commands (Jokes, Quotes, Memes, Horoscope) ...

# Main Function to Run Bot
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CommandHandler("joke", joke))
    app.add_handler(CommandHandler("quote", quote))
    app.add_handler(CommandHandler("meme", meme))
    app.add_handler(CommandHandler("horoscope", horoscope))
    app.add_handler(CommandHandler("support", support))
    app.add_handler(CommandHandler("reply", reply))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
