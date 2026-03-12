"""
Registon O'quv Markaz Bot — Main Entry Point
"""

import asyncio
import logging
import signal
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from database import db
from middlewares.auth import AuthMiddleware
from middlewares.state_cleanup import StateCleanupMiddleware
from handlers import start, registration, referral, contest, courses, admin

# ── Logging ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


# ── Main ───────────────────────────────────────────────────────

async def main():
    logger.info("🚀 Registon O'quv Markaz Bot ishga tushmoqda...")

    # Initialize database
    await db.init_db()
    logger.info("✅ Ma'lumotlar bazasi tayyor.")

    # Sync referral counts to fix any mismatches
    await db.sync_referral_counts()

    # Ensure superadmin exists
    await db.ensure_superadmin(config.superadmin_id)
    logger.info("✅ Superadmin tekshirildi: %s", config.superadmin_id)

    if config.required_channel:
        await db.ensure_default_channel(config.required_channel)
        logger.info("✅ Asosiy kanal: %s", config.required_channel)

    # Refresh button sets from DB labels
    from utils.i18n import refresh_btn_sets
    custom_labels = await db.get_all_settings()
    refresh_btn_sets(custom_labels)
    logger.info("✅ Tugma nomlari yangilandi.")

    # Create bot and dispatcher
    bot = Bot(
        token=config.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # ── Set bot profile info (shown BEFORE /start) ──────────
    # try:
    #     await bot.set_my_name("Registon O'quv Markaz")
    #     await bot.set_my_short_description(
    #         "🎓 Registon O'quv Markazining rasmiy boti | Bepul darsliklar | Konkurslar"
    #     )
    #     await bot.set_my_description(
    #         "🎓 Registon O'quv Markaz — rasmiy Telegram bot\n\n"
    #         "✅ Bepul darsliklar va video darslar\n"
    #         "🏆 Referal orqali konkursda qatnashing\n"
    #         "🎁 Do'stlaringizni taklif qilib sovg'alar yuting\n"
    #         "📚 O'quv materiallari — barcha fanlarbo'yicha\n\n"
    #         "Boshlash uchun — /start tugmasini bosing! 👇"
    #     )
    #     logger.info("✅ Bot tavsifi yangilandi.")
    # except Exception as e:
    #     logger.warning("Bot tavsifini yangilashda xato: %s", e)

    # Register middleware (on all updates)
    dp.update.outer_middleware(AuthMiddleware())
    dp.message.outer_middleware(StateCleanupMiddleware())
    dp.callback_query.outer_middleware(StateCleanupMiddleware())

    # Register all routers (order matters for priorities)
    dp.include_router(admin.router)       # Admin first (specific commands)
    dp.include_router(start.router)
    dp.include_router(registration.router)
    dp.include_router(referral.router)
    dp.include_router(contest.router)
    dp.include_router(courses.router)

    # Graceful shutdown
    async def shutdown():
        logger.info("🛑 Bot to'xtatilmoqda...")
        await dp.storage.close()
        await bot.session.close()

    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")

    try:
        await dp.start_polling(
            bot,
            skip_updates=True,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi.")
