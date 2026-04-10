import asyncio
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters
)
from config import BOT_TOKEN, CHAT_ID
from db import init_db
from scheduler import setup_scheduler
from handlers import (
    start,
    request_plan,
    receive_plan,
    send_morning_reminder,
    view_plan,
    WAITING_FOR_PLAN
)

# Logging so you can see what's happening in the terminal
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)

async def main():
    # 1. Initialize the database
    await init_db()
    print("✅ Database ready")

    # 2. Build the bot application
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # 3. Conversation handler — listens for your plan after the 10 PM reminder
    conversation = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan)
        ],
        states={
            WAITING_FOR_PLAN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_plan)
            ]
        },
        fallbacks=[],
        per_chat=True
    )

    # 4. Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("plan", request_plan))
    app.add_handler(CommandHandler("view", view_plan))
    app.add_handler(conversation)

    # 5. Start the scheduler
    setup_scheduler(app)

    # 6. Start the bot
    print("🤖 Bot is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    # Keep running forever
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())