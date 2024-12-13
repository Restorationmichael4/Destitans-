from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json
from config import BOT_TOKEN

# Load Questions
with open("questions.json", "r") as file:
    QUESTIONS = json.load(file)

SCORES = {}  # To track user scores

# Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Welcome {user.first_name}! Ready for some trivia fun? Type /play to start!"
    )

# Play Command
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = random.choice(QUESTIONS)
    options = [InlineKeyboardButton(opt, callback_data=opt) for opt in question["options"]]
    keyboard = InlineKeyboardMarkup.from_column(options)

    context.user_data["current_question"] = question
    await update.message.reply_text(question["question"], reply_markup=keyboard)

# Handle Answers
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    question = context.user_data.get("current_question")
    answer = query.data

    if answer == question["answer"]:
        SCORES[query.from_user.id] = SCORES.get(query.from_user.id, 0) + 1
        await query.answer("Correct!")
    else:
        await query.answer("Wrong!")

    await query.edit_message_text(f"The correct answer was: {question['answer']}")
    await play(query.message, context)

# Main Function
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("play", play))
    app.add_handler(CallbackQueryHandler(handle_answer))

    print("Bot is running...")
    app.run_polling()
