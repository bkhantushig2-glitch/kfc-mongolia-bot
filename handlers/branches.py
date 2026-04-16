import json
import os
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_branches():
    with open(os.path.join(DATA_DIR, "branches.json"), encoding="utf-8") as f:
        return json.load(f)

BRANCHES = load_branches()

async def branches_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📍 *KFC Улаанбаатар салбарууд:*\n\n"

    for b in BRANCHES:
        text += f"🏪 *{b['name']}*\n"
        text += f"📍 {b['address']}\n"
        text += f"🕐 {b['hours']}\n"
        text += f"📞 {b['phone']}\n\n"

    text += "Захиалга өгөхийн тулд /menu дарна уу!"

    await update.message.reply_text(text, parse_mode="Markdown")

def get_handlers():
    return [
        CommandHandler("branches", branches_command),
    ]
