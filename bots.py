# bot.py
# Telegram bot for earning stars/tasks system
# Stack:
# - aiogram 3
# - SQLite
# - Railway ready

import sqlite3
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio

TOKEN = "8937885622:AAHg8eWabUeKxJIQX4E70OdIgXQd9R-bNgk"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# =========================
# DATABASE
# =========================

db = sqlite3.connect("database.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    stars INTEGER DEFAULT 0,
    invited_by INTEGER DEFAULT NULL
)
""")

db.commit()

# =========================
# TASKS
# =========================

tasks = [
    {
        "id": 1,
        "text": "⭐ Поставь звезду GitHub репозиторию",
        "reward": 10
    },
    {
        "id": 2,
        "text": "📢 Подпишись на Telegram канал",
        "reward": 5
    },
    {
        "id": 3,
        "text": "👥 Пригласи друга",
        "reward": 20
    }
]

# =========================
# FUNCTIONS
# =========================

def add_user(user_id, username):
    cursor.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    )

    user = cursor.fetchone()

    if not user:
        cursor.execute(
            "INSERT INTO users (user_id, username, stars) VALUES (?, ?, ?)",
            (user_id, username, 0)
        )
        db.commit()


def get_balance(user_id):
    cursor.execute(
        "SELECT stars FROM users WHERE user_id = ?",
        (user_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return 0


def add_stars(user_id, amount):
    cursor.execute(
        "UPDATE users SET stars = stars + ? WHERE user_id = ?",
        (amount, user_id)
    )
    db.commit()


# =========================
# COMMANDS
# =========================

@dp.message(Command("start"))
async def start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    add_user(user_id, username)

    text = f"""
<b>🎉 Добро пожаловать!</b>

Ты можешь зарабатывать ⭐ звёзды выполняя задания.

📌 Команды:
    
/start - запуск
/profile - профиль
/tasks - задания
/daily - ежедневный бонус
/top - топ пользователей
/balance - баланс
"""

    await message.answer(text)


@dp.message(Command("profile"))
async def profile(message: Message):
    user_id = message.from_user.id
    stars = get_balance(user_id)

    text = f"""
👤 <b>Профиль</b>

🆔 ID: <code>{user_id}</code>
⭐ Звёзды: <b>{stars}</b>
"""

    await message.answer(text)


@dp.message(Command("balance"))
async def balance(message: Message):
    stars = get_balance(message.from_user.id)

    await message.answer(
        f"⭐ Твой баланс: <b>{stars}</b>"
    )


@dp.message(Command("tasks"))
async def show_tasks(message: Message):
    text = "<b>📋 Доступные задания:</b>\n\n"

    for task in tasks:
        text += (
            f"🆔 {task['id']}\n"
            f"{task['text']}\n"
            f"💰 Награда: {task['reward']} ⭐\n\n"
        )

    text += (
        "Для выполнения:\n"
        "/done ID\n\n"
        "Пример:\n"
        "/done 1"
    )

    await message.answer(text)


@dp.message(Command("done"))
async def complete_task(message: Message):
    try:
        args = message.text.split()

        if len(args) < 2:
            return await message.answer(
                "❌ Укажи ID задания"
            )

        task_id = int(args[1])

        found_task = None

        for task in tasks:
            if task["id"] == task_id:
                found_task = task
                break

        if not found_task:
            return await message.answer(
                "❌ Задание не найдено"
            )

        reward = found_task["reward"]

        add_stars(message.from_user.id, reward)

        await message.answer(
            f"✅ Задание выполнено!\n"
            f"⭐ Получено: {reward}"
        )

    except:
        await message.answer(
            "❌ Ошибка"
        )


@dp.message(Command("daily"))
async def daily_bonus(message: Message):
    reward = random.randint(5, 20)

    add_stars(message.from_user.id, reward)

    await message.answer(
        f"🎁 Ежедневный бонус!\n"
        f"⭐ Ты получил {reward} звёзд"
    )


@dp.message(Command("top"))
async def top_users(message: Message):
    cursor.execute(
        "SELECT username, stars FROM users ORDER BY stars DESC LIMIT 10"
    )

    users = cursor.fetchall()

    text = "<b>🏆 Топ пользователей:</b>\n\n"

    place = 1

    for user in users:
        username = user[0]
        stars = user[1]

        text += (
            f"{place}. @{username} — ⭐ {stars}\n"
        )

        place += 1

    await message.answer(text)


# =========================
# START
# =========================

async def main():
    print("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
