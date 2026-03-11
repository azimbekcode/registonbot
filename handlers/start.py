"""
Start handler — /start with channel check, main menu via ReplyKeyboard.
All messages are multilingual via i18n.
"""

import logging
from aiogram import Router, Bot, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import db
from keyboards.user_kb import (
    channel_check_kb,
    main_menu_kb,
    referral_kb,
    remove_kb,
)
from keyboards.admin_kb import user_ref_leaderboard_kb
from utils.channel_check import check_subscriptions
from utils.i18n import (
    t,
    BTN_INVITE, BTN_REFERRALS, BTN_COURSES,
    BTN_PROFILE, BTN_CONTEST,
    BTN_CONTEST_RULES, BTN_RESULTS,
    BTN_REGISTER,
)

logger = logging.getLogger(__name__)
router = Router(name="start")


async def get_bot_username(bot: Bot) -> str:
    me = await bot.get_me()
    return me.username


async def get_lang(user_id: int) -> str:
    """Shortcut: get user language, default 'uz'."""
    return await db.get_user_language(user_id)


async def get_user_menu_kb(user_id: int, is_registered: bool, is_contestant: bool, lang: str):
    labels = await db.get_all_settings()
    from keyboards.user_kb import main_menu_kb
    return main_menu_kb(is_registered, is_contestant, lang, labels)


async def show_main_panel(send_fn, bot: Bot, user_row, lang: str = "uz"):
    """Show main panel after subscription/registration."""
    is_registered = bool(user_row["is_registered"]) if user_row else False
    is_contestant = bool(user_row["is_contestant"]) if user_row else False
    fn = (user_row.get("full_name") or user_row.get("first_name") or "") if user_row else ""

    if not is_registered:
        name_part = f", <b>{fn}</b>" if fn else ""
        await send_fn(
            t("welcome_unreg", lang, name=name_part),
            reply_markup=await get_user_menu_kb(user_row["telegram_id"], False, False, lang),
        )
        return

    ref_count = user_row["referral_count"] or 0
    req = int(await db.get_setting("required_referrals") or "5")
    filled = "\u2705" * ref_count
    empty = "\u2b1c" * max(0, req - ref_count)

    text = t("welcome_registered", lang,
             name=fn, cur=ref_count, req=req,
             filled=filled, empty=empty,
             left=max(0, req - ref_count))

    await send_fn(
        text,
        reply_markup=await get_user_menu_kb(user_row["telegram_id"], True, is_contestant, lang),
    )


# ── /start ─────────────────────────────────────────────────────

@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext, db_user=None):
    await state.clear()
    args = message.text.split(maxsplit=1)
    referral_code = args[1].strip() if len(args) > 1 else None
    user_id = message.from_user.id

    user_row = db_user or await db.get_user(user_id)
    lang = await get_lang(user_id)

    if referral_code and user_row:
        inviter = await db.get_user_by_referral_code(referral_code)
        if inviter and inviter["telegram_id"] != user_id:
            # Check DB again for fresh status
            fresh_user = await db.get_user(user_id)
            if fresh_user and not fresh_user["referred_by"]:
                await db.update_user(user_id, referred_by=inviter["telegram_id"])
                logger.info(f"User {user_id} set referred_by={inviter['telegram_id']} via link")
            
            # Save to state as backup for registration
            await state.update_data(referral_code=referral_code)

    channels = await db.get_active_channels()

    if not channels:
        user_row = await db.get_user(user_id)
        await show_main_panel(message.answer, bot, user_row, lang)
        return

    all_subscribed, results = await check_subscriptions(bot, user_id, channels)
    if not all_subscribed:
        not_joined = [ch for ch, ok in zip(channels, results) if not ok]
        await message.answer(
            t("channel_join_prompt", lang, n=len(not_joined)),
            reply_markup=channel_check_kb(not_joined, lang=lang),
        )
        return

    user_row = await db.get_user(user_id)
    await show_main_panel(message.answer, bot, user_row, lang)


# ── Channel check ──────────────────────────────────────────────

