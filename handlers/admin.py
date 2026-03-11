"""
Admin panel handler — complete admin functionality.
Sections: users, contestants, channels, courses, stats, settings, admins, broadcast.
"""

import asyncio
import logging
import io
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import config
from utils.i18n import ta
from database import db
from keyboards.admin_kb import (
    admin_main_kb,
    admin_back_kb,
    users_kb,
    user_detail_kb,
    confirm_delete_user_kb,
    channels_kb,
    courses_admin_kb,
    settings_kb,
    admins_kb,
    broadcast_target_kb,
    broadcast_confirm_kb,
    confirm_action_kb,
    db_viewer_main_kb,
    db_viewer_back_kb,
    db_users_page_kb,
    db_users_page_with_delete_kb,
    search_method_kb,
    contest_ids_kb,
    ref_leaderboard_admin_kb,
)


logger = logging.getLogger(__name__)
router = Router(name="admin")


# ── ADMIN STATES ───────────────────────────────────────────────

class AdminState(StatesGroup):
    # Channels
    adding_channel = State()
    # Courses
    adding_course_category = State()
    adding_course_title = State()
    adding_course_desc = State()
    adding_course_forward = State()
    # Settings
    setting_ref_count = State()
    setting_welcome = State()
    setting_invite_text = State()
    setting_contest_rules_text = State()
    setting_dynamic_value = State()
    # Admins
    adding_admin_id = State()
    # Broadcast
    broadcast_message = State()
    # User search
    user_search_query = State()
    user_search_by_phone = State()
    user_search_by_username = State()
    user_search_by_name = State()
    user_search_by_id = State()


# ── ADMIN GUARD ─────────────────────────────────────────────────

async def check_admin(telegram_id: int) -> bool:
    return await db.is_admin(telegram_id, config.superadmin_id)


async def check_superadmin(telegram_id: int) -> bool:
    return await db.is_superadmin(telegram_id, config.superadmin_id)


async def get_lang(user_id: int) -> str:
    return await db.get_user_language(user_id)


# ── /admin COMMAND ─────────────────────────────────────────────

@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return  # Silently ignore
    await state.clear()

    lang = await get_lang(message.from_user.id)
    is_sa = await check_superadmin(message.from_user.id)
    stats = await db.get_stats()
    await message.answer(
        ta("admin_title", lang,
           total=stats["total"], registered=stats["registered"],
           contestants=stats["contestants"], today=stats["today"]),
        reply_markup=admin_main_kb(is_superadmin=is_sa, lang=lang),
    )


@router.callback_query(F.data == "back_to_admin")
async def back_to_admin(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        await callback.answer("❌ Ruxsat yo'q.", show_alert=True)
        return
    await state.clear()
    await callback.answer()
    is_sa = await check_superadmin(callback.from_user.id)
    stats = await db.get_stats()
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        ta("admin_title", lang,
           total=stats["total"], registered=stats["registered"],
           contestants=stats["contestants"], today=stats["today"]),
        reply_markup=admin_main_kb(is_superadmin=is_sa, lang=lang),
    )


# ── USERS SECTION ──────────────────────────────────────────────

