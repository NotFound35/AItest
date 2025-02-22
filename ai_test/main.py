import os
from telethon import TelegramClient, events
import openai
import difflib
import logging
from dotenv import load_dotenv

load_dotenv()
# Ваши данные
# api_id = '20590033'  # Укажите API_ID
# api_hash = '3c282ae507c0fbb7e9fcab64222e622e'  # Укажите API_HASH
# phone_number = '+35795145008'  # Ваш номер телефона в Telegram
# openai_api_key = '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'  # Ваш API-ключ OpenAI

# Настроим OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')
api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
# Создание клиента Telegram
client = TelegramClient('session_name', api_id, api_hash)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Пример товаров
products = {
    "001": {
        "name": "Умные часы",
        "description": "Умные часы с мониторингом здоровья и уведомлениями.",
        "price": 1999,
        "image": "https://example.com/smartwatch.jpg",
        "link": "https://example.com/buy/smartwatch"
    },
    "002": {
        "name": "Беспроводные наушники",
        "description": "Качественные беспроводные наушники с отличным звуком.",
        "price": 2999,
        "image": "https://example.com/headphones.jpg",
        "link": "https://example.com/buy/headphones"
    }
}

def get_product_recommendations(user_input):
    recommendations = []
    for product in products.values():
        # Поиск по названию и описанию (игнорируем регистр)
        match_name = difflib.get_close_matches(user_input.lower(), [product["name"].lower()], cutoff=0.5)
        match_desc = difflib.get_close_matches(user_input.lower(), [product["description"].lower()], cutoff=0.5)
        
        if match_name or match_desc:
            recommendations.append(product)

    return recommendations

async def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# def get_product_recommendations(user_input):
#     recommendations = []
#     for product_id, product in products.items():
#         if product["name"].lower() in user_input.lower() or product["description"].lower() in user_input.lower():
#             recommendations.append(product)
#     return recommendations

# Фильтр: реагировать только на ЛИЧНЫЕ сообщения
@client.on(events.NewMessage(func=lambda e: e.is_private))
async def my_event_handler(event):

    me = await client.get_me()
    if event.message.sender_id == me.id:
        return

    incoming_message = event.message.message
    logging.info(f"Получено сообщение: {incoming_message} от пользователя {event.message.sender_id}")
    
    # Получить рекомендации
    recommendations = get_product_recommendations(incoming_message)
    if recommendations:
        response = "Вот что я могу вам предложить:\n\n"
        logging.info(f"Найдено {len(recommendations)} предложений")
        for product in recommendations:
            response += f"{product['name']}\n{product['description']}\nЦена: {product['price']} рублей\n" \
                        f"![Изображение]({product['image']})\n" \
                        f"[Купить здесь]({product['link']})\n\n"
            
            logging.info(f"Отправлено предложение: {product['name']} пользователю {event.message.sender_id}")
    else:
        # Если нет предложений, отправляем запрос в AI
        try:
            response = await generate_response(incoming_message)
            logging.info(f"Ответ от OpenAI: {response}")
        except Exception as e:
            logging.error(f"Ошибка OpenAI: {e}")

    await event.reply(response)

async def main():
    await client.start()
    logging.info("Бот запущен, ожидаю сообщений...")
    await client.run_until_disconnected()

with client:
    client.loop.run_until_complete(main())


# import os
# from telethon import TelegramClient, events
# import openai


# # Ваши данные
# api_id = '20590033'
# api_hash = '3c282ae507c0fbb7e9fcab64222e622e'
# phone_number = '+35795145008'
# openai_api_key = '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'

# # Настроим OpenAI API
# openai.api_key = openai_api_key

# # Создание клиента Telegram
# client = TelegramClient('session_name', api_id, api_hash)

