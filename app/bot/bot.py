import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            f"Вітаємо, {user.first_name}!\n"
            f"Ви успішно зареєстровані в нашій системі!\n"
            f"Тепер ви можете створювати та керувати своїми списками покупок."
        )
    else:
        message = (
            f"Вітаємо з поверненням, {user.first_name}!\n"
            f"Готові продовжити керування своїми списками покупок?"
        )

    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


# Function to run the bot
def run_bot():
    logger.info("Starting bot...")
    app = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    run_bot()