@router.callback_query(F.data == "check_subscription")
async def check_subscription_cb(callback: CallbackQuery, bot: Bot, state: FSMContext):
    user_id = callback.from_user.id
    lang = await get_lang(user_id)
    channels = await db.get_active_channels()
    all_sub, results = await check_subscriptions(bot, user_id, channels)
    if not all_sub:
        not_joined = [ch for ch, ok in zip(channels, results) if not ok]
        await callback.answer(t("not_subscribed", lang, n=len(not_joined)), show_alert=True)
        return
    await callback.answer("✅")
    try:
        await callback.message.delete()
    except Exception:
        pass
    user_row = await db.get_user(user_id)
    await show_main_panel(callback.message.answer, bot, user_row, lang)


# ── ReplyKeyboard menu buttons ─────────────────────────────────

@router.message(F.text.in_(BTN_INVITE))
async def menu_share(message: Message, bot: Bot):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    user_row = await db.get_user(user_id)
    if not user_row or not user_row["is_registered"]:
        await message.answer(t("not_registered", lang))
        return

    req = int(await db.get_setting("required_referrals") or "5")
    ref_count = user_row["referral_count"] or 0
    bot_username = await get_bot_username(bot)
    ref_code = user_row["referral_code"] or ""
    ref_link = f"https://t.me/{bot_username}?start={ref_code}"
    
    # Tanlov matnini bazadan o'qiymiz
    custom_invite_text = await db.get_setting("invite_text")
    if custom_invite_text:
        contest_text = custom_invite_text
    else:
        # Yangi tanlov matni (Default)
        contest_text = (
            "📚 <b>Maxsus milliy sertifikat kitoblari tanloviga start beramiz!</b>\n\n"
            "📚 Tanlovda qatnashish uchun ishtirokchilar 👉 @onatilidarslar_bot manzili orqali ro'yxatdan o'tib, "
            "o'zlariga biriktirilgan maxsus havola orqali 18-mart sanasiga qadar eng ko'p tanishlarini taklif qilishlari kerak bo'ladi.\n\n"
            "✅ <b>Tanlov g'oliblari quyidagicha aniqlanadi:</b>\n"
            "🔹 1-o'rin — Ona tili MS qo'llanma (3 ta kitob) + tezkor milliy sertifikat kursi uchun 100% chegirma\n"
            "🔹 2-o'rin — Ona tili MS qo'llanma (3 ta kitob) + tezkor milliy sertifikat kursi uchun 50% chegirma\n"
            "🔹 3-o'rin — Ona tili MS qo'llanma (3 ta kitob) + tezkor milliy sertifikat kursi uchun 30% chegirma\n"
            "🔹 4-10-o'rinlar — Ona tili MS qo'llanma (3 ta kitob) + tezkor milliy sertifikat kursi uchun 10% chegirma\n\n"
            "✅ <b>Maxsus sovrin:</b>\n"
            "🎁  18-mart kuni jonli efirda tanlovga 10 tadan ko'p tanishlarini taklif qilgan ishtiokchilar ichidan 1 kishiga "
            "Milliy sertifikat imtihonini to'lab beruvchi maxsus vaucher g'olibini aniqlaymiz!\n\n"
            "🔖  Tanlovda g'olib bo'lgan barcha ishtirokchilar sertifikat bilan taqdirlanadi."
        )

    # 1-xabar: Tanlov haqida ma'lumot
    await message.answer(contest_text)
    
    # 2-xabar: Referral havola
    link_text = (
        f"🔗 <b>Sizning taklif havolangiz:</b>\n"
        f"<code>{ref_link}</code>"
    )
    await message.answer(
        link_text, 
        reply_markup=referral_kb(ref_link, ref_count, req, lang=lang)
    )


