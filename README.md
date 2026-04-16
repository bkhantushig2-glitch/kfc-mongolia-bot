# KFC Mongolia Telegram Bot 🍗

A Telegram bot for browsing the KFC Mongolia menu, building orders, and finding KFC locations in Ulaanbaatar. Built with Python and python-telegram-bot.

## Features

### /menu — Browse the Menu
Browse KFC Mongolia's menu by category using inline keyboard buttons:
- 🍗 Chicken (Original, Hot Wings, Strips)
- 🍔 Burgers (Zinger, Cheeseburger, Tower, Twister)
- 🎁 Combos (Family Box, Friends Box, meal combos)
- 🍟 Sides (Fries, Coleslaw, Rice)
- 🥤 Drinks (Cola, Fanta, Sprite)

Tap any item to add it to your cart!

### /cart — View Your Order
See everything in your cart with an itemized list and total in MNT (₮).

### /clear — Clear Cart
Start over with an empty cart.

### /branches — KFC Locations
Find all KFC branches in Ulaanbaatar with:
- Address (in Mongolian)
- Hours of operation
- Phone number

## Example Interaction

```
User: /start
Bot:  🍗 KFC Mongolia Бот-д тавтай морил!
      📋 /menu — Цэс харах
      🛒 /cart — Сагс харах
      📍 /branches — Салбарууд

User: /menu
Bot:  [Shows category buttons: Chicken, Burgers, Combos, Sides, Drinks]

User: [Taps "🍔 Бургер"]
Bot:  Shows burger list with prices and add-to-cart buttons

User: [Taps "🛒 Зингер Бургер ₮12,900"]
Bot:  ✅ Зингер Бургер нэмэгдлээ! Сагс: 1 зүйл, ₮12,900

User: /cart
Bot:  🛒 Таны захиалга:
      1. Зингер Бургер — ₮12,900
      ─────────────────────────
      Нийт: ₮12,900
```

## Setup

### Prerequisites
- Python 3.9+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Installation

```bash
git clone https://github.com/bkhantushig2-glitch/kfc-mongolia-bot.git
cd kfc-mongolia-bot
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:
```
BOT_TOKEN=your_telegram_bot_token_here
```

### Run

```bash
python bot.py
```

## Project Structure

```
kfc-mongolia-bot/
├── bot.py              # Main bot entry point
├── config.py           # Environment config
├── handlers/
│   ├── menu.py         # /menu command + category browsing
│   ├── order.py        # /cart, /clear + add-to-cart
│   └── branches.py     # /branches command
├── data/
│   ├── menu.json       # KFC menu items & prices (MNT)
│   └── branches.json   # KFC UB locations
├── requirements.txt
└── .gitignore
```

## Development

Developed using git worktrees for parallel feature development:

```bash
# Menu feature developed in separate worktree
git worktree add ../kfc-bot-menu feature/menu

# Order feature developed in parallel
git worktree add ../kfc-bot-order feature/order
```

Each feature tracked as a GitHub issue and developed on its own branch.

## Author

Batbold — American University of Mongolia, Ulaanbaatar
