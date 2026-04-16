import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_menu():
    with open(os.path.join(DATA_DIR, "menu.json"), encoding="utf-8") as f:
        return json.load(f)

MENU = load_menu()

def get_cart(context):
    if "cart" not in context.user_data:
        context.user_data["cart"] = {}
    return context.user_data["cart"]

def cart_summary(context):
    cart = get_cart(context)
    if not cart:
        return ""
    total_items = sum(cart.values())
    total_price = 0
    for item_id, qty in cart.items():
        item = find_item_by_id(item_id)
        if item:
            total_price += item["price"] * qty
    return f"\n🛒 Сагс: {total_items} зүйл | ₮{total_price:,}"

def find_item_by_id(item_id):
    for category, items in MENU.items():
        for item in items:
            if item["id"] == item_id:
                return item
    return None

def build_category_keyboard(category, context):
    items = MENU[category]
    cart = get_cart(context)
    keyboard = []

    for item in items:
        qty = cart.get(item["id"], 0)
        price = f"₮{item['price']:,}"
        if qty > 0:
            keyboard.append([
                InlineKeyboardButton("➖", callback_data=f"minus:{item['id']}"),
                InlineKeyboardButton(f"{qty}x {item['name']}", callback_data="noop"),
                InlineKeyboardButton("➕", callback_data=f"plus:{item['id']}"),
            ])
        else:
            keyboard.append([
                InlineKeyboardButton(f"{item['name']} • {price}", callback_data=f"plus:{item['id']}"),
            ])

    cats = list(MENU.keys())
    nav = []
    idx = cats.index(category)
    if idx > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"cat:{cats[idx-1]}"))
    nav.append(InlineKeyboardButton(f"{idx+1}/{len(cats)}", callback_data="noop"))
    if idx < len(cats) - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"cat:{cats[idx+1]}"))
    keyboard.append(nav)

    total_items = sum(cart.values()) if cart else 0
    if total_items > 0:
        total_price = sum(find_item_by_id(iid)["price"] * q for iid, q in cart.items() if find_item_by_id(iid))
        keyboard.append([InlineKeyboardButton(f"🛒 Сагс харах (₮{total_price:,})", callback_data="show_cart")])

    return keyboard

def build_category_text(category):
    return f"*{category}*\n\nБүтээгдэхүүн сонгоно уу:"

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    first_cat = list(MENU.keys())[0]
    text = build_category_text(first_cat)
    keyboard = build_category_keyboard(first_cat, context)
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat:", "")
    if category not in MENU:
        return
    text = build_category_text(category)
    keyboard = build_category_keyboard(category, context)
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

def find_category_for_item(item_id):
    for category, items in MENU.items():
        for item in items:
            if item["id"] == item_id:
                return category
    return None

async def plus_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_id = query.data.replace("plus:", "")
    cart = get_cart(context)
    cart[item_id] = cart.get(item_id, 0) + 1
    item = find_item_by_id(item_id)
    await query.answer(f"✅ {item['name']} x{cart[item_id]}")

    category = find_category_for_item(item_id)
    if category:
        text = build_category_text(category)
        keyboard = build_category_keyboard(category, context)
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def minus_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_id = query.data.replace("minus:", "")
    cart = get_cart(context)
    if item_id in cart:
        cart[item_id] -= 1
        if cart[item_id] <= 0:
            del cart[item_id]
    item = find_item_by_id(item_id)
    qty = cart.get(item_id, 0)
    name = item["name"]
    msg = "❌ Хасагдлаа" if qty == 0 else f"{name} x{qty}"
    await query.answer(msg)

    category = find_category_for_item(item_id)
    if category:
        text = build_category_text(category)
        keyboard = build_category_keyboard(category, context)
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

def get_handlers():
    return [
        CommandHandler("menu", menu_command),
        CallbackQueryHandler(category_callback, pattern=r"^cat:"),
        CallbackQueryHandler(plus_callback, pattern=r"^plus:"),
        CallbackQueryHandler(minus_callback, pattern=r"^minus:"),
        CallbackQueryHandler(noop_callback, pattern=r"^noop$"),
    ]
