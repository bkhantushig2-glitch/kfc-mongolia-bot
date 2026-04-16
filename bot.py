from telegram import Update, BotCommand
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from config import BOT_TOKEN
from handlers import menu, order, branches

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🍗 *KFC Mongolia Бот*-д тавтай морил!\n\n"
        "Энэ бот нь KFC Mongolia-н цэс үзэх,\n"
        "захиалга бүрдүүлэх, салбарын мэдээлэл\n"
        "авахад туслана.\n\n"
        "📋 /menu — Цэс харах\n"
        "🛒 /cart — Сагс харах\n"
        "🗑 /clear — Сагс цэвэрлэх\n"
        "📍 /branches — Салбарууд\n"
        "❓ /help — Тусламж",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *Тусламж*\n\n"
        "📋 /menu — KFC цэс харах, ангилалаар\n"
        "🛒 /cart — Сагсанд нэмсэн зүйлс харах\n"
        "🗑 /clear — Сагс хоослох\n"
        "📍 /branches — УБ дахь KFC салбарууд\n\n"
        "Цэснээс бүтээгдэхүүн сонгоод 🛒 товч\n"
        "дарж сагсанд нэмнэ үү!",
        parse_mode="Markdown"
    )

async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Ботыг эхлүүлэх"),
        BotCommand("menu", "Цэс харах"),
        BotCommand("cart", "Сагс харах"),
        BotCommand("clear", "Сагс цэвэрлэх"),
        BotCommand("branches", "Салбарууд"),
        BotCommand("help", "Тусламж"),
    ])

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    for handler in menu.get_handlers():
        app.add_handler(handler)
    for handler in order.get_handlers():
        app.add_handler(handler)
    for handler in branches.get_handlers():
        app.add_handler(handler)

    print("🍗 KFC Mongolia Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
