from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.menu import find_item_by_id, get_cart

def build_cart_text(cart):
    text = "🛒 *Таны захиалга:*\n\n"
    total = 0
    n = 1
    for item_id, qty in cart.items():
        item = find_item_by_id(item_id)
        if not item:
            continue
        line_total = item["price"] * qty
        total += line_total
        if qty > 1:
            text += f"{n}. {item['name']} x{qty} — ₮{line_total:,}\n"
        else:
            text += f"{n}. {item['name']} — ₮{line_total:,}\n"
        n += 1

    text += f"\n{'─' * 25}\n"
    text += f"*Нийт: ₮{total:,}*\n"
    text += f"📦 {sum(cart.values())} зүйл"
    return text, total

def build_cart_keyboard(cart):
    keyboard = []
    for item_id, qty in cart.items():
        item = find_item_by_id(item_id)
        if not item:
            continue
        keyboard.append([
            InlineKeyboardButton("➖", callback_data=f"cminus:{item_id}"),
            InlineKeyboardButton(f" {item['name']} x{qty} ", callback_data="noop"),
            InlineKeyboardButton("➕", callback_data=f"cplus:{item_id}"),
        ])

    keyboard.append([InlineKeyboardButton("💳 Төлбөр төлөх", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🗑 Бүгдийг цэвэрлэх", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton("📋 Цэс харах", callback_data="cat:" + "🍗 Дан бүтээгдэхүүн")])
    return keyboard

async def show_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = get_cart(context)
    if not cart:
        await query.edit_message_text("🛒 Таны сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        return
    text, _ = build_cart_text(cart)
    keyboard = build_cart_keyboard(cart)
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = get_cart(context)
    if not cart:
        await update.message.reply_text("🛒 Таны сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        return
    text, _ = build_cart_text(cart)
    keyboard = build_cart_keyboard(cart)
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def cart_plus_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_id = query.data.replace("cplus:", "")
    cart = get_cart(context)
    cart[item_id] = cart.get(item_id, 0) + 1
    await query.answer(f"➕ x{cart[item_id]}")
    text, _ = build_cart_text(cart)
    keyboard = build_cart_keyboard(cart)
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def cart_minus_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_id = query.data.replace("cminus:", "")
    cart = get_cart(context)
    if item_id in cart:
        cart[item_id] -= 1
        if cart[item_id] <= 0:
            del cart[item_id]
    await query.answer("➖")

    if not cart:
        await query.edit_message_text("🛒 Сагс хоосон боллоо.\n\n/menu дарж захиалга өгнө үү!")
        return

    text, _ = build_cart_text(cart)
    keyboard = build_cart_keyboard(cart)
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cart"] = {}
    await update.message.reply_text("🗑 Сагс цэвэрлэгдлээ!\n\n/menu дарж дахин захиална уу.")

async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cart"] = {}
    await query.edit_message_text("🗑 Сагс цэвэрлэгдлээ!\n\n/menu дарж дахин захиална уу.")

async def ask_address(update, context):
    cart = get_cart(context)
    if not cart:
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text("🛒 Сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        else:
            await update.message.reply_text("🛒 Сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        return

    context.user_data["waiting_address"] = True
    text = "📍 *Хүргэлтийн хаяг оруулна уу:*\n\n"
    text += "Жишээ: Баянзүрх дүүрэг, 15-р хороо, 23-р байр, 45 тоот"

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")

async def checkout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ask_address(update, context)

async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ask_address(update, context)

async def receive_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("waiting_address"):
        return

    context.user_data["waiting_address"] = False
    address = update.message.text
    cart = get_cart(context)

    if not cart:
        await update.message.reply_text("🛒 Сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        return

    text = "✅ *Захиалга баталгаажлаа!*\n\n"
    total = 0
    n = 1
    for item_id, qty in cart.items():
        item = find_item_by_id(item_id)
        if not item:
            continue
        line_total = item["price"] * qty
        total += line_total
        if qty > 1:
            text += f"{n}. {item['name']} x{qty} — ₮{line_total:,}\n"
        else:
            text += f"{n}. {item['name']} — ₮{line_total:,}\n"
        n += 1

    text += f"\n{'─' * 25}\n"
    text += f"*Нийт: ₮{total:,}*\n\n"
    text += f"📍 *Хаяг:* {address}\n\n"
    text += "💳 *Төлбөрийн мэдээлэл:*\n"
    text += "🏦 Хаан банк\n"
    text += "📋 Данс: `5042 0811 2538`\n"
    text += "👤 Нэр: KFC Mongolia LLC\n\n"
    text += f"📌 Гүйлгээний утга: `KFC-{update.effective_user.id}`\n\n"
    text += "Төлбөрөө шилжүүлсний дараа хүргэлт 30-45 минутад ирнэ. 🛵\n\n"
    text += "📞 Лавлах: +976 7555-1010"

    context.user_data["cart"] = {}
    await update.message.reply_text(text, parse_mode="Markdown")

def get_handlers():
    return [
        CommandHandler("cart", cart_command),
        CommandHandler("clear", clear_command),
        CommandHandler("checkout", checkout_command),
        CallbackQueryHandler(show_cart_callback, pattern=r"^show_cart$"),
        CallbackQueryHandler(cart_plus_callback, pattern=r"^cplus:"),
        CallbackQueryHandler(cart_minus_callback, pattern=r"^cminus:"),
        CallbackQueryHandler(checkout_callback, pattern=r"^checkout$"),
        CallbackQueryHandler(clear_cart_callback, pattern=r"^clear_cart$"),
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address),
    ]
