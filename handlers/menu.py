import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_menu():
    with open(os.path.join(DATA_DIR, "menu.json"), encoding="utf-8") as f:
        return json.load(f)

MENU = load_menu()

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for category in MENU:
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat:{category}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🍗 *KFC Mongolia Цэс*\n\nАнгилал сонгоно уу:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat:", "")

    if category not in MENU:
        await query.edit_message_text("Ангилал олдсонгүй.")
        return

    items = MENU[category]
    text = f"*{category}*\n\n"
    keyboard = []

    for item in items:
        text += f"• {item['name']} — ₮{item['price']:,}\n"
        keyboard.append([InlineKeyboardButton(
            f"🛒 {item['name']} ₮{item['price']:,}",
            callback_data=f"add:{item['id']}"
        )])

    keyboard.append([InlineKeyboardButton("⬅️ Буцах", callback_data="back_to_menu")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def back_to_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for category in MENU:
        keyboard.append([InlineKeyboardButton(category, callback_data=f"cat:{category}")])
    await query.edit_message_text(
        "🍗 *KFC Mongolia Цэс*\n\nАнгилал сонгоно уу:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

def find_item_by_id(item_id):
    for category, items in MENU.items():
        for item in items:
            if item["id"] == item_id:
                return item
    return None

def get_handlers():
    return [
        CommandHandler("menu", menu_command),
        CallbackQueryHandler(category_callback, pattern=r"^cat:"),
        CallbackQueryHandler(back_to_menu_callback, pattern=r"^back_to_menu$"),
    ]
