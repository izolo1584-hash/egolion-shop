
import os
import asyncio
import logging
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery, LabeledPrice,
    PreCheckoutQuery, InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8579666403

bot = Bot(token=TOKEN)
dp = Dispatcher()

db = sqlite3.connect("shop.db")
db.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product TEXT,
    status TEXT
)
""")
db.commit()

PRODUCTS = {
    "Unturned Cheat": 50,
    "Roblox Cheat": 75,
}

@dp.message(CommandStart())
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{name} — ⭐ {price}",
            callback_data=f"buy:{name}"
        )]
        for name, price in PRODUCTS.items()
    ])

    await message.answer(
        "🦁 EGOLION - SHOP\n\nВыбери товар:",
        reply_markup=keyboard
    )

@dp.callback_query(F.data.startswith("buy:"))
async def buy(callback: CallbackQuery):
    product = callback.data.split(":", 1)[1]
    price = PRODUCTS[product]

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=product,
        description="Покупка в EGOLION - SHOP",
        payload=f"order:{product}",
        currency="XTR",
        prices=[LabeledPrice(label=product, amount=price)]
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await query.answer(ok=True)

@dp.message(F.successful_payment)
async def payment(message: Message):
    product = message.successful_payment.invoice_payload.split(":", 1)[1]

    cursor = db.execute(
        "INSERT INTO orders (user_id, product, status) VALUES (?, ?, ?)",
        (message.from_user.id, product, "paid")
    )
    db.commit()
    order_id = cursor.lastrowid

    await message.answer(
        f"✅ Оплата получена!\n"
        f"Заказ №{order_id}\n"
        f"Товар: {product}\n"
        "Ожидай ручную выдачу."
    )

    await bot.send_message(
        ADMIN_ID,
        f"🛒 НОВЫЙ ЗАКАЗ №{order_id}\n"
        f"Покупатель: {message.from_user.id}\n"
        f"Товар: {product}\n"
        f"Статус: оплачен"
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
