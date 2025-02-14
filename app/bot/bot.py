import logging
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_BASE_URL = settings.API_BASE_URL

# -------------------- User Authentication --------------------

async def get_or_create_user(db: AsyncSession, telegram_id: int, username: str):
    """
    Check if a user exists in the database; if not, create a new one.
    """
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle the /start command and register the user if necessary.
    """
    user = update.effective_user
    logger.info(f"Received /start from {user.username} ({user.id})")
    async for db in get_db():
        await get_or_create_user(db, telegram_id=user.id, username=user.username)
    message = (
        f"✅ Вітаємо, {user.first_name}!\n"
        "📌 Оберіть одну з кнопок нижче для початку роботи:"
    )
    keyboard = [
        [InlineKeyboardButton("📋 Переглянути кімнати", callback_data="view_rooms")],
        [InlineKeyboardButton("➕ Створити кімнату", callback_data="create_room")],
        [InlineKeyboardButton("🔑 Приєднатися до кімнати", callback_data="join_room")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

# -------------------- Button Handling --------------------

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle inline button presses.
    """
    query = update.callback_query
    data = query.data
    logger.info(f"User {query.from_user.id} pressed button: {data}")
    if data == "view_rooms":
        await view_rooms(update, context)
    elif data == "create_room":
        await ask_room_name(update, context)
    elif data == "join_room":
        await ask_invite_code(update, context)
    elif data == "leave_room":
        await leave_room_handler(update, context)
    elif data == "create_shopping_list":
        # Placeholder for creating a shopping list
        await query.answer()
        await query.message.reply_text("🛒 Функція створення списку покупок незабаром буде доступна!")
    elif data == "view_shopping_list":
        # Placeholder for viewing a shopping list
        await query.answer()
        await query.message.reply_text("📜 Функція перегляду списку покупок незабаром буде доступна!")
    else:
        await query.answer("Невідома дія.")

# -------------------- View Rooms --------------------

async def view_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Fetch and display the list of user's rooms.
    """
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/rooms/",
                headers={"telegram-id": str(user_id)},
            )
        rooms = response.json()
    except Exception as e:
        logger.error(f"Error fetching rooms: {e}")
        await query.message.reply_text("❌ Помилка при отриманні кімнат.")
        return

    if isinstance(rooms, dict) and "error" in rooms:
        await query.message.reply_text("❌ У Вас ще немає створених кімнат.")
        return
    if not rooms:
        await query.message.reply_text("⚠️ Кімнати відсутні.")
        return

    message = "🏠 *Ваші кімнати:*\n\n"
    keyboard = []
    for room in rooms:
        message += f"🔹 *{room['name']}* (Код запрошення: {room['invite_code']})\n"
        keyboard.append([InlineKeyboardButton(f"🔑 {room['name']}", callback_data=f"room_{room['id']}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

# -------------------- Create Room --------------------

async def ask_room_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Prompt the user to enter a room name.
    """
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("📝 Введіть назву кімнати:")
    context.user_data["awaiting_room_name"] = True

async def create_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Create a room after receiving the room name.
    """
    if not context.user_data.get("awaiting_room_name"):
        return
    user_id = update.message.from_user.id
    room_name = update.message.text.strip()
    logger.info(f"Creating room: {room_name} for user {user_id}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/rooms/",
                json={"name": room_name},
                headers={"telegram-id": str(user_id)},
            )
        result = response.json()
    except Exception as e:
        logger.error(f"Error creating room: {e}")
        await update.message.reply_text("❌ Помилка при створенні кімнати.")
        context.user_data.pop("awaiting_room_name", None)
        return

    if "error" in result:
        await update.message.reply_text(f"❌ Помилка: {result['error']}")
    else:
        await update.message.reply_text(
            f"✅ *Кімната створена!*\n"
            f"🏠 Назва: *{result.get('name', 'Невідома')}*\n"
            f"🔑 Код запрошення: {result.get('invite_code', 'N/A')}",
            parse_mode="Markdown",
        )
    context.user_data.pop("awaiting_room_name", None)

# -------------------- Join Room --------------------

async def ask_invite_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Prompt the user to enter an invitation code.
    """
    query = update.callback_query
    await query.answer()
    logger.info(f"User {query.from_user.id} wants to join a room.")
    await query.message.reply_text("🔑 Введіть код запрошення:")
    context.user_data["awaiting_invite_code"] = True