@router.callback_query(F.data == "admin_users")
async def admin_users(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    stats = await db.get_stats()
    await callback.message.edit_text(
        f"👥 <b>FOYDALANUVCHILAR</b>\n\n"
        f"Jami ro'yxatdan o'tganlar: <b>{stats['registered']}</b>\n"
        f"Bugun qo'shilganlar: <b>{stats['today']}</b>\n"
        f"Konkurs ishtirokchilari: <b>{stats['contestants']}</b>",
        reply_markup=users_kb(lang=await get_lang(callback.from_user.id)),
    )


@router.callback_query(F.data == "admin_contestants")
async def admin_contestants(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    users = await db.get_all_users(contestants_only=True)
    lang = await get_lang(callback.from_user.id)
    lines = [ta("contestants_list", lang, n=len(users))]
    for u in users:
        name = f"{u['full_name'] or ''} {u['last_name_reg'] or ''}".strip() or "Noma'lum"
        tg = f"@{u['username']}" if u["username"] else str(u["telegram_id"])
        lines.append(f"#{u['id']}. {name} | {tg} | {u['phone'] or '-'}")
    await callback.message.edit_text(
        "\n".join(lines) if len(lines) > 1 else ta("contestants_empty", lang),
        reply_markup=admin_back_kb(lang=lang),
    )


@router.callback_query(F.data == "admin_user_search")
async def admin_user_search(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    await callback.message.edit_text(
        "🔍 <b>QIDIRUV USULINI TANLANG</b>\n\n"
        "Qanday usulda foydalanuvchini qidirmoqchisiz?",
        reply_markup=search_method_kb(lang=await get_lang(callback.from_user.id)),
    )


# ── Qidiruv usuli tanlanganda ─────────────────────────────────

_SEARCH_LABELS = {
    "search_by_phone": ("📱 Telefon raqam", "Telefon raqam kiriting:", AdminState.user_search_by_phone),
    "search_by_username": ("👤 Username", "Username kiriting (@ belgisisiz ham bo'ladi):", AdminState.user_search_by_username),
    "search_by_name": ("🏷️ Ism", "Ismni kiriting:", AdminState.user_search_by_name),
    "search_by_id": ("🆔 Telegram ID", "Telegram ID raqamini kiriting:", AdminState.user_search_by_id),
    "search_by_all": ("🔍 Barchasi", "Telefon, username, ism yoki ID kiriting:", AdminState.user_search_query),
}


@router.callback_query(F.data.startswith("search_by_"))
async def search_method_selected(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    method = callback.data
    if method not in _SEARCH_LABELS:
        return await callback.answer()
    label, prompt, fsm_state = _SEARCH_LABELS[method]
    await state.update_data(search_method=method)
    await state.set_state(fsm_state)
    await callback.answer()
    await callback.message.edit_text(
        f"🔍 <b>QIDIRUV: {label}</b>\n\n"
        f"<i>{prompt}</i>",
    )


async def _do_search(message: Message, state: FSMContext, mode: str):
    """Qidiruv so'rovini bajaradi."""
    await state.clear()
    query = message.text.strip()
    is_sa = await check_superadmin(message.from_user.id)

    if mode == "search_by_phone":
        results = await db.search_users(query)  # phone LIKE
        results = [r for r in results if (r["phone"] or "").startswith(query.lstrip("0").lstrip("+")) or query in (r["phone"] or "")]
        if not results:
            results = await db.search_users(query)
    elif mode == "search_by_username":
        uq = query.lstrip("@")
        results = await db.search_users(uq)
        results = [r for r in results if (r["username"] or "").lower() == uq.lower()
                   or uq.lower() in (r["username"] or "").lower()]
        if not results:
            results = await db.search_users(uq)
    elif mode == "search_by_name":
        results = await db.search_users(query)
        results = [r for r in results if query.lower() in (r["full_name"] or "").lower()
                   or query.lower() in (r["first_name"] or "").lower()]
        if not results:
            results = await db.search_users(query)
    elif mode == "search_by_id":
        try:
            tid = int(query)
            user = await db.get_user(tid)
            results = [user] if user else []
        except ValueError:
            results = []
    else:  # search_by_all
        results = await db.search_users(query)

    if not results:
        await message.answer(
            f"❌ <b>Topilmadi</b>\n\nSo'rov: <code>{query}</code>",
            reply_markup=admin_back_kb()
        )
        return

    if len(results) == 1:
        await show_user_detail(message, results[0], is_superadmin=is_sa)
    else:
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        from aiogram.types import InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        for u in results[:10]:
            unknown = "Noma'lum"
            name = u["full_name"] or u["first_name"] or unknown
            phone = u["phone"] or ""
            builder.row(
                InlineKeyboardButton(
                    text=f"#{u['id']} | {name} | {phone}",
                    callback_data=f"admin_view_user_{u['telegram_id']}",
                )
            )
        builder.row(InlineKeyboardButton(text="🔙 Admin panel", callback_data="back_to_admin"))
        await message.answer(
            f"🔍 Topildi: <b>{len(results)}</b> ta. Birini tanlang:",
            reply_markup=builder.as_markup(),
        )


# ── Har bir state uchun message handler ───────────────────────────

@router.message(AdminState.user_search_by_phone)
async def process_search_phone(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id): return
    await _do_search(message, state, "search_by_phone")


@router.message(AdminState.user_search_by_username)
async def process_search_username(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id): return
    await _do_search(message, state, "search_by_username")


@router.message(AdminState.user_search_by_name)
async def process_search_name(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id): return
    await _do_search(message, state, "search_by_name")


@router.message(AdminState.user_search_by_id)
async def process_search_id(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id): return
    await _do_search(message, state, "search_by_id")



@router.message(AdminState.user_search_query)
async def process_user_search(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return
    await _do_search(message, state, "search_by_all")



async def show_user_detail(message_or_cb, user_row, is_superadmin: bool = False, lang: str = "uz"):
    unknown = "Noma'lum"
    fn = user_row['full_name'] or ''
    ln = user_row['last_name_reg'] or ''
    name = f"{fn} {ln}".strip() or unknown
    tg = f"@{user_row['username']}" if user_row["username"] else "-"
    banned = bool(user_row["is_banned"])
    ph = user_row['phone'] or '-'
    prof = user_row['profession'] or '-'
    joined = str(user_row['joined_at'])[:10] if user_row['joined_at'] else '-'
    reg_at = str(user_row['registered_at'])[:10] if user_row.get('registered_at') else '-'
    refs = user_row['referral_count'] or 0
    ishtirokchi = "Ha ✅" if user_row['is_contestant'] else "Yo'q"
    bloklangan = "Ha 🚫" if banned else "Yo'q"
    text = ta("user_detail", lang,
        index=user_row['id'],
        id=user_row['telegram_id'], name=name, phone=ph, prof=prof,
        uname=tg, joined=joined, reg_at=reg_at,
        contestant=ishtirokchi, refs=refs, banned=bloklangan,
    )
    kb = user_detail_kb(user_row["telegram_id"], banned, is_superadmin=is_superadmin, lang=lang)
    if isinstance(message_or_cb, Message):
        await message_or_cb.answer(text, reply_markup=kb)
    else:
        await message_or_cb.message.edit_text(text, reply_markup=kb)



@router.callback_query(F.data.startswith("admin_view_user_"))
async def admin_view_user(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()
    tid = int(callback.data.replace("admin_view_user_", ""))
    user_row = await db.get_user(tid)
    if not user_row:
        await callback.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)
        return
    is_sa = await check_superadmin(callback.from_user.id)
    lang = await get_lang(callback.from_user.id)
    await show_user_detail(callback, user_row, is_superadmin=is_sa, lang=lang)



@router.callback_query(F.data.startswith("admin_ban_"))
async def admin_ban_user(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    tid = int(callback.data.replace("admin_ban_", ""))
    await db.ban_user(tid, 1)
    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta("user_banned", lang), show_alert=True)
    user_row = await db.get_user(tid)
    if user_row:
        is_sa = await check_superadmin(callback.from_user.id)
        await show_user_detail(callback, user_row, is_superadmin=is_sa, lang=lang)


@router.callback_query(F.data.startswith("admin_unban_"))
async def admin_unban_user(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    tid = int(callback.data.replace("admin_unban_", ""))
    await db.ban_user(tid, 0)
    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta("user_unbanned", lang), show_alert=True)
    user_row = await db.get_user(tid)
    if user_row:
        is_sa = await check_superadmin(callback.from_user.id)
        await show_user_detail(callback, user_row, is_superadmin=is_sa, lang=lang)



@router.callback_query(F.data.startswith("admin_delete_user_"))
async def admin_delete_user_confirm(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()
    tid = int(callback.data.replace("admin_delete_user_", ""))
    user_row = await db.get_user(tid)
    if not user_row:
        lang0 = await get_lang(callback.from_user.id)
        return await callback.answer(ta("user_not_found", lang0), show_alert=True)
    lang = await get_lang(callback.from_user.id)
    fn = user_row["full_name"] or "-"
    ph = user_row["phone"] or "-"
    await callback.message.edit_text(
        ta("delete_confirm", lang, name=fn, phone=ph),
        reply_markup=confirm_delete_user_kb(tid, lang=lang),
    )


@router.callback_query(F.data.startswith("admin_confirm_delete_"))
async def admin_confirm_delete_user(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    tid = int(callback.data.replace("admin_confirm_delete_", ""))
    await db.delete_user(tid)
    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta("user_deleted", lang), show_alert=True)
    await callback.message.edit_text(
        ta("user_deleted", lang) + f"\n🆔 ID: <code>{tid}</code>",
        reply_markup=admin_back_kb(lang=lang),
    )



@router.callback_query(F.data == "admin_export_users")
async def admin_export_users(callback: CallbackQuery, bot: Bot, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer("📥 Fayl tayyorlanmoqda...")
    content = await db.export_users_txt()
    file_bytes = content.encode("utf-8")
    doc = BufferedInputFile(file_bytes, filename="users_export.txt")
    await bot.send_document(callback.from_user.id, document=doc, caption="📋 Foydalanuvchilar ro'yxati (Faqat reg)")


@router.callback_query(F.data == "admin_export_users_all")
async def admin_export_users_all(callback: CallbackQuery, bot: Bot, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer("📥 Fayl tayyorlanmoqda...")
    content = await db.export_users_txt(registered_only=False)
    file_bytes = content.encode("utf-8")
    doc = BufferedInputFile(file_bytes, filename="all_users_export.txt")
    await bot.send_document(callback.from_user.id, document=doc, caption="📋 Barcha foydalanuvchilar ro'yxati")


# ── CHANNELS SECTION ───────────────────────────────────────────

@router.callback_query(F.data == "admin_channels")
async def admin_channels(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    channels = await db.get_all_channels()
    text = "📢 <b>KANALLAR BOSHQARUVI</b>\n\n"
    if not channels:
        text += "Hech qanday kanal yo'q."
    else:
        for ch in channels:
            s = "✅" if ch["is_active"] else "❌"
            text += f"{s} {ch['channel_title'] or ch['channel_id']} — <code>{ch['channel_id']}</code>\n"
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=channels_kb(channels, lang=lang))


@router.callback_query(F.data == "admin_ch_add")
async def admin_ch_add(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()
    await state.set_state(AdminState.adding_channel)
    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(ta("channel_add_prompt", lang))


@router.message(AdminState.adding_channel)
async def process_add_channel(message: Message, state: FSMContext, bot: Bot):
    if not await check_admin(message.from_user.id):
        return
    await state.clear()
    channel_input = message.text.strip()

    # Try to get channel info
    try:
        chat = await bot.get_chat(channel_input)
        channel_id = f"@{chat.username}" if chat.username else str(chat.id)
        title = chat.title or channel_input

        # Check bot can get members (bot must be admin)
        try:
            await bot.get_chat_member(chat.id, message.from_user.id)
        except Exception:
            pass  # Still add, just warn

        await db.add_channel(channel_id, title, message.from_user.id)
        await message.answer(
            f"✅ Kanal qo'shildi: <b>{title}</b> ({channel_id})",
            reply_markup=admin_back_kb(),
        )
    except Exception as e:
        logger.error("Error adding channel: %s", e)
        await message.answer(
            "❌ Kanal topilmadi yoki bot kanalga admin qilinmagan.\n"
            "Botni kanalga admin qilib qayta urinib ko'ring.",
            reply_markup=admin_back_kb(),
        )


@router.callback_query(F.data.startswith("admin_ch_toggle_"))
async def admin_ch_toggle(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    parts = callback.data.replace("admin_ch_toggle_", "").split("_")
    ch_db_id = int(parts[0])
    new_val = int(parts[1])
    await db.toggle_channel(ch_db_id, new_val)
    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta("channel_toggled", lang))
    channels = await db.get_all_channels()
    await callback.message.edit_reply_markup(reply_markup=channels_kb(channels, lang=lang))


@router.callback_query(F.data.startswith("admin_ch_delete_"))
async def admin_ch_delete(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    ch_id = callback.data.replace("admin_ch_delete_", "")
    await db.remove_channel(ch_id)
    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta("channel_deleted", lang))
    channels = await db.get_all_channels()
    await callback.message.edit_reply_markup(reply_markup=channels_kb(channels, lang=lang))


# ── COURSES SECTION ────────────────────────────────────────────

@router.callback_query(F.data == "admin_courses")
async def admin_courses(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    courses = await db.get_all_courses()
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        ta("course_add_title", lang).replace("Darslik nomini kiriting:", "📚 <b>DARSLIKLAR</b>"),
        reply_markup=courses_admin_kb(courses, lang=lang),
    )


@router.callback_query(F.data == "admin_course_add")
async def admin_course_add(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()
    await state.set_state(AdminState.adding_course_category)
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📖 Standart darslik", callback_data="admin_cat_standard"),
        InlineKeyboardButton(text="🔐 Majburiy blok",    callback_data="admin_cat_mandatory"),
    )
    builder.row(InlineKeyboardButton(text="🔙 Bekor qilish", callback_data="admin_courses"))
    await callback.message.edit_text(
        "📂 <b>Kategoriyani tanlang:</b>",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(AdminState.adding_course_category, F.data.startswith("admin_cat_"))
async def process_course_category(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id): return
    cat = callback.data.replace("admin_cat_", "")
    await state.update_data(course_category=cat)
    await state.set_state(AdminState.adding_course_title)
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(ta("course_add_title", lang))


@router.message(AdminState.adding_course_title)
async def process_course_title(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return
    await state.update_data(course_title=message.text.strip())
    await state.set_state(AdminState.adding_course_desc)
    lang = await get_lang(message.from_user.id)
    await message.answer(ta("course_add_desc", lang))


@router.message(AdminState.adding_course_desc)
async def process_course_desc(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return
    desc = message.text.strip()
    if desc == "-":
        desc = ""
    await state.update_data(course_desc=desc)
    await state.set_state(AdminState.adding_course_forward)
    await message.answer(
        f"📤 Endi yopiq kanaldan (<code>{config.courses_channel}</code>) "
        f"darslik xabarini <b>forward</b> qiling:"
    )


@router.message(AdminState.adding_course_forward)
async def process_course_forward(message: Message, state: FSMContext, bot: Bot):
    if not await check_admin(message.from_user.id):
        return

    import re as _re
    # Use config value
    channel_id = config.courses_channel

    # --- Find message ID ---
    msg_id = None

    # Option 1: Forwarded message
    if message.forward_from_message_id:
        msg_id = message.forward_from_message_id

    # Option 2: Link or text ID
    if not msg_id:
        text = (message.text or message.caption or "").strip()
        m = _re.search(r"t\.me/c/\d+/(\d+)", text)
        if m:
            msg_id = int(m.group(1))
        elif _re.fullmatch(r"\d+", text):
            msg_id = int(text)

    if not msg_id:
        await message.answer(
            "❌ Xabar ID aniqlanmadi.\n\n"
            "<b>Qanday qo'shish kerak:</b>\n\n"
            "1️⃣ Kanal xabarini bosing → <b>Havolani nusxalash</b>\n"
            "   Shunday havola olinadi: <code>https://t.me/c/3816800490/47</code>\n"
            "   Shu havolani botga yuboring\n\n"
            "2️⃣ Yoki faqat xabar raqamini yuboring: <code>47</code>"
        )
        return

    # --- Extract file_id: forward message to admin's chat ---
    file_id = None
    file_type = "text"

    try:
        temp_msg = await bot.forward_message(
            chat_id=message.from_user.id,
            from_chat_id=channel_id,
            message_id=msg_id,
        )

        if temp_msg.video:
            file_id = temp_msg.video.file_id
            file_type = "video"
        elif temp_msg.document:
            file_id = temp_msg.document.file_id
            file_type = "document"
        elif temp_msg.photo:
            file_id = temp_msg.photo[-1].file_id
            file_type = "photo"
        elif temp_msg.audio:
            file_id = temp_msg.audio.file_id
            file_type = "audio"
        elif temp_msg.text:
            file_id = ""
            file_type = "text"

        try:
            await bot.delete_message(message.from_user.id, temp_msg.message_id)
        except Exception:
            pass

    except Exception as e:
        await message.answer(
            f"❌ Kanaldan xabar olib bo'lmadi.\n"
            f"ID: <code>{msg_id}</code>\n"
            f"Xato: {e}\n\n"
            "Bot kanalda <b>Admin</b> bo'lishi kerak!"
        )
        return

    data = await state.get_data()
    await state.clear()

    orig_caption = temp_msg.html_text or ""

    await db.add_course(
        title=data.get("course_title", "Nomsiz"),
        description=data.get("course_desc", ""),
        message_id=msg_id,
        file_id=file_id or "",
        file_type=file_type,
        added_by=message.from_user.id,
        category=data.get("course_category", "standard"),
        original_caption=orig_caption,
    )
    await message.answer(
        f"✅ Darslik qo'shildi: <b>{data.get('course_title', 'Nomsiz')}</b>\n"
        f"📁 Tur: {file_type} | 🔢 ID: <code>{msg_id}</code>",
        reply_markup=admin_back_kb(),
    )






@router.callback_query(F.data.startswith("admin_course_toggle_"))
async def admin_course_toggle(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    parts = callback.data.replace("admin_course_toggle_", "").split("_")
    course_id = int(parts[0])
    new_val = int(parts[1])
    await db.toggle_course(course_id, new_val)
    lang = await get_lang(callback.from_user.id)
    await callback.answer("✅")
    courses = await db.get_all_courses()
    await callback.message.edit_reply_markup(reply_markup=courses_admin_kb(courses, lang=lang))


@router.callback_query(F.data.startswith("admin_course_delete_"))
async def admin_course_delete(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    course_id = int(callback.data.replace("admin_course_delete_", ""))
    await db.delete_course(course_id)
    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta("course_deleted", lang))
    courses = await db.get_all_courses()
    await callback.message.edit_reply_markup(reply_markup=courses_admin_kb(courses, lang=lang))


# ── STATISTICS ─────────────────────────────────────────────────

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery, bot: Bot, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    stats = await db.get_stats()

    lang = await get_lang(callback.from_user.id)
    top_lines = []
    for i, r in enumerate(stats["top_referrers"], 1):
        name = r["full_name"] or r["username"] or str(r["telegram_id"])
        top_lines.append(f"  {i}. {name} — {r['referral_count']}")
    top_text = "\n".join(top_lines) if top_lines else "  —"
    pending = stats.get("total", 0) - stats.get("registered", 0)
    banned = stats.get("banned", 0)

    text = (
        ta("admin_stats", lang,
           total=stats["total"], registered=stats["registered"],
           contestants=stats["contestants"], pending=pending,
           banned=banned, today=stats["today"])
        + f"\n\n🔗 Top referrers:\n{top_text}"
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder as _IKB
    from aiogram.types import InlineKeyboardButton as _IKBBtn
    _builder = _IKB()
    _builder.row(_IKBBtn(text=ta("btn_full_report", lang), callback_data="admin_export_users"))
    _builder.row(_IKBBtn(text=ta("btn_back_admin", lang), callback_data="back_to_admin"))
    await callback.message.edit_text(text, reply_markup=_builder.as_markup())


# ── SETTINGS ───────────────────────────────────────────────────

@router.callback_query(F.data == "admin_settings")
async def admin_settings(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    settings = await db.get_all_settings()
    lang = await get_lang(callback.from_user.id)
    try:
        await callback.message.edit_text(
            ta("btn_bot_settings", lang),
            reply_markup=settings_kb(settings, lang=lang),
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin_set_contest_"))
async def admin_set_contest(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    val = callback.data.replace("admin_set_contest_", "")
    await db.set_setting("contest_active", val, callback.from_user.id)
    status = "yoqildi ✅" if val == "1" else "o'chirildi ❌"
    await callback.answer(f"Konkurs {status}.")
    lang = await get_lang(callback.from_user.id)
    settings = await db.get_all_settings()
    await callback.message.edit_reply_markup(reply_markup=settings_kb(settings, lang=lang))


@router.callback_query(F.data.startswith("admin_set_reg_"))
async def admin_set_reg(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    val = callback.data.replace("admin_set_reg_", "")
    await db.set_setting("registration_open", val, callback.from_user.id)
    status = "ochildi ✅" if val == "1" else "yopildi ❌"
    await callback.answer(f"Ro'yxat {status}.")
    lang = await get_lang(callback.from_user.id)
    settings = await db.get_all_settings()
    await callback.message.edit_reply_markup(reply_markup=settings_kb(settings, lang=lang))


@router.callback_query(F.data == "admin_set_ref_count")
async def admin_set_ref_count(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()
    await state.set_state(AdminState.setting_ref_count)
    current = await db.get_setting("required_referrals") or "5"
    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(ta("set_ref_prompt", lang) + f"\nHozirgi: <b>{current}</b>")


@router.message(AdminState.setting_ref_count)
async def process_ref_count(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return
    try:
        val = int(message.text.strip())
        if not (1 <= val <= 100):
            raise ValueError
    except ValueError:
        await message.answer("❌ 1 dan 100 gacha raqam kiriting:")
        return
    await state.clear()
    await db.set_setting("required_referrals", str(val), message.from_user.id)
    lang = await get_lang(message.from_user.id)
    await message.answer(ta("set_ref_done", lang, n=val), reply_markup=admin_back_kb(lang=lang))


@router.callback_query(F.data == "admin_set_welcome")
async def admin_set_welcome(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()
    await state.set_state(AdminState.setting_welcome)
    current = await db.get_setting("welcome_message") or ""
    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(
        ta("set_welcome_prompt", lang) + f"\n\n<i>{current}</i>"
    )


@router.message(AdminState.setting_welcome)
async def process_welcome_msg(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return
    await state.clear()
    await db.set_setting("welcome_message", message.text.strip(), message.from_user.id)
    lang = await get_lang(message.from_user.id)
    await message.answer(ta("set_welcome_done", lang), reply_markup=admin_back_kb(lang=lang))


@router.callback_query(F.data.startswith("admin_set_std_lessons_"))
async def admin_set_std_lessons(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id): return
    val = callback.data.replace("admin_set_std_lessons_", "")
    await db.set_setting("standard_lessons_active", val, callback.from_user.id)
    await callback.answer("✅ Yangilandi")
    settings = await db.get_all_settings()
    lang = await get_lang(callback.from_user.id)
    from keyboards.admin_kb import settings_kb
    await callback.message.edit_reply_markup(reply_markup=settings_kb(settings, lang))


@router.callback_query(F.data.startswith("admin_set_man_lessons_"))
async def admin_set_man_lessons(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id): return
    val = callback.data.replace("admin_set_man_lessons_", "")
    await db.set_setting("mandatory_lessons_active", val, callback.from_user.id)
    await callback.answer("✅ Yangilandi")
    settings = await db.get_all_settings()
    lang = await get_lang(callback.from_user.id)
    from keyboards.admin_kb import settings_kb
    await callback.message.edit_reply_markup(reply_markup=settings_kb(settings, lang))


# ── DO'ST TAKLIF QILISH matni tahrirlash ──────────────────────

@router.callback_query(F.data == "admin_set_invite_text")
async def admin_set_invite_text(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()
    await state.set_state(AdminState.setting_invite_text)
    current = await db.get_setting("invite_text") or ""
    await callback.message.answer(
        "✉️ <b>DO'ST TAKLIF QILISH matni tahrirlash</b>\n\n"
        "Yangi matnni kiriting (HTML teglari qo'llab-quvvatlanadi: <b>, <i>, <code>):\n\n"
        f"<b>Hozirgi matn:</b>\n<i>{current or 'Standart'}</i>"
    )


@router.message(AdminState.setting_invite_text)
async def process_invite_text(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return
    await state.clear()
    await db.set_setting("invite_text", message.text.strip(), message.from_user.id)
    lang = await get_lang(message.from_user.id)
    await message.answer("✅ Do'st taklif qilish matni yangilandi.", reply_markup=admin_back_kb(lang=lang))


# ── TANLOV SHARTLARI matni tahrirlash ─────────────────────────

@router.callback_query(F.data == "admin_set_contest_rules_text")
async def admin_set_contest_rules_text(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()
    await state.set_state(AdminState.setting_contest_rules_text)
    current = await db.get_setting("contest_rules_text") or ""
    await callback.message.answer(
        "📋 <b>TANLOV SHARTLARI matni tahrirlash</b>\n\n"
        "Yangi matnni kiriting (HTML teglari qo'llab-quvvatlanadi: <b>, <i>, <code>):\n\n"
        f"<b>Hozirgi matn:</b>\n<i>{current or 'Standart'}</i>"
    )


@router.message(AdminState.setting_contest_rules_text)
async def process_contest_rules_text(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return
    await state.clear()
    await db.set_setting("contest_rules_text", message.text.strip(), message.from_user.id)
    lang = await get_lang(message.from_user.id)
    await message.answer("✅ Tanlov shartlari matni yangilandi.", reply_markup=admin_back_kb(lang=lang))


# ── ADMINS SECTION (SUPERADMIN ONLY) ──────────────────────────

@router.callback_query(F.data == "admin_admins")
async def admin_admins(callback: CallbackQuery, state: FSMContext):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("❌ Faqat superadmin uchun.", show_alert=True)
    await state.clear()
    await callback.answer()
    admins = await db.get_all_admins()
    lang = await get_lang(callback.from_user.id)
    text = f"👮 <b>ADMINLAR ({len(admins)} ta)</b>"
    await callback.message.edit_text(
        text,
        reply_markup=admins_kb(admins, config.superadmin_id, lang=lang),
    )


@router.callback_query(F.data == "admin_adm_add")
async def admin_adm_add(callback: CallbackQuery, state: FSMContext):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("❌ Faqat superadmin uchun.", show_alert=True)
    await callback.answer()
    await state.set_state(AdminState.adding_admin_id)
    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(ta("admin_add_prompt", lang))


@router.message(AdminState.adding_admin_id)
async def process_add_admin(message: Message, state: FSMContext, bot: Bot):
    if not await check_superadmin(message.from_user.id):
        return
    await state.clear()
    try:
        new_admin_id = int(message.text.strip())
    except ValueError:
        await message.answer("❌ Noto'g'ri ID. Raqam kiriting.", reply_markup=admin_back_kb())
        return

    # Check not already admin
    existing = await db.get_admin(new_admin_id)
    if existing:
        await message.answer("⚠️ Bu foydalanuvchi allaqachon admin.", reply_markup=admin_back_kb())
        return

    # Try to get user info
    try:
        member = await bot.get_chat(new_admin_id)
        username = getattr(member, "username", None)
        full_name = getattr(member, "full_name", None)
    except Exception:
        username = None
        full_name = None

    await db.add_admin(new_admin_id, username, full_name, message.from_user.id)
    lang = await get_lang(message.from_user.id)
    await message.answer(
        ta("admin_added", lang) + f" <code>{new_admin_id}</code>",
        reply_markup=admin_back_kb(lang=lang),
    )

    # Notify new admin
    try:
        await bot.send_message(
            new_admin_id,
            "👮 Siz Registon O'quv Markaz botida admin qildingiz!\n\n/admin buyrug'ini bering.",
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admin_adm_remove_"))
async def admin_adm_remove(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("❌ Faqat superadmin uchun.", show_alert=True)
    tid = int(callback.data.replace("admin_adm_remove_", ""))
    if tid == config.superadmin_id:
        await callback.answer("❌ Superadminni o'chirib bo'lmaydi!", show_alert=True)
        return
    if tid == callback.from_user.id:
        await callback.answer("❌ O'zingizni o'chirib bo'lmaydi!", show_alert=True)
        return
    await db.remove_admin(tid)
    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta("admin_removed", lang))
    admins = await db.get_all_admins()
    await callback.message.edit_reply_markup(
        reply_markup=admins_kb(admins, config.superadmin_id, lang=lang)
    )


# ── BROADCAST ──────────────────────────────────────────────────

@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        ta("broadcast_write", lang),
        reply_markup=broadcast_target_kb(lang=lang),
    )


@router.callback_query(F.data.startswith("broadcast_") & ~F.data.startswith("broadcast_confirm_"))
async def broadcast_target_selected(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)

    target = callback.data.replace("broadcast_", "")
    if target == "all":
        users = await db.get_all_users()
    elif target == "registered":
        users = await db.get_all_users(registered_only=True)
    elif target == "contestants":
        users = await db.get_all_users(contestants_only=True)
    elif target == "unregistered":
        users = await db.get_all_users(unregistered_only=True)
    else:
        return

    await state.update_data(broadcast_target=target, broadcast_count=len(users))
    await state.set_state(AdminState.broadcast_message)
    await callback.answer()
    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(ta("broadcast_write", lang) + f"\n\n({len(users)} ta)")


@router.message(AdminState.broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id):
        return

    data = await state.get_data()
    target = data.get("broadcast_target", "all")
    count = data.get("broadcast_count", 0)

    # Store message_id for later use
    await state.update_data(broadcast_msg_id=message.message_id, broadcast_chat_id=message.chat.id)

    label_map = {
        "all": "Hammaga",
        "registered": "Ro'yxatdagilarga",
        "contestants": "Ishtirokchilarga",
        "unregistered": "Ro'yxatdan o'tmaganlarga",
    }

    lang = await get_lang(message.from_user.id)
    await message.answer(
        ta("broadcast_preview", lang) + f"\n\n({count} ta)",
        reply_markup=broadcast_confirm_kb(target, count, lang=lang),
    )


@router.callback_query(F.data.startswith("broadcast_confirm_"))
async def broadcast_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()

    data = await state.get_data()
    target = callback.data.replace("broadcast_confirm_", "")
    await state.clear()

    if target == "all":
        users = await db.get_all_users()
    elif target == "registered":
        users = await db.get_all_users(registered_only=True)
    elif target == "contestants":
        users = await db.get_all_users(contestants_only=True)
    elif target == "unregistered":
        users = await db.get_all_users(unregistered_only=True)
    else:
        users = []

    src_chat_id = data.get("broadcast_chat_id")
    src_msg_id = data.get("broadcast_msg_id")

    if not src_chat_id or not src_msg_id:
        await callback.message.answer("❌ Xabar topilmadi.", reply_markup=admin_back_kb())
        return

    await callback.message.edit_text(
        f"📤 Yuborish boshlandi... ({len(users)} kishi)"
    )

    sent = 0
    failed = 0
    batch_size = 25

    for i, user in enumerate(users):
        try:
            await bot.copy_message(
                chat_id=user["telegram_id"],
                from_chat_id=src_chat_id,
                message_id=src_msg_id,
            )
            sent += 1
        except Exception:
            failed += 1

        # Rate limiting
        if (i + 1) % batch_size == 0:
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(0.05)

    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(
        ta("broadcast_done", lang, ok=sent, fail=failed),
        reply_markup=admin_back_kb(lang=lang),
    )


# -- DATABASE VIEWER (SUPERADMIN ONLY) --------------------------

PAGE_SIZE = 5  # Bir sahifada ko'rsatiladigan userlar soni


@router.callback_query(F.data == "sa_db_viewer")
async def sa_db_viewer(callback: CallbackQuery, state: FSMContext):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await state.clear()
    await callback.answer()

    counts = await db.db_get_table_counts()
    c_u = counts["users"]
    c_ad = counts["admins"]
    c_ch = counts["channels"]
    c_co = counts["courses"]
    c_r = counts["referrals"]
    c_cp = counts["contest_participants"]
    c_bs = counts["bot_settings"]
    text = (
        "<b>DATABASE KO'RISH MENYUSI</b>\n\n"
        f"users: <b>{c_u}</b> ta yozuv\n"
        f"admins: <b>{c_ad}</b> ta yozuv\n"
        f"channels: <b>{c_ch}</b> ta yozuv\n"
        f"courses: <b>{c_co}</b> ta yozuv\n"
        f"referrals: <b>{c_r}</b> ta yozuv\n"
        f"contest_participants: <b>{c_cp}</b> ta yozuv\n"
        f"bot_settings: <b>{c_bs}</b> ta yozuv\n\n"
        "Ko'rmoqchi bo'lgan jadvalni tanlang:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=db_viewer_main_kb())
    except Exception:
        await callback.message.answer(text, reply_markup=db_viewer_main_kb())


# -- USERS JADVALI (sahifalash bilan) ---------------------------

async def _show_users_page(callback: CallbackQuery, page: int):
    users = await db.db_get_all_users_full()
    total = len(users)
    if total == 0:
        await callback.message.edit_text(
            "<b>USERS JADVALI</b>\n\nHech qanday yozuv yo'q.",
            reply_markup=db_viewer_back_kb(),
        )
        return

    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    page = max(0, min(page, total_pages - 1))
    start = page * PAGE_SIZE
    chunk = users[start: start + PAGE_SIZE]

    lines = [f"<b>USERS JADVALI</b> ({total} ta) - Sahifa {page + 1}/{total_pages}\n"]
    user_ids = []
    for u in chunk:
        fn = u["full_name"] or ""
        ln = u["last_name_reg"] or ""
        name = (fn + " " + ln).strip() or "Noma'lum"
        reg = "Reg:HA" if u["is_registered"] else "Reg:YOQ"
        ban = " BAN" if u["is_banned"] else ""
        joined = str(u["joined_at"])[:10]
        uname = u["username"] or "-"
        phone = u["phone"] or "-"
        tid = u["telegram_id"]
        user_ids.append(tid)
        lines.append(
            f"#{u['id']}. <b>{name}</b>{ban}\n"
            f"  ID: <code>{tid}</code> | @{uname}\n"
            f"  Tel: {phone} | {reg} | {joined}"
        )

    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=db_users_page_with_delete_kb(page, total_pages, user_ids, lang=lang),
    )


@router.callback_query(F.data == "sa_db_users")
async def sa_db_users(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await callback.answer()
    await _show_users_page(callback, 0)


@router.callback_query(F.data.startswith("sa_db_users_p_"))
async def sa_db_users_page(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await callback.answer()
    page = int(callback.data.replace("sa_db_users_p_", ""))
    await _show_users_page(callback, page)


@router.callback_query(F.data.startswith("sa_del_user_"))
async def sa_delete_user(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    tid = int(callback.data.replace("sa_del_user_", ""))
    user_row = await db.get_user(tid)
    if not user_row:
        await callback.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)
        return
    fn = user_row["full_name"] or "-"
    await db.delete_user(tid)
    await callback.answer(f"✅ {fn} o'chirildi.", show_alert=True)
    # Sahifani yangilash
    await _show_users_page(callback, 0)


# -- ADMINS JADVALI ----------------------------------------------

@router.callback_query(F.data == "sa_db_admins")
async def sa_db_admins(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await callback.answer()

    admins = await db.get_all_admins()
    unknown = "Noma'lum"
    lines = [f"<b>ADMINS JADVALI</b> ({len(admins)} ta)\n"]
    for i, a in enumerate(admins, 1):
        role = a["role"]
        role_emoji = "SUPERADMIN" if role == "superadmin" else "ADMIN"
        active_s = "HA" if a["is_active"] else "YOQ"
        aname = a["full_name"] or unknown
        auser = a["username"] or "-"
        atid = a["telegram_id"]
        added = str(a["added_at"])[:10]
        lines.append(
            f"{i}. [{role_emoji}] <b>{aname}</b>\n"
            f"   @{auser} | ID: <code>{atid}</code>\n"
            f"   Rol: {role} | Faol: {active_s} | {added}"
        )

    await callback.message.edit_text(
        "\n".join(lines) if len(lines) > 1 else "Adminlar yo'q.",
        reply_markup=db_viewer_back_kb(),
    )


# -- CHANNELS JADVALI --------------------------------------------

@router.callback_query(F.data == "sa_db_channels")
async def sa_db_channels(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await callback.answer()

    channels = await db.get_all_channels()
    lines = [f"<b>CHANNELS JADVALI</b> ({len(channels)} ta)\n"]
    for i, c in enumerate(channels, 1):
        st = "FAOL" if c["is_active"] else "OCHIQ-EMAS"
        ctitle = c["channel_title"] or "-"
        cid = c["channel_id"]
        cadded = str(c["added_at"])[:10]
        lines.append(
            f"{i}. [{st}] <b>{ctitle}</b>\n"
            f"   ID: <code>{cid}</code>\n"
            f"   Qo'shildi: {cadded}"
        )

    await callback.message.edit_text(
        "\n".join(lines) if len(lines) > 1 else "Kanallar yo'q.",
        reply_markup=db_viewer_back_kb(),
    )


# -- COURSES JADVALI ---------------------------------------------

@router.callback_query(F.data == "sa_db_courses")
async def sa_db_courses(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await callback.answer()

    courses = await db.get_all_courses()
    lines = [f"<b>COURSES JADVALI</b> ({len(courses)} ta)\n"]
    for i, c in enumerate(courses, 1):
        st = "FAOL" if c["is_active"] else "OCHIQ-EMAS"
        ctitle = c["title"]
        ctype = c["file_type"]
        cmid = c["message_id"]
        cdesc = (c["description"] or "-")[:40]
        cadded = str(c["added_at"])[:10]
        lines.append(
            f"{i}. [{st}] <b>{ctitle}</b>\n"
            f"   Tur: {ctype} | msg_id: <code>{cmid}</code>\n"
            f"   Tavsif: {cdesc}\n"
            f"   Qo'shildi: {cadded}"
        )

    await callback.message.edit_text(
        "\n".join(lines) if len(lines) > 1 else "Darsliklar yo'q.",
        reply_markup=db_viewer_back_kb(),
    )


# -- REFERRALS JADVALI -------------------------------------------

@router.callback_query(F.data == "sa_db_referrals")
async def sa_db_referrals(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await callback.answer()

    referrals = await db.db_get_all_referrals()
    total = len(referrals)
    lines = [f"<b>REFERRALS JADVALI</b> ({total} ta)\n"]
    for i, r in enumerate(referrals[:30], 1):
        inviter = r["inviter_name"] or str(r["inviter_id"])
        invitee = r["invitee_name"] or str(r["invitee_id"])
        iuser = ""
        if r.get("inviter_username"):
            iuser = " @" + r["inviter_username"]
        rdate = str(r["joined_at"])[:10]
        lines.append(
            f"{i}. {inviter}{iuser} => {invitee}\n"
            f"   Sana: {rdate}"
        )

    if total > 30:
        lines.append(f"\n... va yana {total - 30} ta (hisobotda to'liq ko'ring)")

    await callback.message.edit_text(
        "\n".join(lines) if len(lines) > 1 else "Referrallar yo'q.",
        reply_markup=db_viewer_back_kb(),
    )


# -- CONTEST PARTICIPANTS ----------------------------------------

@router.callback_query(F.data == "sa_db_contest")
async def sa_db_contest(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await callback.answer()

    participants = await db.db_get_all_contest_participants()
    lines = [f"<b>CONTEST PARTICIPANTS</b> ({len(participants)} ta)\n"]
    for i, p in enumerate(participants, 1):
        pname = p["full_name"] or "Noma'lum"
        puser = p["username"] or "-"
        ptid = p["telegram_id"]
        pphone = p["phone"] or "-"
        pref = p["referral_count"]
        pjoined = str(p["joined_contest_at"])[:10]
        lines.append(
            f"{i}. <b>{pname}</b>\n"
            f"   @{puser} | ID: <code>{ptid}</code>\n"
            f"   Tel: {pphone} | Ref:{pref}\n"
            f"   Qo'shildi: {pjoined}"
        )

    await callback.message.edit_text(
        "\n".join(lines) if len(lines) > 1 else "Hali ishtirokchilar yo'q.",
        reply_markup=db_viewer_back_kb(),
    )


# -- BOT SETTINGS JADVALI ----------------------------------------

@router.callback_query(F.data == "sa_db_settings")
async def sa_db_settings_view(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await callback.answer()

    settings = await db.get_all_settings()
    lines = [f"<b>BOT SETTINGS JADVALI</b> ({len(settings)} ta)\n"]
    for key, value in settings.items():
        lines.append(f"<b>{key}</b>: <code>{value}</code>")

    await callback.message.edit_text(
        "\n".join(lines) if len(lines) > 1 else "Sozlamalar yo'q.",
        reply_markup=db_viewer_back_kb(),
    )


# -- TO'LIQ HISOBOT EXPORT ---------------------------------------

@router.callback_query(F.data == "sa_db_export_full")
async def sa_db_export_full(callback: CallbackQuery, bot: Bot):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
    await callback.answer("To'liq hisobot tayyorlanmoqda...", show_alert=False)

    content = await db.db_export_full_report()
    file_bytes = content.encode("utf-8")
    doc = BufferedInputFile(file_bytes, filename="database_full_report.txt")
    await bot.send_document(
        callback.from_user.id,
        document=doc,
        caption="<b>To''liq Database Hisoboti</b>\nBarcha jadvallar: users, admins, channels, courses, referrals, contest, settings",
    )


# -- NOOP --------------------------------------------------------

@router.callback_query(F.data == "noop")
async def noop(callback: CallbackQuery):
    await callback.answer()


# ── BARCHA FOYDALANUVCHILAR (sahifalash) ───────────────────────────────────

ALL_USERS_PAGE_SIZE = 8


async def _show_all_users_page(callback: CallbackQuery, page: int):
    users = await db.get_all_users()
    total = len(users)
    if total == 0:
        lang = await get_lang(callback.from_user.id)
        await callback.message.edit_text(
            "👥 <b>Barcha foydalanuvchilar</b>\n\nHech qanday foydalanuvchi yo'q.",
            reply_markup=admin_back_kb(lang=lang),
        )
        return

    total_pages = (total + ALL_USERS_PAGE_SIZE - 1) // ALL_USERS_PAGE_SIZE
    page = max(0, min(page, total_pages - 1))
    start = page * ALL_USERS_PAGE_SIZE
    chunk = users[start: start + ALL_USERS_PAGE_SIZE]

    lines = [f"👥 <b>BARCHA FOYDALANUVCHILAR</b> ({total} ta) — Sahifa {page + 1}/{total_pages}\n"]
    for u in chunk:
        fn = u["full_name"] or ""
        ln = u["last_name_reg"] or ""
        name = (fn + " " + ln).strip() or u["first_name"] or "Noma'lum"
        reg = "✅ Reg" if u["is_registered"] else "❌ Reg"
        ban = " | 🚫 BAN" if u["is_banned"] else ""
        phone = u["phone"] or "-"
        uname = f"@{u['username']}" if u["username"] else "-"
        refs = u["referral_count"] or 0
        joined = str(u["joined_at"])[:10]
        lines.append(
            f"#{u['id']}. <b>{name}</b>{ban}\n"
            f"   🔑 <code>{u['telegram_id']}</code> | {uname}\n"
            f"   📱 {phone} | {reg} | 🔗 {refs} ref | {joined}"
        )

    # Sahifalash tugmalari
    from aiogram.utils.keyboard import InlineKeyboardBuilder as _IKB
    from aiogram.types import InlineKeyboardButton as _IKBBtn
    _b = _IKB()
    nav = []
    if page > 0:
        nav.append(_IKBBtn(text="← Oldingi", callback_data=f"admin_all_users_{page - 1}"))
    nav.append(_IKBBtn(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(_IKBBtn(text="Keyingi →", callback_data=f"admin_all_users_{page + 1}"))
    if nav:
        _b.row(*nav)
    _b.row(_IKBBtn(text="📥 Ro'yxatni yuklab olish (Faqat reg)", callback_data="admin_export_users"))
    _b.row(_IKBBtn(text="📥 To'liq bazani yuklab olish", callback_data="admin_export_users_all"))
    _b.row(_IKBBtn(text="🔙 Foydalanuvchilar menyusi", callback_data="admin_users"))
    _b.row(_IKBBtn(text="🔙 Admin panel", callback_data="back_to_admin"))

    await callback.message.edit_text("\n".join(lines), reply_markup=_b.as_markup())


@router.callback_query(F.data.startswith("admin_all_users_"))
async def admin_all_users(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()
    page_str = callback.data.replace("admin_all_users_", "")
    try:
        page = int(page_str)
    except ValueError:
        page = 0
    await _show_all_users_page(callback, page)


@router.callback_query(F.data == "admin_contest_ids")
async def admin_contest_ids(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    participants = await db.get_contest_participants_ids()
    lang = await get_lang(callback.from_user.id)
    total = len(participants)

    if not participants:
        await callback.message.edit_text(
            "🏆 <b>KONKURS ISHTIROKCHILARI</b>\n\nHali hech kim yo'q.",
            reply_markup=contest_ids_kb(lang=lang),
        )
        return

    # Sahifalar bo'yicha ko'rsatish (30 kishi)
    lines = [f"🏆 <b>KONKURS ISHTIROKCHILARI IDlari</b> ({total} ta)\n"]
    for p in participants[:50]:
        fn = p["full_name"] or ""
        ln = p["last_name_reg"] or ""
        name = f"{fn} {ln}".strip() or "Noma'lum"
        uname = f"@{p['username']}" if p["username"] else "-"
        lines.append(
            f"#{p['id']}. <code>{p['telegram_id']}</code> | {name} | {uname} | Ref:{p['referral_count']}"
        )
    if total > 50:
        lines.append(f"\n... va yana {total - 50} ta (IDlar faylida ko'ring)")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=contest_ids_kb(lang=lang),
    )


@router.callback_query(F.data == "admin_export_contest_ids")
async def admin_export_contest_ids(callback: CallbackQuery, bot: Bot):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer("📥 Fayl tayyorlanmoqda...", show_alert=False)

    participants = await db.get_contest_participants_ids()
    if not participants:
        await bot.send_message(callback.from_user.id, "❌ Ishtirokchilar yo'q.")
        return

    lines = ["KONKURS ISHTIROKCHILARI — Telegram IDlar ro'yxati", "=" * 50, ""]
    lines.append(f"Jami: {len(participants)} ta ishtirokchi")
    lines.append("=" * 50)
    lines.append("")
    for i, p in enumerate(participants, 1):
        fn = p["full_name"] or ""
        ln = p["last_name_reg"] or ""
        name = f"{fn} {ln}".strip() or "Noma'lum"
        uname = f"@{p['username']}" if p["username"] else "-"
        joined = str(p["joined_contest_at"])[:10] if p["joined_contest_at"] else "-"
        lines.append(
            f"{i}. ID: {p['telegram_id']} | {name} | {uname} | "
            f"Ref: {p['referral_count']} | Qo'shildi: {joined}"
        )
    lines.append("")
    lines.append("=" * 50)
    lines.append("Faqat IDlar (copy-paste uchun):")
    for p in participants:
        lines.append(str(p["telegram_id"]))

    content = "\n".join(lines)
    file_bytes = content.encode("utf-8")
    from aiogram.types import BufferedInputFile
    doc = BufferedInputFile(file_bytes, filename="contest_participants_ids.txt")
    await bot.send_document(
        callback.from_user.id,
        document=doc,
        caption=f"🏆 Konkurs ishtirokchilari: <b>{len(participants)}</b> ta\nFaylda barcha IDlar mavjud.",
    )


@router.callback_query(F.data == "admin_pick_winner")
async def admin_pick_winner(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer("🎲 Random tanlanmoqda...", show_alert=False)

    winner = await db.pick_random_contestant()
    lang = await get_lang(callback.from_user.id)

    if not winner:
        await callback.message.answer(
            "❌ Ishtirokchilar yo'q. Hali hech kim konkursda qatnashmoqchi emas.",
            reply_markup=admin_back_kb(lang=lang),
        )
        return

    fn = winner["full_name"] or ""
    ln = winner["last_name_reg"] or ""
    name = f"{fn} {ln}".strip() or "Noma'lum"
    uname = f"@{winner['username']}" if winner["username"] else "-"
    ph = winner["phone"] or "-"
    refs = winner["referral_count"] or 0
    joined = str(winner["joined_contest_at"])[:10] if winner["joined_contest_at"] else "-"

    await callback.message.answer(
        f"🎉 <b>RANDOM G'OLIB ANIQLANDI!</b>\n\n"
        f"🏆 <b>{name}</b>\n"
        f"🔑 Telegram ID: <code>{winner['telegram_id']}</code>\n"
        f"👤 Username: {uname}\n"
        f"📱 Telefon: {ph}\n"
        f"🔗 Referallar: {refs} ta\n"
        f"📅 Konkursga qo'shildi: {joined}\n\n"
        f"✅ Bu natija <b>tasodifiy</b> tarzda aniqlandi.",
        reply_markup=admin_back_kb(lang=lang),
    )


# ── REFERRAL REYTINGI (Admin/Superadmin) ──────────────────────────────

@router.callback_query(F.data == "admin_ref_leaderboard")
async def admin_ref_leaderboard(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await state.clear()
    await callback.answer()
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        "📊 <b>REFERRAL REYTINGI</b>\n\nNechta foydalanuvchini ko'rmoqchisiz?",
        reply_markup=ref_leaderboard_admin_kb(lang=lang),
    )


@router.callback_query(F.data.startswith("admin_ref_lb_"))
async def admin_ref_lb_show(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id):
        return await callback.answer(ta("no_access", "uz"), show_alert=True)
    await callback.answer()

    limit = int(callback.data.replace("admin_ref_lb_", ""))
    users = await db.get_referral_leaderboard(limit=limit)
    lang = await get_lang(callback.from_user.id)

    if not users:
        await callback.message.edit_text(
            "📊 <b>Referral reytingi</b>\n\nHali hech kim referal yig'magan.",
            reply_markup=admin_back_kb(lang=lang),
        )
        return

    lines = [f"📊 <b>REFERRAL REYTINGI — Top {limit}</b>\n"]
    for i, u in enumerate(users, 1):
        fn = u["full_name"] or ""
        ln = u["last_name_reg"] or ""
        name = f"{fn} {ln}".strip() or u["username"] or "Noma'lum"
        uname = f" (@{u['username']})" if u["username"] else ""
        lines.append(f"{i}. {name}{uname} | <code>{u['telegram_id']}</code> — <b>{u['referral_count']}</b> ta")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=ref_leaderboard_admin_kb(lang=lang),
    )


# ── INTERFACE SETTINGS ───────────────────────────────────────

@router.callback_query(F.data == "admin_interface_settings")
async def admin_interface_settings(callback: CallbackQuery):
    if not await check_admin(callback.from_user.id): return
    await callback.answer()
    from keyboards.admin_kb import interface_settings_kb
    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        "🎨 <b>Tugma va matnlar sozlamalari</b>\n\n"
        "Ushbu bo'limda bot menyusidagi tugma nomlarini va asosiy matnlarni o'zgartirishingiz mumkin.",
        reply_markup=interface_settings_kb(lang=lang)
    )

@router.callback_query(F.data.startswith("admin_set_lb_"))
async def admin_set_label_start(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id): return
    await callback.answer()
    key_map = {
        "courses": "label_btn_courses",
        "profile": "label_btn_profile",
        "invite": "label_btn_invite",
        "rules": "label_btn_contest_rules",
        "results": "label_btn_results",
        "mandatory": "label_btn_mandatory",
        "standard": "label_btn_standard",
    }
    short_key = callback.data.replace("admin_set_lb_", "")
    db_key = key_map.get(short_key)
    if not db_key: return
    
    await state.update_data(dy_key=db_key)
    await state.set_state(AdminState.setting_dynamic_value)
    current = await db.get_setting(db_key)
    await callback.message.answer(f"📝 Tugma uchun yangi nom kiriting:\n\nHozirgi: <b>{current}</b>")

@router.callback_query(F.data.startswith("admin_set_txt_"))
async def admin_set_text_start(callback: CallbackQuery, state: FSMContext):
    if not await check_admin(callback.from_user.id): return
    await callback.answer()
    key_map = {
        "profile": "text_profile",
        "results": "text_results_main",
        "courses_main": "text_courses_main",
        "courses_std": "text_courses_standard",
        "courses_man": "text_courses_mandatory",
        "invite": "invite_text",
        "rules": "contest_rules_text",
    }
    short_key = callback.data.replace("admin_set_txt_", "")
    db_key = key_map.get(short_key)
    if not db_key: return
    
    await state.update_data(dy_key=db_key)
    await state.set_state(AdminState.setting_dynamic_value)
    current = await db.get_setting(db_key)
    await callback.message.answer(
        f"📝 Yangi matn kiriting:\n\n"
        f"Eslatma: HTML teglari mumkin. Profil matnida {{name}}, {{phone}}, {{ref_count}} o'zgaruvchilardan foydalanishingiz mumkin.\n\n"
        f"<b>Hozirgi matn:</b>\n{current}"
    )

@router.message(AdminState.setting_dynamic_value)
async def process_dynamic_value(message: Message, state: FSMContext):
    if not await check_admin(message.from_user.id): return
    data = await state.get_data()
    db_key = data.get("dy_key")
    if not db_key:
        await state.clear()
        return
        
    val = message.text.strip()
    await db.set_setting(db_key, val, message.from_user.id)
    
    # Refresh sets if it was a label
    if db_key.startswith("label_btn_"):
        from utils.i18n import refresh_btn_sets
        custom_labels = await db.get_all_settings()
        refresh_btn_sets(custom_labels)
        
    await state.clear()
    lang = await get_lang(message.from_user.id)
    from keyboards.admin_kb import admin_back_kb
    await message.answer("✅ Muvaffaqiyatli saqlandi!", reply_markup=admin_back_kb(lang=lang))
