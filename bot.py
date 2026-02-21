import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Join Community", url="https://t.me/Amaz0World")],
        [InlineKeyboardButton("Enter Giveaway 🎁", callback_data='enter')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to **Amazo-World**! 🌐\n\nYour gateway to crypto rewards.",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def main():
    # Use Environment Variable for security
    token = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is starting...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    # Keep it running
    while True:
        await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(main())
