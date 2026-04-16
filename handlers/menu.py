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

def find_item_by_id(item_id):
    for category, items in MENU.items():
        for item in items:
            if item["id"] == item_id:
                return item
    return None

def find_category_for_item(item_id):
    for category, items in MENU.items():
        for item in items:
            if item["id"] == item_id:
                return category
    return None

def build_categories_keyboard(context):
    cart = get_cart(context)
    keyboard = []
    cats = list(MENU.keys())
    for i in range(0, len(cats), 2):
        row = [InlineKeyboardButton(cats[i], callback_data=f"cat:{cats[i]}")]
        if i + 1 < len(cats):
            row.append(InlineKeyboardButton(cats[i+1], callback_data=f"cat:{cats[i+1]}"))
        keyboard.append(row)

    if cart:
        total_items = sum(cart.values())
        total_price = sum(find_item_by_id(iid)["price"] * q for iid, q in cart.items() if find_item_by_id(iid))
        keyboard.append([InlineKeyboardButton(f"🛒 Сагс харах ({total_items} зүйл • ₮{total_price:,})", callback_data="show_cart")])

    return keyboard

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

    keyboard.append([InlineKeyboardButton("⬅️ Ангилалууд", callback_data="categories")])

    if cart:
        total_items = sum(cart.values())
        total_price = sum(find_item_by_id(iid)["price"] * q for iid, q in cart.items() if find_item_by_id(iid))
        keyboard.append([InlineKeyboardButton(f"🛒 Сагс харах ({total_items} зүйл • ₮{total_price:,})", callback_data="show_cart")])

    return keyboard

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = build_categories_keyboard(context)
    await update.message.reply_text(
        "🍗 *KFC Mongolia*\n\nАнгилал сонгоно уу:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = build_categories_keyboard(context)
    await query.edit_message_text(
        "🍗 *KFC Mongolia*\n\nАнгилал сонгоно уу:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def category_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category = query.data.replace("cat:", "")
    if category not in MENU:
        return
    text = f"*{category}*\n\nБүтээгдэхүүн сонгоно уу:"
    keyboard = build_category_keyboard(category, context)
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def plus_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_id = query.data.replace("plus:", "")
    cart = get_cart(context)
    cart[item_id] = cart.get(item_id, 0) + 1
    item = find_item_by_id(item_id)
    await query.answer(f"✅ {item['name']} x{cart[item_id]}")

    category = find_category_for_item(item_id)
    if category:
        text = f"*{category}*\n\nБүтээгдэхүүн сонгоно уу:"
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
        text = f"*{category}*\n\nБүтээгдэхүүн сонгоно уу:"
        keyboard = build_category_keyboard(category, context)
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def noop_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()

def get_handlers():
    return [
        CommandHandler("menu", menu_command),
        CallbackQueryHandler(categories_callback, pattern=r"^categories$"),
        CallbackQueryHandler(category_callback, pattern=r"^cat:"),
        CallbackQueryHandler(plus_callback, pattern=r"^plus:"),
        CallbackQueryHandler(minus_callback, pattern=r"^minus:"),
        CallbackQueryHandler(noop_callback, pattern=r"^noop$"),
    ]
