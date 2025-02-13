import logging

import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = settings.API_BASE_URL


# Function to get or create a user in the database
async def get_or_create_user(db: AsyncSession, telegram_id: int, username: str):
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user, True

    return user, False


# Command handler for /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"Received /start from {user.username} ({user.id})")

    is_new = False
    async for db in get_db():
        user_obj, is_new = await get_or_create_user(db, telegram_id=user.id, username=user.username)

    if is_new:
        message = (
            f"✅ Вітаємо, {user.first_name}!\n"
            f"Ви успішно зареєстровані в системі.\n\n"
            f"📌 Використовуйте кнопки нижче, щоб почати роботу:"
        )
    else:
        message = (
            f"👋 Вітаємо з поверненням, {user.first_name}!\n"
            f"Обирайте дію нижче:"
        )

    keyboard = [
        [InlineKeyboardButton("📋 Переглянути кімнати", callback_data="view_rooms")],
        [InlineKeyboardButton("➕ Створити кімнату", callback_data="create_room")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


# Function to handle button clicks
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "view_rooms":
        await view_rooms(update, context)
    elif data == "create_room":
        await ask_room_name(update, context)


# Function to view rooms
async def view_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    response = requests.get(f"{API_BASE_URL}/rooms/", headers={"telegram-id": str(user_id)})
    rooms = response.json()

    if isinstance(rooms, dict) and "error" in rooms:
        await query.message.reply_text("❌ Ви ще не створили жодної кімнати.")
        return

    if not rooms:
        await query.message.reply_text("⚠️ У вас поки що немає кімнат.")
        return

    message = "🏠 *Ваші кімнати:*\n\n"
    keyboard = []

    for room in rooms:
        message += f"🔹 *{room['name']}* (Код: `{room['invite_code']}`)\n"
        keyboard.append([InlineKeyboardButton(f"🔑 {room['name']}", callback_data=f"room_{room['id']}")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


# Function to ask for room name
async def ask_room_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.message.reply_text("📝 Введіть назву кімнати:")
    context.user_data["awaiting_room_name"] = True


# Function to create a room after receiving a name
async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "awaiting_room_name" not in context.user_data:
        return

    user_id = update.message.from_user.id
    room_name = update.message.text

    logger.info(f"Creating room: {room_name} for user {user_id}")

    response = requests.post(
        f"{API_BASE_URL}/rooms/",
        json={"name": room_name},
        headers={"telegram-id": str(user_id)}
    )
    result = response.json()

    logger.info(f"API Response: {result}")

    if "error" in result:
        await update.message.reply_text(f"❌ Помилка: {result['error']}")
    elif "name" not in result:
        await update.message.reply_text("⚠️ Сервер повернув неочікувану відповідь.")
    else:
        await update.message.reply_text(
            f"✅ *Кімнату створено!*\n"
            f"🏠 Назва: *{result.get('name', 'Unknown')}*\n"
            f"🔑 Код запрошення: `{result.get('invite_code', 'N/A')}`",
            parse_mode="Markdown"
        )

    del context.user_data["awaiting_room_name"]


# Function to run the bot
def run_bot():
    logger.info("Starting bot...")
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, create_room))

    app.run_polling()


if __name__ == "__main__":
    run_bot()
