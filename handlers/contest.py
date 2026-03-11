"""
Contest handler — contest status display.
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

from database import db
from keyboards.user_kb import main_menu_kb, back_kb

logger = logging.getLogger(__name__)
router = Router(name="contest")


@router.callback_query(F.data == "contest_info")
async def contest_info(callback: CallbackQuery, bot: Bot):
    """Show contest information."""
    await callback.answer()

    contest_active_str = await db.get_setting("contest_active") or "1"
    contest_active = contest_active_str == "1"

    total = await db.get_contest_count()
    required_str = await db.get_setting("required_referrals") or "5"

    user_row = await db.get_user(callback.from_user.id)
    is_contestant = user_row["is_contestant"] if user_row else False

    text = (
        f"🏆 <b>KONKURS MA'LUMOTI</b>\n\n"
        f"Holat: {'✅ Faol' if contest_active else '❌ Yakunlangan'}\n"
        f"Jami ishtirokchilar: <b>{total}</b>\n"
        f"Talab: <b>{required_str} ta referal</b>\n\n"
    )

    if is_contestant:
        text += "🎊 Siz allaqachon ishtirokchisiz!"
    else:
        ref_count = user_row["referral_count"] if user_row else 0
        text += (
            f"Sizning holatingiz: {ref_count}/{required_str} ta referal\n"
            f"{'✅' * ref_count}{'⬜️' * max(0, int(required_str) - ref_count)}"
        )

    await callback.message.edit_text(
        text,
        reply_markup=main_menu_kb(is_contestant=bool(is_contestant)),
    )
