"""
Registration handler — multilingual (uz/ru/en).
Simplified flow: btn_register → full_name → phone (contact).
"""

import logging
import re
from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from keyboards.user_kb import phone_kb, main_menu_kb, cancel_kb, remove_kb
from utils.referral_gen import generate_referral_code
from utils.i18n import t, BTN_REGISTER, BTN_CANCEL

logger = logging.getLogger(__name__)
router = Router(name="registration")


class RegState(StatesGroup):
    full_name = State()
    phone     = State()


def is_valid_name(text: str) -> bool:
    return bool(re.match(r"^[A-Za-zА-Яа-яЁёÀ-ÿ'\- ]+$", text.strip()))


async def get_lang(user_id: int) -> str:
    return await db.get_user_language(user_id)


# ── Start registration ─────────────────────────────────────────

@router.message(F.text.in_(BTN_REGISTER))
@router.callback_query(F.data == "start_registration")
@router.callback_query(F.data == "reg_restart")
async def start_registration(update, state: FSMContext):
    if isinstance(update, CallbackQuery):
        await update.answer()
        user_id = update.from_user.id
        send = update.message.answer
    else:
        user_id = update.from_user.id
        send = update.answer

    lang = await get_lang(user_id)

    old_data = await state.get_data()
    referral_code = old_data.get("referral_code")
    
    await state.clear()
    await state.set_state(RegState.full_name)
    
    if referral_code:
        await state.update_data(referral_code=referral_code)
        logger.info(f"Preserving referral_code {referral_code} in FSM for user {user_id}")

    await send(
        t("reg_start", lang),
        reply_markup=cancel_kb(lang),
    )


# ── Step 1: Full name ──────────────────────────────────────────

@router.message(RegState.full_name)
async def process_full_name(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    text = message.text.strip() if message.text else ""

    if text in BTN_CANCEL:
        await state.clear()
        await message.answer(
            t("reg_cancelled", lang),
            reply_markup=main_menu_kb(is_registered=False, lang=lang),
        )
        return

    if len(text) < 3:
        await message.answer(t("reg_name_short", lang))
        return

    if not is_valid_name(text):
        await message.answer(t("reg_name_invalid", lang))
        return

    await state.update_data(full_name=text)
    await state.set_state(RegState.phone)

    # To'g'ridan-to'g'ri telefon so'rash
    await message.answer(
        t("reg_ask_phone", lang),
        reply_markup=phone_kb(lang),
    )


# ── Step 2: Phone via contact ──────────────────────────────────

@router.message(RegState.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext, bot: Bot):
    lang = await get_lang(message.from_user.id)
    phone_raw = message.contact.phone_number
    if not phone_raw.startswith("+"):
        phone_raw = "+" + phone_raw

    if not re.match(r"^\+998[0-9]{9}$", phone_raw):
        await message.answer(t("reg_uz_phone_only", lang), reply_markup=phone_kb(lang))
        return

    phone = phone_raw
    data = await state.get_data()
    full_name = data.get("full_name", "")

    existing = await db.get_user_by_phone(phone)
    if existing and existing["telegram_id"] != message.from_user.id:
        await message.answer(t("reg_phone_taken", lang), reply_markup=remove_kb())
        await state.clear()
        return

    pre_row = await db.get_user(message.from_user.id)
    referred_by = pre_row["referred_by"] if pre_row else None

    if not referred_by:
        ref_code_fsm = data.get("referral_code")
        if ref_code_fsm:
            inviter = await db.get_user_by_referral_code(ref_code_fsm)
            if inviter and inviter["telegram_id"] != message.from_user.id:
                referred_by = inviter["telegram_id"]
                logger.info(f"Referral found via FSM: {referred_by} for {message.from_user.id}")
    else:
        logger.info(f"Referral found via DB: {referred_by} for {message.from_user.id}")

    referral_code = generate_referral_code()
    parts = full_name.split(maxsplit=1)
    first = parts[0]
    last = parts[1] if len(parts) > 1 else ""

    await db.register_user(
        telegram_id=message.from_user.id,
        full_name=first,
        last_name=last,
        age=None,
        profession="",
        phone=phone,
        referral_code=referral_code,
        referred_by=referred_by,
    )

    if referred_by:
        logger.info(f"Attempting to add referral: inviter={referred_by}, invitee={message.from_user.id}")
        added = await db.add_referral(referred_by, message.from_user.id)
        if added:
            inviter_row = await db.get_user(referred_by)
            inviter_lang = await db.get_user_language(referred_by)
            req_str = await db.get_setting("required_referrals") or "5"
            
            # Since add_referral already did +1 in DB, we just take the current value
            new_count = (inviter_row["referral_count"] or 0) if inviter_row else 0
            
            logger.info(f"Referral successfully added. New count for {referred_by} is {new_count}")
            
            if new_count >= int(req_str):
                await db.make_contestant(referred_by)
                contestant_msg = {
                    "uz": "\n🏆 <b>Tabriklaymiz! Siz konkurs ishtirokchisi bo'ldingiz!</b>",
                    "ru": "\n🏆 <b>Поздравляем! Вы стали участником конкурса!</b>",
                    "en": "\n🏆 <b>Congratulations! You became a contest participant!</b>",
                }.get(inviter_lang, "")
            else:
                left = int(req_str) - new_count
                contestant_msg = {
                    "uz": f"\nQoldi: <b>{left} ta</b> do'st",
                    "ru": f"\nОсталось: <b>{left}</b>",
                    "en": f"\nRemaining: <b>{left}</b>",
                }.get(inviter_lang, "")
            try:
                await bot.send_message(
                    referred_by,
                    f"🎉 <b>{full_name}</b> havolangiz orqali ro'yxatdan o'tdi!\n"
                    f"👥 {new_count} ta referal"
                    f"{contestant_msg}",
                )
            except Exception as e:
                logger.warning("Inviter notify error: %s", e)
        else:
            logger.warning(f"Referral failed: already exists or DB error. inviter={referred_by}, invitee={message.from_user.id}")

    fresh = await db.get_user(message.from_user.id)
    is_contestant = bool(fresh["is_contestant"]) if fresh else False
    await state.clear()

    await message.answer(
        f"✅ <b>Ro'yxatdan o'tdingiz!</b>\n\n"
        f"👤 Ism: <b>{full_name}</b>\n"
        f"📱 Raqam: {phone}",
        reply_markup=main_menu_kb(is_registered=True, is_contestant=is_contestant, lang=lang),
    )


@router.message(RegState.phone)
async def process_phone_wrong(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    if message.text and message.text in BTN_CANCEL:
        await state.clear()
        await message.answer(
            t("reg_cancelled", lang),
            reply_markup=main_menu_kb(is_registered=False, lang=lang),
        )
        return
    await message.answer(t("reg_phone_only", lang), reply_markup=phone_kb(lang))
