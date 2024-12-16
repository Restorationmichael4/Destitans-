from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import requests
import json
import random

# Constants
BOT_TOKEN = "YOUR_BOT_TOKEN"
HUGGING_FACE_API_KEY = "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"
YOUTUBE_API_KEY = "AIzaSyDW_4o3hbLKw1kDGv9ezWy-Opi4omIHOXA"
REQUIRED_CHANNEL = "@destitans"  # Telegram channel users must join
SCORES = {}  # Dictionary to track user scores
anon_chats = {}  # Dictionary to store anonymous chat pairings

# Load JSON data
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

# Helper Functions
async def is_user_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member_status = await context.bot.get_chat_member(chat_id=REQUIRED_CHANNEL, user_id=user_id)
        return member_status.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# Commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if await is_user_member(update, context):
        await update.message.reply_text(
            f"Welcome {user.first_name}! Use /play for trivia, /youtube to search videos, /ai for AI chat, "
            f"/joke for jokes, /quote for quotes, /horoscope for horoscopes, or /meme for memes."
        )
    else:
        await update.message.reply_text(
            f"Please join our channel first to use this bot: {REQUIRED_CHANNEL}."
        )

# Jokes
async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get jokes!\nJoin here: {REQUIRED_CHANNEL}"
        )
        return

    random_joke = random.choice(JOKES)
    await update.message.reply_text(random_joke)

# Quotes
async def quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get quotes!\nJoin here: {REQUIRED_CHANNEL}"
        )
        return

    random_quote = random.choice(QUOTES)
    await update.message.reply_text(random_quote)

# Horoscope
async def horoscope(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get horoscopes!\nJoin here: {REQUIRED_CHANNEL}"
        )
        return

    random_horoscope = random.choice(HOROSCOPES)
    await update.message.reply_text(random_horoscope)

# Memes
async def meme(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_member(update, context):
        await update.message.reply_text(
            f"You need to join our channel to get memes!\nJoin here: {REQUIRED_CHANNEL}"
        )
        return

    random_meme = random.choice(MEMES)
    await update.message.reply_photo(random_meme)

# YouTube Search
async def youtube_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Provide a search term! Example: `/youtube Python tutorial`")
        return

    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        results = [f"{item['snippet']['title']}: https://www.youtube.com/watch?v={item['id']['videoId']}" for item in data["items"][:5]]
        await update.message.reply_text("\n".join(results))
    else:
        await update.message.reply_text("Could not fetch videos, try again later.")

# AI Chat
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Provide input for AI! Example: `/ai Tell me a joke.`")
        return

    url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    payload = {"inputs": query}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        await update.message.reply_text(result[0]["generated_text"])
    else:
        await update.message.reply_text("AI processing failed, try again later.")

# Anonymous Chat
async def anon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in anon_chats:
        await update.message.reply_text("You are already in an anonymous chat!")
        return

    for partner_id in list(anon_chats.keys()):
        if anon_chats[partner_id] is None:
            anon_chats[user_id] = partner_id
            anon_chats[partner_id] = user_id
            await context.bot.send_message(partner_id, "You are now connected to an anonymous chat. Say hi!")
            await update.message.reply_text("You are now connected to an anonymous chat. Say hi!")
            return

    anon_chats[user_id] = None
    await update.message.reply_text("Looking for a partner...")

async def anon_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in anon_chats or anon_chats[user_id] is None:
        await update.message.reply_text("You are not in an anonymous chat. Use /anon to start.")
        return

    partner_id = anon_chats[user_id]
    await context.bot.send_message(partner_id, update.message.text)

async def anon_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in anon_chats:
        await update.message.reply_text("You are not in an anonymous chat.")
        return

    partner_id = anon_chats.pop(user_id)
    if partner_id:
        anon_chats.pop(partner_id, None)
        await context.bot.send_message(partner_id, "Your partner has left the chat.")
    await update.message.reply_text("You have left the anonymous chat.")

# Trivia Game
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = random.choice(QUESTIONS)
    context.user_data["current_question"] = question

    options = [
        InlineKeyboardButton(text=option, callback_data=option)
        for option in question["options"]
    ]
    keyboard = InlineKeyboardMarkup.from_column(options)
    await update.message.reply_text(question["question"], reply_markup=keyboard)

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
        await query.answer("Correct!")
    else:
        await query.answer("Wrong!")

    await query.edit_message_text(f"The correct answer was: {correct_answer}")

# Bot Setup
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("joke", joke))
app.add_handler(CommandHandler("quote", quote))
app.add_handler(CommandHandler("horoscope", horoscope))
app.add_handler(CommandHandler("meme", meme))
app.add_handler(CommandHandler("youtube", youtube_search))
app.add_handler(CommandHandler("ai", ai_chat))
app.add_handler(CommandHandler("anon", anon))
app.add_handler(CommandHandler("leave", anon_leave))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anon_message))
app.add_handler(CommandHandler("play", play))
app.add_handler(CallbackQueryHandler(handle_answer))

if __name__ == "__main__":
    app.run_polling()
