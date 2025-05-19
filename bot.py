from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
from datetime import datetime, timedelta
import os

TOKEN = os.environ.get("BOT_TOKEN")

RATE, HOURS, DAYS, DATE_CHOICE, CUSTOM_DATE = range(5)
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я помогу рассчитать дату замены баллона.\nСколько распылений прибор делает в час?")
    return RATE

async def get_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['rate'] = float(update.message.text)
    await update.message.reply_text("Сколько часов в день работает прибор?")
    return HOURS

async def get_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['hours'] = float(update.message.text)
    await update.message.reply_text("Сколько дней в неделю работает прибор?")
    return DAYS

async def get_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data['days'] = int(update.message.text)

    # Вопрос про дату установки
    keyboard = [
        [KeyboardButton("Сегодня")],
        [KeyboardButton("Указать дату вручную")]
    ]
    await update.message.reply_text(
        "Когда производилась замена баллона?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return DATE_CHOICE

async def handle_date_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Сегодня":
        user_data['start_date'] = datetime.now()
        return await calculate(update, context)
    else:
        await update.message.reply_text("Введите дату в формате ДД.ММ.ГГГГ")
        return CUSTOM_DATE

async def handle_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        user_data['start_date'] = datetime.strptime(text, "%d.%m.%Y")
        return await calculate(update, context)
    except ValueError:
        await update.message.reply_text("Неверный формат даты. Попробуйте снова (ДД.ММ.ГГГГ):")
        return CUSTOM_DATE

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rate = user_data['rate']
    hours = user_data['hours']
    days = user_data['days']
    start_date = user_data['start_date']

    sprays_per_day = rate * hours
    lifespan_days = (3000 / sprays_per_day) / days * 7
    replace_date = start_date + timedelta(days=lifespan_days)

    await update.message.reply_text(f"Баллона хватит примерно до: {replace_date.strftime('%d.%m.%Y')}")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей, отменено.")
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_rate)],
            HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_hours)],
            DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_days)],
            DATE_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date_choice)],
            CUSTOM_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_custom_date)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()
