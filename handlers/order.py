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

async def clear_cart_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cart"] = []
    await query.edit_message_text("🗑 Сагс цэвэрлэгдлээ!\n\n/menu дарж дахин захиална уу.")

def get_handlers():
    return [
        CommandHandler("cart", cart_command),
        CommandHandler("clear", clear_command),
        CallbackQueryHandler(add_to_cart_callback, pattern=r"^add:"),
        CallbackQueryHandler(clear_cart_callback, pattern=r"^clear_cart$"),
    ]