@router.message(F.text.in_(BTN_REFERRALS))
async def menu_referrals(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    ref_list = await db.get_referral_list(user_id)
    if not ref_list:
        await message.answer(t("referrals_empty", lang))
        return
    unknown = "Noma'lum"
    lines = [t("referrals_title", lang, n=len(ref_list))]
    for i, r in enumerate(ref_list, 1):
        name = r["full_name"] or r["username"] or unknown
        lines.append(f"{i}. {name}")
    await message.answer("\n".join(lines))




@router.message(F.text.in_(BTN_PROFILE))
async def menu_profile(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    user_row = await db.get_user(user_id)
    if not user_row: return
    
    text_tpl = await db.get_setting("text_profile") or "👤 <b>PROFIL</b>\n\nIsm: {name}\nTel: {phone}\nReferallaringiz: {ref_count} ta"
    text = text_tpl.format(
        name=user_row["full_name"] or user_row["username"] or "—",
        phone=user_row["phone"] or "—",
        ref_count=user_row["referral_count"] or 0
    )
    await message.answer(text)


@router.message(F.text.in_(BTN_CONTEST_RULES))
async def menu_contest_rules(message: Message):
    """Tanlov shartlarini ko'rsatish."""
    user_id = message.from_user.id
    lang = await get_lang(user_id)

    # Admin tomonidan kiritilgan maxsus matnni o'qi
    custom_text = await db.get_setting("contest_rules_text")
    if custom_text:
        await message.answer(custom_text)
    else:
        req = int(await db.get_setting("required_referrals") or "5")
        await message.answer(
            f"\U0001f4cb <b>TANLOV SHARTLARI</b>\n\n"
            f"\U0001f3af Tanlovda ishtirok etish uchun:\n\n"
            f"1\ufe0f\u20e3 Ro'yxatdan o'ting\n"
            f"2\ufe0f\u20e3 <b>{req} ta</b> do'stingizni taklif qiling\n"
            f"3\ufe0f\u20e3 Taklif qilingan do'stlaringiz ham ro'yxatdan o'tishi kerak\n\n"
            f"\U0001f3c6 Eng ko'p do'st taklif qilgan ishtirokchilar g'olib sifatida tanlanadi!\n\n"
            f"\U0001f4cc Qo'shimcha ma'lumot uchun admin bilan bog'laning."
        )


@router.message(F.text.in_(BTN_RESULTS))
async def menu_results(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    """Natijalarni ko'rsatish — referral reytingi."""
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    user_row = await db.get_user(user_id)
    if not user_row:
        return
    req = int(await db.get_setting("required_referrals") or "5")
    ref_count = user_row["referral_count"] or 0

    # PROACTIVE STATUS UPDATE: Dinamik tekshiruv
    if ref_count >= req:
        if not user_row["is_contestant"]:
            await db.make_contestant(user_id)
            user_row = await db.get_user(user_id) # Refresh data
    else:
        if user_row["is_contestant"]:
            await db.remove_contestant(user_id)
            user_row = await db.get_user(user_id) # Refresh data

    bot_username = await get_bot_username(bot)
    ref_code = user_row["referral_code"] or ""
    ref_link = f"https://t.me/{bot_username}?start={ref_code}"
    filled = "\u2705" * ref_count
    empty = "\u2b1c" * max(0, req - ref_count)
    total = await db.get_contest_count()
    fn_user = user_row["full_name"] or "—"
    ishtirokchi = t("yes", lang) if user_row["is_contestant"] else t("not_yet", lang)

    top_users = await db.get_referral_leaderboard(limit=20)
    unknown = "Noma'lum"
    lb_lines = ["\n📊 <b>Top 20 referral reytingi:</b>"]
    if not top_users:
        lb_lines.append("<i>Hali hech kim referal yig'magan.</i>")
    else:
        for i, u in enumerate(top_users, 1):
            fn = u["full_name"] or ""
            ln = u["last_name_reg"] or ""
            name = f"{fn} {ln}".strip() or u["username"] or unknown
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            lb_lines.append(f"{medal} {name} — <b>{u['referral_count']}</b>")

    text = (
        (await db.get_setting("text_results_main") or "🏅 <b>NATIJALAR</b>") + "\n\n"
        f"👤 {fn_user}\n"
        f"📱 {user_row['phone'] or '—'}\n"
        f"{t('stats_invited', lang)}: {ref_count}/{req} {filled}{empty}\n"
        f"{t('stats_contestant', lang)}: {ishtirokchi}\n"
        f"{t('stats_total', lang)}: <b>{total}</b>\n\n"
        + "\n".join(lb_lines)
    )

    await message.answer(
        text,
        reply_markup=user_ref_leaderboard_kb(lang=lang),
    )


@router.callback_query(F.data == "user_ref_lb_all_options")
async def user_ref_lb_all_options(callback: CallbackQuery):
    from keyboards.admin_kb import user_ref_lb_options_kb
    lang = await get_lang(callback.from_user.id)
    try:
        await callback.message.edit_reply_markup(reply_markup=user_ref_lb_options_kb(lang=lang))
    except Exception:
        pass


@router.callback_query(F.data.startswith("user_ref_lb_"))
async def user_ref_lb_limit_cb(callback: CallbackQuery):
    limit_str = callback.data.replace("user_ref_lb_", "")
    if limit_str == "all_options": return
    
    await callback.answer()
    lang = await get_lang(callback.from_user.id)
    limit = None if limit_str == "all" else int(limit_str)
    
    top_users = await db.get_referral_leaderboard(limit=limit)
    unknown = "Noma'lum"
    
    title = f"Top {limit}" if limit else "Barcha"
    lb_lines = [f"\n📊 <b>{title} referral reytingi:</b>"]
    
    if not top_users:
        lb_lines.append("<i>Hali hech kim referal yig'magan.</i>")
    else:
        for i, u in enumerate(top_users, 1):
            fn = u["full_name"] or ""
            ln = u["last_name_reg"] or ""
            name = f"{fn} {ln}".strip() or u["username"] or unknown
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            lb_lines.append(f"{medal} {name} — <b>{u['referral_count']}</b>")
            if limit and i >= limit: break

    # Extract user stats for the top part (could be optimized but let's keep it consistent)
    user_id = callback.from_user.id
    user_row = await db.get_user(user_id)
    ref_count = int(user_row["referral_count"] or 0)
    req_val = await db.get_setting("required_referrals")
    try:
        req = int(req_val or "10")
    except (ValueError, TypeError):
        req = 10
    
    total = await db.get_contest_count()
    ishtirokchi = t("yes", lang) if user_row["is_contestant"] else t("not_yet", lang)
    ref_link = f"https://t.me/{(await callback.bot.get_me()).username}?start={user_id}"
    fn_user = user_row["full_name"] or "—"
    
    filled = "\u2705" * min(ref_count, req)
    empty = "\u2b1c" * max(0, req - ref_count)

    text = (
        (await db.get_setting("text_results_main") or "🏅 <b>NATIJALAR</b>") + "\n\n"
        f"👤 {fn_user}\n"
        f"📱 {user_row['phone'] or '—'}\n"
        f"{t('stats_invited', lang)}: {ref_count}/{req} {filled}{empty}\n"
        f"{t('stats_contestant', lang)}: {ishtirokchi}\n"
        f"{t('stats_total', lang)}: <b>{total}</b>\n\n"
        + "\n".join(lb_lines)
    )
    
    from keyboards.admin_kb import user_ref_leaderboard_kb
    try:
        await callback.message.edit_text(
            text,
            reply_markup=user_ref_leaderboard_kb(lang=lang),
        )
    except Exception:
        pass


@router.callback_query(F.data == "back_to_results")
async def back_to_results_cb(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    from keyboards.admin_kb import user_ref_leaderboard_kb
    try:
        await callback.message.edit_reply_markup(reply_markup=user_ref_leaderboard_kb(lang=lang))
    except Exception:
        pass



@router.message(F.text.in_(BTN_CONTEST))
async def menu_contest(message: Message):
    user_id = message.from_user.id
    lang = await get_lang(user_id)
    total = await db.get_contest_count()
    ref_list = await db.get_referral_list(user_id)
    unknown = "Noma'lum"
    names = "\n".join(
        f"  • {r['full_name'] or r['username'] or unknown}" for r in ref_list
    ) or t("contest_none", lang)
    await message.answer(
        f"{t('contest_title', lang)}\n\n"
        f"{t('contest_total', lang, n=total)}\n\n"
        f"{t('contest_my_refs', lang)}\n{names}"
    )


@router.callback_query(F.data == "back_to_main")
async def back_to_main_cb(callback: CallbackQuery):
    """Global handler for back_to_main — deletes the inline message."""
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass


# ── Til tanlash ────────────────────────────────────────────────

@router.callback_query(F.data == "settings_choose_lang")
async def settings_choose_lang(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇿 O'zbek",  callback_data="set_lang_uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang_ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang_en"),
    )
    await callback.answer()
    await callback.message.edit_text(
        t("choose_language", lang),
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data.startswith("set_lang_"))
async def set_language(callback: CallbackQuery, bot: Bot):
    new_lang = callback.data.replace("set_lang_", "")
    if new_lang not in ("uz", "ru", "en"):
        return await callback.answer("❌", show_alert=True)

    await db.set_user_language(callback.from_user.id, new_lang)
    await callback.answer(t("language_changed", new_lang), show_alert=True)

    try:
        await callback.message.delete()
    except Exception:
        pass

    # Yangi tilda sozlamalar menyusini qayta ko'rsatish
    user_row = await db.get_user(callback.from_user.id)
    fn = (user_row["full_name"] or "—") if user_row else "—"
    phone = (user_row["phone"] or "—") if user_row else "—"
    lang_names = {"uz": "O'zbek 🇺🇿", "ru": "Русский 🇷🇺", "en": "English 🇬🇧"}

    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=f"🌐 {t('settings_change_lang_btn', new_lang)}",
            callback_data="settings_choose_lang",
        )
    )
    await callback.message.answer(
        f"{t('settings_title', new_lang)}\n\n"
        f"{t('settings_name', new_lang)}: <b>{fn}</b>\n"
        f"{t('settings_phone', new_lang)}: <b>{phone}</b>\n"
        f"{t('settings_language', new_lang)}: <b>{lang_names[new_lang]}</b>",
        reply_markup=builder.as_markup(),
    )

    # Asosiy menyu klaviaturasini yangi tilda yangilash
    if user_row:
        is_reg = bool(user_row["is_registered"])
        is_con = bool(user_row["is_contestant"])
        await callback.message.answer(
            t("main_menu", new_lang),
            reply_markup=main_menu_kb(is_registered=is_reg, is_contestant=is_con, lang=new_lang),
        )



# ── Course forward ─────────────────────────────────────────────



# ── Foydalanuvchi Referral Reytingi ────────────────────────────────────

@router.callback_query(F.data.startswith("user_ref_lb_"))
async def user_ref_leaderboard(callback: CallbackQuery):
    suffix = callback.data.replace("user_ref_lb_", "")

    # "all" yoki raqam
    if suffix == "all":
        limit = None
    else:
        try:
            limit = int(suffix)
        except ValueError:
            limit = None

    await callback.answer()
    lang = await get_lang(callback.from_user.id)
    users = await db.get_referral_leaderboard(limit=limit)

    if not users:
        await callback.message.answer(
            "📊 <b>Referral reytingi</b>\n\nHali hech kim referal yig'magan."
        )
        return

    unknown = "Noma'lum"
    title = "📊 <b>Referral reytingi — Barcha ishtirokchilar</b>\n"
    lines = [title]
    for i, u in enumerate(users, 1):
        fn = u["full_name"] or ""
        ln = u["last_name_reg"] or ""
        name = f"{fn} {ln}".strip() or u["username"] or unknown
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        lines.append(f"{medal} {name} — <b>{u['referral_count']}</b> referal")

    # Telegram 4096 belgi limitiga mos qismlarga bo'lish
    chunk_text = ""
    first_sent = False
    for line in lines:
        candidate = chunk_text + "\n" + line if chunk_text else line
        if len(candidate) > 3800:
            if not first_sent:
                await callback.message.answer(chunk_text)
                first_sent = True
            else:
                await callback.message.answer(chunk_text)
            chunk_text = line
        else:
            chunk_text = candidate

    if chunk_text:
        if not first_sent:
            await callback.message.answer(
                chunk_text,
                reply_markup=user_ref_leaderboard_kb(lang=lang),
            )
        else:
            await callback.message.answer(chunk_text)
