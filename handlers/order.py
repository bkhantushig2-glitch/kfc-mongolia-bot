from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
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

async def cart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    if not cart:
        await update.message.reply_text(
            "🛒 Таны сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!"
        )
        return

    text = "🛒 *Таны захиалга:*\n\n"
    for i, item in enumerate(cart, 1):
        text += f"{i}. {item['name']} — ₮{item['price']:,}\n"

    total = sum(i["price"] for i in cart)
    text += f"\n{'─' * 25}\n"
    text += f"*Нийт: ₮{total:,}*\n"
    text += f"📦 {len(cart)} зүйл"

    keyboard = [
        [InlineKeyboardButton("💳 Төлбөр төлөх", callback_data="checkout")],
        [InlineKeyboardButton("🗑 Сагс цэвэрлэх", callback_data="clear_cart")],
        [InlineKeyboardButton("📋 Цэс харах", callback_data="back_to_menu")],
    ]

    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["cart"] = []
    await update.message.reply_text("🗑 Сагс цэвэрлэгдлээ!\n\n/menu дарж дахин захиална уу.")

async def checkout_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get("cart", [])
    if not cart:
        await update.message.reply_text(
            "🛒 Таны сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!"
        )
        return

    text = "✅ *Захиалга баталгаажлаа!*\n\n"
    for i, item in enumerate(cart, 1):
        text += f"{i}. {item['name']} — ₮{item['price']:,}\n"

    total = sum(i["price"] for i in cart)
    text += f"\n{'─' * 25}\n"
    text += f"*Нийт: ₮{total:,}*\n\n"
    text += "💳 *Төлбөрийн мэдээлэл:*\n"
    text += "🏦 Хаан банк\n"
    text += "📋 Данс: `5042 0811 2538`\n"
    text += "👤 Нэр: KFC Mongolia LLC\n\n"
    text += f"📌 Гүйлгээний утга: `KFC-{update.effective_user.id}`\n\n"
    text += "Төлбөрөө шилжүүлсний дараа хүргэлт 30-45 минутад ирнэ. 🛵\n\n"
    text += "📞 Лавлах: +976 7555-1010"

    context.user_data["cart"] = []

    await update.message.reply_text(text, parse_mode="Markdown")

async def checkout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cart = context.user_data.get("cart", [])
    if not cart:
        await query.edit_message_text("🛒 Сагс хоосон байна.\n\n/menu дарж захиалга өгнө үү!")
        return

    text = "✅ *Захиалга баталгаажлаа!*\n\n"
    for i, item in enumerate(cart, 1):
        text += f"{i}. {item['name']} — ₮{item['price']:,}\n"

    total = sum(i["price"] for i in cart)
    text += f"\n{'─' * 25}\n"
    text += f"*Нийт: ₮{total:,}*\n\n"
    text += "💳 *Төлбөрийн мэдээлэл:*\n"
    text += "🏦 Хаан банк\n"
    text += "📋 Данс: `5042 0811 2538`\n"
    text += "👤 Нэр: KFC Mongolia LLC\n\n"
    text += f"📌 Гүйлгээний утга: `KFC-{query.from_user.id}`\n\n"
    text += "Төлбөрөө шилжүүлсний дараа хүргэлт 30-45 минутад ирнэ. 🛵\n\n"
    text += "📞 Лавлах: +976 7555-1010"

    context.user_data["cart"] = []

    await query.edit_message_text(text, parse_mode="Markdown")

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
        CallbackQueryHandler(checkout_callback, pattern=r"^checkout$"),
        CallbackQueryHandler(clear_cart_callback, pattern=r"^clear_cart$"),
    ]
