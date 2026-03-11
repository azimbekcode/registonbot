"""
Referral handler — referral link display and management.
"""

import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

from database import db
from keyboards.user_kb import referral_kb, back_kb

logger = logging.getLogger(__name__)
router = Router(name="referral")


@router.callback_query(F.data == "show_referral")
async def show_referral(callback: CallbackQuery, bot: Bot):
    """Display referral panel."""
    await callback.answer()
    user_row = await db.get_user(callback.from_user.id)
    if not user_row or not user_row["is_registered"]:
        await callback.answer("❌ Avval ro'yxatdan o'ting!", show_alert=True)
        return

    me = await bot.get_me()
    ref_code = user_row["referral_code"] or ""
    ref_link = f"https://t.me/{me.username}?start={ref_code}"

    required_str = await db.get_setting("required_referrals") or "5"
    required = int(required_str)
    ref_count = user_row["referral_count"] or 0

    filled = "✅" * min(ref_count, required)
    empty = "⬜️" * max(0, required - ref_count)

    await callback.message.edit_text(
        f"🔗 <b>REFERAL TIZIMI</b>\n\n"
        f"Konkursda qatnashish uchun {required} ta do'stingizni taklif qiling!\n\n"
        f"Sizning havolangiz:\n"
        f"<code>{ref_link}</code>\n\n"
        f"👥 Do'stlaringiz: {ref_count}/{required} {filled}{empty}\n"
        f"Qoldi: <b>{max(0, required - ref_count)} ta</b>",
        reply_markup=referral_kb(ref_link, ref_count, required),
    )
