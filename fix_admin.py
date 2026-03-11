"""
admin.py database viewer bo'limini to'g'rilash uchun script.
"""
import re

with open("handlers/admin.py", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

# 985-qatorgacha saqlaymiz (broadcast bo'limi tugashi)
base_lines = lines[:985]
base = "\n".join(base_lines)

new_viewer = r'''


# -- DATABASE VIEWER (SUPERADMIN ONLY) --------------------------

PAGE_SIZE = 5  # Bir sahifada ko'rsatiladigan userlar soni


@router.callback_query(F.data == "sa_db_viewer")
async def sa_db_viewer(callback: CallbackQuery):
    if not await check_superadmin(callback.from_user.id):
        return await callback.answer("Faqat superadmin uchun!", show_alert=True)
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
    for u in chunk:
        fn = u["full_name"] or ""
        ln = u["last_name_reg"] or ""
        name = (fn + " " + ln).strip() or "Noma'lum"
        reg = "Reg:HA" if u["is_registered"] else "Reg:YOQ"
        ban = " BAN" if u["is_banned"] else ""
        joined = str(u["joined_at"])[:10]
        uname = u["username"] or "-"
        phone = u["phone"] or "-"
        age = u["age"] or "-"
        prof = u["profession"] or "-"
        ref_count = u["referral_count"]
        tid = u["telegram_id"]
        lines.append(
            f"- <b>{name}</b>{ban}\n"
            f"  ID: <code>{tid}</code> | @{uname}\n"
            f"  Tel: {phone} | Yosh: {age} | Kasb: {prof}\n"
            f"  {reg} | Ref:{ref_count} | {joined}"
        )

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=db_users_page_kb(page, total_pages),
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
'''

result = base + new_viewer

with open("handlers/admin.py", "w", encoding="utf-8") as f:
    f.write(result)

print("Done! Lines:", result.count("\n"))