# # Пример товаров
# products = {
#     "001": {
#         "name": "Умные часы",
#         "description": "Умные часы с мониторингом здоровья и уведомлениями.",
#         "price": 1999,
#         "image": "https://example.com/smartwatch.jpg",
#         "link": "https://example.com/buy/smartwatch"
#     },
#     "002": {
#         "name": "Беспроводные наушники",
#         "description": "Качественные беспроводные наушники с отличным звуком.",
#         "price": 2999,
#         "image": "https://example.com/headphones.jpg",
#         "link": "https://example.com/buy/headphones"
#     }
# }

# async def generate_response(prompt):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": prompt}]
#     )
#     return response['choices'][0]['message']['content']

# def get_product_recommendations(user_input):
#     recommendations = []
#     for product_id, product in products.items():
#         if product["name"].lower() in user_input.lower() or product["description"].lower() in user_input.lower():
#             recommendations.append(product)
#     return recommendations

# @client.on(events.NewMessage())
# async def my_event_handler(event):
#     incoming_message = event.message.message
#     print(f"Получено сообщение: {incoming_message}")
#     # Получить рекомендации
#     recommendations = get_product_recommendations(incoming_message)
#     if recommendations:
#         response = "Вот что я могу вам предложить:\n\n"
#         for product in recommendations:
#             response += f"{product['name']}\n{product['description']}\nЦена: {product['price']} рублей\n" \
#                         f"![Изображение]({product['image']})\n" \
#                         f"[Купить здесь]({product['link']})\n\n"
#     else:
#         # Если нет предложений, отправляем запрос в AI
#         response = await generate_response(incoming_message)
#     await event.reply(response)

# async def main():
#     await client.start()
#     print("Бот запущен, ожидаю сообщений...")
#     await client.run_until_disconnected()
# with client:
#     client.loop.run_until_complete(main())




# import os
# import asyncio
# import openai
# import logging
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters import Command
# from openai import OpenAI
# from dotenv import load_dotenv

# load_dotenv()

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )

# # Загрузка токенов
# BOT_TOKEN = os.getenv("BOT_TOKEN")
# # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ALLOWED_USERS = set(map(int, os.getenv("ALLOWED_USERS", "").split(",")))

# # Инициализация бота
# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher()

# # Устанавливаем ключ API для OpenAI
# client = OpenAI(api_key="sk-87fca32327e74d63bb2f68787100a051", base_url)

# # Проверка пользователя
# async def is_allowed_user(user_id):
#     return user_id in ALLOWED_USERS

# # Обработка команд
# @dp.message(Command("start"))
# async def send_welcome(message: types.Message):
#     logging.info(f"Пользователь {message.from_user.id} залогинился в боте")

#     if not await is_allowed_user(message.from_user.id):
#         logging.warning(f"Пользователю {message.from_user.id} запрещен вход")
#         await message.reply("❌ У вас нет доступа к этому боту.")
#         return
#     await message.reply("🤖 Привет! Я бот-продавец. Напиши мне, что ты хочешь купить!")

# # Генерация текста с OpenAI
# @dp.message()
# async def chat_with_gpt(message: types.Message):
#     logging.info(f"Получено сообщение от пользователя {message.from_user.id} {message.text}")

#     if not await is_allowed_user(message.from_user.id):
#         logging.warning(f"Пользователь без доступа {message.from_user.id} пытается отправить запрос {message.text}")
#         await message.reply("❌ У вас нет доступа.")
#         return

#     try:
#         # Правильный вызов API OpenAI
#         response = openai.ChatCompletion.create(
#             model="deepseek-chat",
#             messages=[{"role": "user", "content": message.text}]
#         )
#         reply = response["choices"][0]["message"]["content"]
#     except Exception as e:
#         logging.error(f"Ошибка OpenAI: {e}")
#         reply = "⚠ Ошибка при обработке запроса."

#     await message.reply(reply)

# async def main():
#     dp.startup.register(lambda: logging.info("Бот запущен"))
#     await dp.start_polling(bot)

# # Запуск бота
# if __name__ == "__main__":
#     asyncio.run(main())
