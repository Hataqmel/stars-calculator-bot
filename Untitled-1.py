import logging
import urllib.request
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiohttp import web

# Токен вашего бота от @BotFather
API_TOKEN = '8903668038:AAEKRPbwGJSrmHJ6uYqde6y-gbW_U_HcPCY'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

STARS_USD_PAYOUT = 0.013
RETAIL_RUB_RATE = 1.8

def get_usd_to_rub():
    try:
        url = "https://er-api.com"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return data['rates']['RUB']
    except Exception as e:
        logging.error(f"Ошибка получения курса: {e}")
        return 95.0

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="📊 Актуальные курсы"))
    builder.add(types.KeyboardButton(text="🧮 Калькулятор"))
    await message.answer(
        "👋 Привет! Я бот-калькулятор курсов Telegram Stars.\n"
        "Помогу рассчитать выгоду при покупке или выводе звезд.",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )

@dp.message(lambda message: message.text == "📊 Актуальные курсы")
async def show_rates(message: types.Message):
    usd_rub = get_usd_to_rub()
    author_rub = STARS_USD_PAYOUT * usd_rub
    text = (
        f"💵 **Текущие курсы Stars:**\n\n"
        f"🛒 **Покупка (Рынок):** ~{RETAIL_RUB_RATE} ₽ за 1 шт.\n"
        f"💰 **Вывод авторов:** ${STARS_USD_PAYOUT} ≈ {author_rub:.2f} ₽ за 1 шт.\n\n"
        f"📈 Курс USD/RUB: {usd_rub:.2f} ₽"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(lambda message: message.text == "🧮 Калькулятор")
async def ask_amount(message: types.Message):
    await message.answer("Введите количество Stars для расчета (например: 1000):")

@dp.message()
async def calculate_stars(message: types.Message):
    if not message.text.isdigit():
        return
    stars_count = int(message.text)
    usd_rub = get_usd_to_rub()
    buy_total = stars_count * RETAIL_RUB_RATE
    payout_usd = stars_count * STARS_USD_PAYOUT
    payout_rub = payout_usd * usd_rub
    text = (
        f"🧮 **Расчет для {stars_count:,} Stars:**\n\n"
        f"🛒 **Ориентировочная покупка:** {buy_total:,} ₽\n"
        f"📥 **Официальный вывод (до комиссий):**\n"
        f"└ В долларах: ${payout_usd:.2f}\n"
        f"└ В рублей: {payout_rub:.2f} ₽\n\n"
        f"_Примечание: При выводе через Fragment учитывайте холд 21 день и комиссию сети TON (~1-5%)._"
    )
    await message.answer(text, parse_mode="Markdown")

# Крошечный веб-сервер для обмана бесплатного тарифа Render
async def handle_web(request):
    return web.Response(text="Бот работает!")

async def main():
    # Запуск веб-сервера на порту 10000 (стандарт для Render)
    app = web.Application()
    app.router.add_get('/', handle_web)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    asyncio.create_task(site.start())
    
    # Запуск опроса Telegram
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
