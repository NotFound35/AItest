import os
import re
import threading
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from database import init_chat_db, save_message, get_chat_history, clear_chat_history, init_payment_db, save_payment, has_paid, get_allowed_users_from_db
import openai


load_dotenv()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = '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'


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


openai.api_key = OPENAI_API_KEY


init_chat_db()
init_payment_db()


PRODUCTS = {
    "магний": {
        "title": "Магний B6",
        "description": "Поддерживает работу нервной системы и снимает стресс.",
        "price": "1200₽",
        "link": "https://example.com/magnesium"
    },
    "витамин c": {
        "title": "Витамин C",
        "description": "Укрепляет иммунитет и помогает бороться с инфекциями.",
        "price": "900₽",
        "link": "https://example.com/vitamin-c"
    },
    "омега-3": {
        "title": "Омега-3",
        "description": "Поддерживает здоровье сердца и сосудов.",
        "price": "1500₽",
        "link": "https://example.com/omega-3"
    }
}



async def check_payment(user_id):
    return has_paid(user_id)

def recommend_product(user_message):
    user_message = user_message.lower()
    for keyword, product in PRODUCTS.items():
        if keyword in user_message:
            return product
    return None

def update_allowed_users_periodically():
    global ALLOWED_USERS
    ALLOWED_USERS = get_allowed_users_from_db()
    print(f"Список разрешенных пользователей обновлен: {ALLOWED_USERS}")
    threading.Timer(60, update_allowed_users_periodically).start()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    if await check_payment(user_id):
        await message.reply("✅ Оплата подтверждена! Вы можете начать использовать бота. Используйте команду /newchat [название чата].")
    else:
        save_payment(user_id)
        await message.reply("💳 Привет! Чтобы получить доступ к функционалу бота, вам нужно оплатить. \n Реквизиты перевода: \n После оплаты Вы можете использовать команду /pay.")


@dp.message(Command("pay"))
async def process_payment(message: types.Message):
    user_id = message.from_user.id
    if await check_payment(user_id):
        await message.reply("✅ Оплата успешно подтверждена! Теперь вы можете начать диалог с помощью команды /newchat [название чата].")
    else:
        save_payment(user_id)
        await message.reply("💳 Оплата успешно подтверждена! Теперь вы можете начать диалог с помощью команды /newchat [название чата].")


@dp.message(Command("newchat"))
async def new_chat(message: types.Message):
    user_id = message.from_user.id
    if not await check_payment(user_id):
        await message.reply("❌ У вас нет доступа. Пожалуйста, оплатите с помощью команды /pay.")
        return

    chat_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "default"
    save_message(user_id, chat_name, "system", f"Начат новый чат: {chat_name}")
    await message.reply(f"✨ Новый чат создан: {chat_name} \n Начните общение с ботом.")


@dp.message()
async def chat_with_gpt(message: types.Message):
    user_id = message.from_user.id
    if not await check_payment(user_id):
        await message.reply("❌ У вас нет доступа. Пожалуйста, оплатите с помощью команды /pay.")
        return

    chat_name = "default"
    history = get_chat_history(user_id, chat_name)
    history.append({"role": "user", "content": message.text})

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=history
        )
        bot_reply = response['choices'][0]['message']['content']

        product = recommend_product(message.text)
        if product:
            bot_reply += f"\n\n🌿 *Рекомендую попробовать:* *{product['title']}*\n{product['description']}\n💰 Цена: {product['price']}\n🔗 [Купить]({product['link']})"

        save_message(user_id, chat_name, "user", message.text)
        save_message(user_id, chat_name, "assistant", bot_reply)

    except Exception as e:
        logging.error(f"Ошибка OpenAI: {e}")
        bot_reply = "⚠ Произошла ошибка при запросе к нейросети."

    await message.reply(bot_reply, parse_mode="Markdown", disable_web_page_preview=False)


@dp.message(Command("clear"))
async def clear_history(message: types.Message):
    user_id = message.from_user.id
    if not await check_payment(user_id):
        await message.reply("❌ У вас нет доступа. Пожалуйста, оплатите с помощью команды /pay.")
        return

    chat_name = "default"
    clear_chat_history(user_id, chat_name)
    await message.reply("🧹 История чата очищена!")

async def main():
    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

