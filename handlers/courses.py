"""
Courses handler — free lessons from private channel -1003816800490.
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from config import config
from database import db
from keyboards.user_kb import courses_kb, back_kb
from utils.channel_check import check_subscriptions
from utils.i18n import t, BTN_COURSES

logger = logging.getLogger(__name__)
router = Router(name="courses")

COURSES_CHANNEL = config.courses_channel  # Yopiq kanal ID


async def _show_course_categories(send_fn, user_id: int, lang: str = "uz"):
    """Show category choice: Darsliklar or Majburiy blok darslar."""
    from keyboards.user_kb import course_categories_kb
    settings = await db.get_all_settings()
    
    std_active = settings.get("standard_lessons_active") != "0"
    man_active = settings.get("mandatory_lessons_active") != "0"
    
    text = settings.get("text_courses_main") or t("courses_title", lang)
    await send_fn(text, reply_markup=course_categories_kb(
        lang=lang, 
        standard_active=std_active, 
        mandatory_active=man_active,
        labels=settings
    ))


async def _show_courses_list(send_fn, user_id: int, bot: Bot, category: str = "standard", edit: bool = False):
    """Shared logic: show courses list by category."""
    lang = await db.get_user_language(user_id)
    courses = await db.get_active_courses(category=category)
    settings = await db.get_all_settings()
    
    if not courses:
        text = t("courses_empty", lang)
        from keyboards.user_kb import course_categories_kb
        std_active = settings.get("standard_lessons_active") != "0"
        man_active = settings.get("mandatory_lessons_active") != "0"
        await send_fn(text, reply_markup=course_categories_kb(
            lang=lang, 
            standard_active=std_active, 
            mandatory_active=man_active,
            labels=settings
        ))
        return

    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    
    if category == "standard":
        cat_name = settings.get("label_btn_standard") or t("btn_standard_courses", lang)
        header = settings.get("text_courses_standard") or f"📚 <b>{cat_name.upper()}</b>"
    else:
        cat_name = settings.get("label_btn_mandatory") or t("btn_mandatory_courses", lang)
        header = settings.get("text_courses_mandatory") or f"🔐 <b>{cat_name.upper()}</b>"
        
    lines = [f"{header}\n"]
    for i, course in enumerate(courses):
        emoji = emojis[i] if i < len(emojis) else "📖"
        desc = f" — {course['description']}" if course["description"] else ""
        lines.append(f"{emoji} {course['title']}{desc}")

    text = "\n".join(lines)
    from keyboards.user_kb import courses_kb
    await send_fn(text, reply_markup=courses_kb(courses))


# ── ReplyKeyboard button ───────────────────────────────────────

@router.message(F.text.in_(BTN_COURSES))
async def menu_courses(message: Message, bot: Bot, state: FSMContext):
    """Handle ReplyKeyboard courses button."""
    await state.clear()
    user_id = message.from_user.id
    channels = await db.get_active_channels()
    all_sub, results = await check_subscriptions(bot, user_id, channels)

    if not all_sub:
        from keyboards.user_kb import channel_check_kb
        not_joined = [ch for ch, ok in zip(channels, results) if not ok]
        await message.answer(
            "🔒 Darsliklarni ko'rish uchun kanallarga a'zo bo'ling:",
            reply_markup=channel_check_kb(not_joined),
        )
        # Always show categories, even if not subscribed, but with a warning
    lang = await db.get_user_language(user_id)
    await _show_course_categories(message.answer, user_id, lang)


# ── Inline callback ────────────────────────────────────────────

@router.callback_query(F.data == "show_courses")
async def show_courses_cb(callback: CallbackQuery, bot: Bot):
    """Handle inline courses button."""
    await callback.answer()
    user_id = callback.from_user.id
    channels = await db.get_active_channels()
    all_sub, results = await check_subscriptions(bot, user_id, channels)

    if not all_sub:
        from keyboards.user_kb import channel_check_kb
        not_joined = [ch for ch, ok in zip(channels, results) if not ok]
        await callback.message.answer(
            "🔒 Darsliklarni ko'rish uchun kanallarga a'zo bo'ling:",
            reply_markup=channel_check_kb(not_joined),
        )
        # Always show categories, even if not subscribed, but with a warning
    lang = await db.get_user_language(user_id)
    await _show_course_categories(callback.message.answer, user_id, lang)


@router.callback_query(F.data == "show_course_cats")
async def show_course_cats_cb(callback: CallbackQuery):
    await callback.answer()
    lang = await db.get_user_language(callback.from_user.id)
    await _show_course_categories(callback.message.edit_text, callback.from_user.id, lang)


@router.callback_query(F.data.startswith("courses_cat_"))
async def courses_cat_selected(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    category = callback.data.replace("courses_cat_", "")
    user_id = callback.from_user.id
    try:
        await _show_courses_list(callback.message.edit_text, user_id, bot, category=category, edit=True)
    except Exception:
        pass


# ── Course forward ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("course_"))
async def send_course(callback: CallbackQuery, bot: Bot):
    """Forward course content from private channel to user."""
    await callback.answer()

    user_id = callback.from_user.id
    user_row = await db.get_user(user_id)
    
    # 1. Check if user is still in DB and registered
    if not user_row or not user_row["is_registered"]:
        await callback.answer("❌ Siz ro'yxatdan o'tmagansiz. Iltimos, /start bosing.", show_alert=True)
        from handlers.start import cmd_start
        # We can't easily call cmd_start without a message, but we can clear state and tell them to press /start
        return

    # 2. Re-check subscriptions before sending content (extra security)
    channels = await db.get_active_channels()
    all_sub, results = await check_subscriptions(bot, user_id, channels)
    if not all_sub:
        from keyboards.user_kb import channel_check_kb
        not_joined = [ch for ch, ok in zip(channels, results) if not ok]
        await callback.message.answer(
            "🔒 Darsliklarni ko'rish uchun kanallarga qayta a'zo bo'ling:",
            reply_markup=channel_check_kb(not_joined),
        )
        return

    course_id = int(callback.data.replace("course_", ""))
    course = await db.get_course(course_id)

    if not course or not course["is_active"]:
        await callback.answer("❌ Bu darslik mavjud emas.", show_alert=True)
        return

    channel_id = COURSES_CHANNEL
    msg_id = course["message_id"]

    logger.info(
        "Darslik yuborilmoqda: course_id=%s, channel=%s, msg_id=%s → user=%s",
        course_id, channel_id, msg_id, callback.from_user.id
    )

    try:
        # Combined caption: bot's title + original channel text
        display_caption = f"📖 <b>{course['title']}</b>"
        if course.get("original_caption"):
            display_caption += f"\n\n{course['original_caption']}"

        await bot.copy_message(
            chat_id=callback.from_user.id,
            from_chat_id=channel_id,
            message_id=msg_id,
            caption=display_caption,
            parse_mode="HTML",
        )

    except TelegramBadRequest as e:
        err_str = str(e)
        if "caption" in err_str.lower():
            # Message has no caption (e.g. video without caption) — try without override
            try:
                await bot.copy_message(
                    chat_id=callback.from_user.id,
                    from_chat_id=channel_id,
                    message_id=msg_id,
                )

            except Exception as e2:
                logger.error("Fallback copy xatosi: %s", e2)
                await callback.message.answer("❌ Darslikni yuborishda xato yuz berdi.")
        else:
            logger.error("Darslik copy xatosi (BadRequest): %s", e)
            await callback.message.answer(
                f"❌ Darslikni yuborishda xato.\nKanal: {channel_id} | Xabar ID: {msg_id}"
            )
    except TelegramForbiddenError:
        await callback.message.answer(
            "❌ Siz botni blokladingiz. Botni yoqib qayta urinib ko'ring."
        )
    except Exception as e:
        logger.error("Darslik kutilmagan xato: %s", e)
        await callback.message.answer(f"❌ Xato: {type(e).__name__}: {e}")

