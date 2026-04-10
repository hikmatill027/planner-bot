from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from db import save_plan_for_date, get_raw_plan_for_date
from formatter import format_plan
from config import CHAT_ID

# Conversation state
WAITING_FOR_PLAN = 1

async def request_plan(update=None, context: ContextTypes.DEFAULT_TYPE=None):
    """Triggered by the 10 PM scheduler job"""
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="📝 *Time to plan tomorrow!*\n\nWrite down your plan for tomorrow. "
             "You can use newlines or commas to separate items.",
        parse_mode="Markdown"
    )

async def receive_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered when you reply with your plan"""
    if update.effective_chat.id != CHAT_ID:
        return ConversationHandler.END

    from datetime import date, timedelta

    # Always save as tomorrow's plan
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    # Fetch existing plan for tomorrow if any
    existing_raw = await get_raw_plan_for_date(tomorrow)

    new_raw = update.message.text.strip()

    # Append new items to existing ones
    if existing_raw:
        combined_raw = existing_raw + "\n" + new_raw
    else:
        combined_raw = new_raw

    formatted = format_plan(combined_raw, target_date=tomorrow)
    await save_plan_for_date(tomorrow, combined_raw, formatted)

    await update.message.reply_text(
        f"✅ *Plan saved for tomorrow!*\n\nHere's your full plan so far:\n\n{formatted}",
        parse_mode="Markdown"
    )

    return ConversationHandler.END

async def send_morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Triggered by the 6 AM and 10 AM scheduler jobs"""
    from datetime import date
    today = date.today().isoformat()

    from db import get_plan_for_date
    plan = await get_plan_for_date(today)

    if plan:
        message = f"🌅 *Good morning! Here's your plan:*\n\n{plan}"
    else:
        message = "⚠️ *No plan recorded for today.*\n\nUse tonight's reminder to set one."

    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=message,
        parse_mode="Markdown"
    )
    
async def view_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows tomorrow's saved plan"""
    if update.effective_chat.id != CHAT_ID:
        return

    from datetime import date, timedelta
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    plan = await get_raw_plan_for_date(tomorrow)

    if plan:
        from formatter import format_plan
        formatted = format_plan(plan, target_date=tomorrow)
        await update.message.reply_text(
            f"📋 *Here's your plan for tomorrow:*\n\n{formatted}",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "📭 *No plan saved for tomorrow yet.*\n\nJust send me a message to add one!",
            parse_mode="Markdown"
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command"""
    if update.effective_chat.id != CHAT_ID:
        return
    await update.message.reply_text(
        "👋 *Daily Planner Bot is running!*\n\n"
        "You will be reminded at:\n"
        "• 🌙 10:00 PM — to write tomorrow's plan\n"
        "• 🌅 6:00 AM — morning reminder\n"
        "• ☀️ 10:00 AM — second morning reminder",
        parse_mode="Markdown"
    )