# import os
# import re
# import threading
# import asyncio
# import logging
# import asyncpg
# from aiogram import Bot, Dispatcher, types
# from aiogram.filters import Command
# from dotenv import load_dotenv
# from database import init_chat_db, save_message, get_chat_history, clear_chat_history
# import openai


# load_dotenv()


# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )


# BOT_TOKEN = os.getenv("BOT_TOKEN")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# DATABASE_URL = os.getenv("DATABASE_URL")


# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher()


# openai.api_key = OPENAI_API_KEY


# init_chat_db()


# PRODUCTS = {
#     "магний": {"title": "Магний B6", "description": "Поддерживает работу нервной системы и снимает стресс.", "price": "1200₽", "link": "https://example.com/magnesium"},
#     "витамин c": {"title": "Витамин C", "description": "Укрепляет иммунитет и помогает бороться с инфекциями.", "price": "900₽", "link": "https://example.com/vitamin-c"},
#     "омега-3": {"title": "Омега-3", "description": "Поддерживает здоровье сердца и сосудов.", "price": "1500₽", "link": "https://example.com/omega-3"}
# }


# async def create_pool():
#     return await asyncpg.create_pool(DATABASE_URL)

# async def get_payment_status(user_id):
#     async with await create_pool() as pool:
#         result = await pool.fetchrow('SELECT paid FROM users WHERE user_id = $1', user_id)
#         return result['paid'] if result else False


# @dp.message(Command("start"))
# async def send_welcome(message: types.Message):
#     user_id = message.from_user.id
#     if await get_payment_status(user_id):
#         await message.reply("✅ Оплата подтверждена! Вы можете начать использовать бота. Используйте команду /newchat [название чата].")
#     else:
#         await message.reply("💳 Привет! Чтобы получить доступ к функционалу бота, вам нужно оплатить. После оплаты используйте команду /pay.")


# @dp.message(Command("pay"))
# async def process_payment(message: types.Message):
#     user_id = message.from_user.id
#     if await get_payment_status(user_id):
#         await message.reply("✅ Оплата уже подтверждена! Можете начать использовать бота.")
#     else:
#         await message.reply("💳 Если вы оплатили, ожидайте подтверждения в базе данных.")


# @dp.message(Command("newchat"))
# async def new_chat(message: types.Message):
#     user_id = message.from_user.id
#     if not await get_payment_status(user_id):
#         await message.reply("❌ У вас нет доступа. Пожалуйста, оплатите с помощью команды /pay.")
#         return

#     chat_name = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else "default"
#     save_message(user_id, chat_name, "system", f"Начат новый чат: {chat_name}")
#     await message.reply(f"✨ Новый чат создан: {chat_name} \n Начните общение с ботом.")


# @dp.message()
# async def chat_with_gpt(message: types.Message):
#     user_id = message.from_user.id
#     if not await get_payment_status(user_id):
#         await message.reply("❌ У вас нет доступа. Пожалуйста, оплатите с помощью команды /pay.")
#         return

#     chat_name = "default" 
#     history = get_chat_history(user_id, chat_name)
#     history.append({"role": "user", "content": message.text})

#     try:
#         response = await openai.ChatCompletion.acreate(model="gpt-4o", messages=history)
#         bot_reply = response['choices'][0]['message']['content']

#         product = recommend_product(message.text)
#         if product:
#             bot_reply += f"\n\n🌿 *Рекомендую попробовать:* *{product['title']}*\n{product['description']}\n💰 Цена: {product['price']}\n🔗 [Купить]({product['link']})"

#         save_message(user_id, chat_name, "user", message.text)
#         save_message(user_id, chat_name, "assistant", bot_reply)
#     except Exception as e:
#         logging.error(f"Ошибка OpenAI: {e}")
#         bot_reply = "⚠ Произошла ошибка при запросе к нейросети."

#     await message.reply(bot_reply, parse_mode="Markdown", disable_web_page_preview=False)


# @dp.message(Command("clear"))
# async def clear_history(message: types.Message):
#     user_id = message.from_user.id
#     if not await get_payment_status(user_id):
#         await message.reply("❌ У вас нет доступа. Пожалуйста, оплатите с помощью команды /pay.")
#         return

#     chat_name = "default"
#     clear_chat_history(user_id, chat_name)
#     await message.reply("🧹 История чата очищена!")


# async def main():
#     logging.info("Бот запущен")
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())
