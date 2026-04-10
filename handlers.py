from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from db import save_plan_for_date, get_raw_plan_for_date
from formatter import format_plan
from config import CHAT_ID

# Conversation state
WAITING_FOR_PLAN = 1
CANCELLING = 2

async def request_plan(update=None, context: ContextTypes.DEFAULT_TYPE = None):
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text="📝 *Time to plan tomorrow!*\n\nWrite down your plan for tomorrow. "
             "You can use newlines or commas to separate items.",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )

async def receive_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != CHAT_ID:
        return ConversationHandler.END

    # If user never triggered add_plan, ignore
    if not context.user_data.get("waiting_for_plan", False):
        return ConversationHandler.END

    context.user_data["waiting_for_plan"] = False

    from datetime import date, timedelta
    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    existing_raw = await get_raw_plan_for_date(tomorrow)
    new_raw = update.message.text.strip()
    combined_raw = existing_raw + "\n" + new_raw if existing_raw else new_raw

    formatted = format_plan(combined_raw, target_date=tomorrow)
    await save_plan_for_date(tomorrow, combined_raw, formatted)

    await update.message.reply_text(
        f"✅ *Plan saved for tomorrow!*\n\nHere's your full plan so far:\n\n{formatted}",
        parse_mode="Markdown"
    )

    await show_keyboard(context.bot, update.effective_chat.id)
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
    if update.effective_chat.id != CHAT_ID:
        return
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Plan", callback_data="add_plan"),
            InlineKeyboardButton("📋 View Plan", callback_data="view_plan"),
        ]
    ])
    await update.message.reply_text(
        "👋 *Daily Planner Bot is running!*\n\n"
        "You will be reminded at:\n"
        "• 🌙 10:00 PM — to write tomorrow's plan\n"
        "• 🌅 6:00 AM — morning reminder\n"
        "• ☀️ 10:00 AM — second morning reminder",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def show_keyboard(bot, chat_id):
    """Helper to send the keyboard after any action"""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Plan", callback_data="add_plan"),
            InlineKeyboardButton("📋 View Plan", callback_data="view_plan"),
        ]
    ])
    await bot.send_message(
        chat_id=chat_id,
        text="What would you like to do?",
        reply_markup=keyboard
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "add_plan":
        await query.message.reply_text(
            "📝 *Send me your plan for tomorrow.*\n\nUse newlines or commas to separate items.",
            parse_mode="Markdown",
            reply_markup=cancel_keyboard()
        )
        context.user_data["waiting_for_plan"] = True

    elif query.data == "cancel":
        context.user_data["waiting_for_plan"] = False
        await query.message.reply_text(
            "❌ *Cancelled.* No changes were made.",
            parse_mode="Markdown"
        )
        await show_keyboard(context.bot, query.message.chat_id)

    elif query.data == "view_plan":
        from datetime import date, timedelta
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        plan = await get_raw_plan_for_date(tomorrow)
        if plan:
            formatted = format_plan(plan, target_date=tomorrow)
            await query.message.reply_text(
                f"📋 *Here's your plan for tomorrow:*\n\n{formatted}",
                parse_mode="Markdown"
            )
        else:
            await query.message.reply_text(
                "📭 *No plan saved for tomorrow yet.*\n\nTap ➕ Add Plan to add one!",
                parse_mode="Markdown"
            )
        await show_keyboard(context.bot, query.message.chat_id)
        
def cancel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Cancel", callback_data="cancel")]
    ])