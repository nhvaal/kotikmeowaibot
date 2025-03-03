# import os
import logging
import asyncio
import requests
# from dotenv import load_dotenv
from config import API_TOKEN,OPENROUTER_API_KEY
from aiogram.filters import Command
from aiogram import Bot, Dispatcher, types

# Загружаю переменные окружения из .env
# load_dotenv()

# API_TOKEN = os.getenv("API_TOKEN")
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Словарь для хранения истории диалогов пользователей
user_histories = {}
MAX_HISTORY = 10000  # Максимальное количество сообщений в истории

# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_histories[message.from_user.id] = []  # Очистка истории при старте
    await message.reply("Приветик! Я твой котик. Поболтай со мной)." )

# Обработчик команды /help
@dp.message(Command("help"))
async def send_help(message: types.Message):
    await message.reply("Я могу отвечать на твои смсочки, напиши мне!")

# Обработчик текстовых сообщений
@dp.message()
async def chat(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text
    print(f"[LOG] ({user_id}) Получено сообщение: {user_text}")
    # Загружаю историю диалога пользователя
    if user_id not in user_histories:
        user_histories[user_id] = []
    # Добавляю текущее сообщение пользователя в историю
    user_histories[user_id].append({"role": "user", "content": user_text})
    # Обрезаю историю, если она превышает лимит
    user_histories[user_id] = user_histories[user_id][-MAX_HISTORY:]
    try:
        # Отправка сообщения в OpenAI API
        response = requests.post("https://openrouter.ai/api/v1/chat/completions",
                                 headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}",
                                          "Content-Type": "application/json"},
                                 json={"model": "openai/gpt-3.5-turbo-0613",
                                       "messages": user_histories[user_id]}) # Передаю всю историю
        # Получение ответа от OpenRouter API
        if response.status_code == 200:
            reply = response.json()["choices"][0]["message"]["content"]
            # Добавляю ответ бота в историю
            user_histories[user_id].append({"role": "assistant", "content": reply})
            user_histories[user_id] = user_histories[user_id][-MAX_HISTORY:]  # Обрезаю историю
            await message.reply(reply)
        else:
            # Сообщение об ошибке
            error_message = response.json().get("error", {}).get("message", "Неизвестная ошибка")
            await message.reply(f"Ошибка: {error_message}")
    except Exception as e:
        # Cообщение об ошибке
        logging.exception("Ошибочка:")
        await message.reply(f"Произошла ошибочка: {str(e)}")

#запуск бота
async def main():
    print('кот тут')
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())