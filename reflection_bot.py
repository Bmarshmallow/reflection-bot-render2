
import logging
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

ASK_REFLECTION = 1
user_answers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}! Время вечерней рефлексии 🌙\n"
        "Отвечай честно — это займёт не больше 3 минут.\n\n"
        "1. Что было твоей микропобедой сегодня?"
    )
    user_answers[user.id] = []
    return ASK_REFLECTION

async def collect_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    text = update.message.text
    user_answers[user.id].append(text)
    questions = [
        "2. Где ты действовал автоматически (Система 1)?",
        "3. Где включал осознанность и Систему 2?",
        "4. Что сегодня было полезным вложением (активом)?",
        "5. Что стоит упростить или повторить завтра?"
    ]
    if len(user_answers[user.id]) < len(questions) + 1:
        await update.message.reply_text(questions[len(user_answers[user.id]) - 1])
        return ASK_REFLECTION
    else:
        summary = "\n".join([f"{i+1}. {ans}" for i, ans in enumerate(user_answers[user.id])])
        await update.message.reply_text(f"Твоя рефлексия завершена ✅\n\n{summary}")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Рефлексия отменена.")
    return ConversationHandler.END

if __name__ == '__main__':
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_REFLECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, collect_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
