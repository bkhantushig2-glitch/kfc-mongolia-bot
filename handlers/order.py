from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers.menu import find_item_by_id

async def add_to_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    item_id = query.data.replace("add:", "")
    item = find_item_by_id(item_id)

    if not item:
        await query.answer("Бүтээгдэхүүн олдсонгүй!")
        return

    if "cart" not in context.user_data:
        context.user_data["cart"] = []

    context.user_data["cart"].append({
        "id": item["id"],
        "name": item["name"],
        "price": item["price"]
    })

    total = sum(i["price"] for i in context.user_data["cart"])
    count = len(context.user_data["cart"])
    await query.answer(f"✅ {item['name']} нэмэгдлээ! Сагс: {count} зүйл, ₮{total:,}")

async def undo_last_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cart = context.user_data.get("cart", [])
    if cart:
        removed = cart.pop()
        await query.answer(f"❌ {removed['name']} хасагдлаа!")
    else:
        await query.answer("Сагс хоосон байна!")

async def remove_item_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    idx = int(query.data.replace("rm:", ""))
    cart = context.user_data.get("cart", [])

    if idx < len(cart):
        removed = cart.pop(idx)
        await query.answer(f"❌ {removed['name']} хасагдлаа!")
    else:
        await query.answer("Олдсонгүй!")

    if not cart:
        await query.edit_message_text("🛒 Сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        return

    text = "🛒 *Таны захиалга:*\n\n"
    keyboard = []
    for i, item in enumerate(cart):
        text += f"{i+1}. {item['name']} — ₮{item['price']:,}\n"
        keyboard.append([InlineKeyboardButton(f"❌ {item['name']}", callback_data=f"rm:{i}")])

    total = sum(i["price"] for i in cart)
    text += f"\n{'─' * 25}\n"
    text += f"*Нийт: ₮{total:,}*\n"
    text += f"📦 {len(cart)} зүйл"

    keyboard.append([InlineKeyboardButton("💳 Төлбөр төлөх", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🗑 Бүгдийг цэвэрлэх", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton("📋 Цэс харах", callback_data="back_to_menu")])

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    if not cart:
        await update.message.reply_text(
            "🛒 Таны сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!"
        )
        return

    text = "🛒 *Таны захиалга:*\n\n"
    keyboard = []
    for i, item in enumerate(cart):
        text += f"{i+1}. {item['name']} — ₮{item['price']:,}\n"
        keyboard.append([InlineKeyboardButton(f"❌ {item['name']}", callback_data=f"rm:{i}")])

    total = sum(i["price"] for i in cart)
    text += f"\n{'─' * 25}\n"
    text += f"*Нийт: ₮{total:,}*\n"
    text += f"📦 {len(cart)} зүйл"

    keyboard.append([InlineKeyboardButton("💳 Төлбөр төлөх", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🗑 Бүгдийг цэвэрлэх", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton("📋 Цэс харах", callback_data="back_to_menu")])

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cart"] = []
    await update.message.reply_text("🗑 Сагс цэвэрлэгдлээ!\n\n/menu дарж дахин захиална уу.")

async def ask_address(update, context):
    cart = context.user_data.get("cart", [])
    if not cart:
        if hasattr(update, "callback_query") and update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text("🛒 Сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        else:
            await update.message.reply_text("🛒 Таны сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        return

    context.user_data["waiting_address"] = True
    text = "📍 *Хүргэлтийн хаяг оруулна уу:*\n\n"
    text += "Жишээ: Баянзүрх дүүрэг, 15-р хороо, 23-р байр, 45 тоот"

    if hasattr(update, "callback_query") and update.callback_query:
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
    cart = context.user_data.get("cart", [])

    if not cart:
        await update.message.reply_text("🛒 Сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        return

    text = "✅ *Захиалга баталгаажлаа!*\n\n"
    for i, item in enumerate(cart, 1):
        text += f"{i}. {item['name']} — ₮{item['price']:,}\n"

    total = sum(i["price"] for i in cart)
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

    context.user_data["cart"] = []

    await update.message.reply_text(text, parse_mode="Markdown")

async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cart"] = []
    await query.edit_message_text("🗑 Сагс цэвэрлэгдлээ!\n\n/menu дарж дахин захиална уу.")

def get_handlers():
    return [
        CommandHandler("cart", cart_command),
        CommandHandler("clear", clear_command),
        CommandHandler("checkout", checkout_command),
        CallbackQueryHandler(add_to_cart_callback, pattern=r"^add:"),
        CallbackQueryHandler(remove_item_callback, pattern=r"^rm:"),
        CallbackQueryHandler(checkout_callback, pattern=r"^checkout$"),
        CallbackQueryHandler(clear_cart_callback, pattern=r"^clear_cart$"),
        MessageHandler(filters.TEXT & ~filters.COMMAND, receive_address),
    ]
