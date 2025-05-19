from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters
from datetime import datetime, timedelta
import os

TOKEN = os.environ.get("BOT_TOKEN")

RATE, HOURS, DAYS = range(3)
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

    rate = user_data['rate']
    hours = user_data['hours']
    working_days = user_data['days']
    
    sprays_per_day = rate * hours
    lifespan_days = (3000 / sprays_per_day) / working_days * 7
    replace_date = datetime.now() + timedelta(days=lifespan_days)
    replace_date_str = replace_date.strftime('%d.%m.%Y')

    await update.message.reply_text(f"Баллона хватит примерно до: {replace_date_str}")
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
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == '__main__':
    main()