async def join_room(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Join a room using an invitation code and display a dynamic menu.
    """
    if not context.user_data.get("awaiting_invite_code"):
        return
    user_id = update.message.from_user.id
    invite_code = update.message.text.strip()
    logger.info(f"User {user_id} attempting to join room with code {invite_code}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/rooms/join/{invite_code}",
                headers={"telegram-id": str(user_id)},
            )
        if response.status_code == 200:
            result = response.json()
            room_name = result.get("name", "Невідома")
            # Assuming the API returns a room id; if not, use invite_code as an identifier.
            room_id = result.get("id", invite_code)
            # Save the current room info in user_data
            context.user_data["current_room"] = room_id

            # Build a dynamic menu for room actions
            keyboard = [
                [InlineKeyboardButton("🛒 Створити список покупок", callback_data="create_shopping_list")],
                [InlineKeyboardButton("📜 Переглянути список покупок", callback_data="view_shopping_list")],
                [InlineKeyboardButton("🚪 Вийти з кімнати", callback_data="leave_room")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"🎉 *Ви приєдналися до кімнати!*\n🏠 Назва: *{room_name}*\n\n"
                "Тут ви можете створювати або переглядати свій список покупок.",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN,
            )
        elif response.status_code == 409:
            await update.message.reply_text(
                "❗ *Ви вже є учасником цієї кімнати!*",
                parse_mode=ParseMode.MARKDOWN,
            )
        elif response.status_code == 404:
            await update.message.reply_text(
                "❌ *Кімната не знайдена!*",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            result = response.json()
            detail = result.get("detail", "Щось пішло не так.")
            await update.message.reply_text(f"❌ Помилка: {detail}", parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error joining room: {e}")
        await update.message.reply_text("❌ Помилка при приєднанні до кімнати.")
    context.user_data.pop("awaiting_invite_code", None)

# -------------------- Leave Room Handler --------------------

async def leave_room_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    current_room = context.user_data.get("current_room")
    if not current_room:
        await query.edit_message_text("Ви не знаходитеся в кімнаті.")
        return

    user_id = query.from_user.id
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{API_BASE_URL}/rooms/{current_room}/leave",
                headers={"telegram-id": str(user_id)},
            )
        if response.status_code == 200:
            await query.edit_message_text("🚪 Ви успішно покинули кімнату.")

            context.user_data.pop("current_room", None)

            keyboard = [
                [InlineKeyboardButton("📋 Переглянути кімнати", callback_data="view_rooms")],
                [InlineKeyboardButton("➕ Створити кімнату", callback_data="create_room")],
                [InlineKeyboardButton("🔑 Приєднатися до кімнати", callback_data="join_room")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(
                chat_id=query.message.chat.id,
                text="Виберіть одну з кнопок для подальших дій:",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("❌ Помилка при виході з кімнати.")
    except Exception as e:
        logger.error(f"Error leaving room: {e}")
        await query.edit_message_text("❌ Помилка з'єднання з сервером.")

# -------------------- Unified Text Handler --------------------

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Unified text handler that calls create_room or join_room based on flags.
    """
    if context.user_data.get("awaiting_room_name"):
        await create_room(update, context)
    elif context.user_data.get("awaiting_invite_code"):
        await join_room(update, context)
    else:
        await update.message.reply_text("Будь ласка, скористайтеся кнопками меню або введіть потрібну інформацію.")

# -------------------- Run Bot --------------------

def run_bot():
    """
    Start the Telegram bot.
    """
    logger.info("Запуск бота...")
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    run_bot()