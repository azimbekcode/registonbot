"""
Patch admin.py to add i18n support.
Adds: ta import, get_lang helper, updates all major message texts and keyboard calls.
"""
import re

with open("handlers/admin.py", "r", encoding="utf-8") as f:
    src = f.read()

# 1. Add 'ta' to imports from utils.i18n (add after existing imports)
if "from utils.i18n import ta" not in src:
    src = src.replace(
        "from config import config\n",
        "from config import config\nfrom utils.i18n import ta\n"
    )

# 2. Add get_lang helper after check_superadmin function
if "async def get_lang(" not in src:
    src = src.replace(
        "# ── /admin COMMAND",
        """async def get_lang(user_id: int) -> str:
    return await db.get_user_language(user_id)


# ── /admin COMMAND"""
    )

# 3. admin_panel: use ta()
src = src.replace(
    """    is_sa = await check_superadmin(message.from_user.id)
    stats = await db.get_stats()
    await message.answer(
        f\"⚙️ <b>ADMIN PANEL</b>\\n\"
        f\"Registon O'quv Markaz Bot\\n\\n\"
        f\"👥 Foydalanuvchilar: {stats['total']}\\n\"
        f\"✅ Ro'yxatdagilar: {stats['registered']}\\n\"
        f\"🏆 Ishtirokchilar: {stats['contestants']}\\n\"
        f\"📅 Bugun: {stats['today']}\",
        reply_markup=admin_main_kb(is_superadmin=is_sa),
    )""",
    """    lang = await get_lang(message.from_user.id)
    is_sa = await check_superadmin(message.from_user.id)
    stats = await db.get_stats()
    await message.answer(
        ta("admin_title", lang,
           total=stats["total"], registered=stats["registered"],
           contestants=stats["contestants"], today=stats["today"]),
        reply_markup=admin_main_kb(is_superadmin=is_sa, lang=lang),
    )"""
)

# 4. back_to_admin: use ta()
src = src.replace(
    """    await callback.message.edit_text(
        f\"⚙️ <b>ADMIN PANEL</b>\\n\"
        f\"Registon O'quv Markaz Bot\\n\\n\"
        f\"👥 Foydalanuvchilar: {stats['total']}\\n\"
        f\"✅ Ro'yxatdagilar: {stats['registered']}\\n\"
        f\"🏆 Ishtirokchilar: {stats['contestants']}\\n\"
        f\"📅 Bugun: {stats['today']}\",
        reply_markup=admin_main_kb(is_superadmin=is_sa),
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        ta("admin_title", lang,
           total=stats["total"], registered=stats["registered"],
           contestants=stats["contestants"], today=stats["today"]),
        reply_markup=admin_main_kb(is_superadmin=is_sa, lang=lang),
    )"""
)

# 5. admin_users: users_kb()
src = src.replace(
    """        reply_markup=users_kb(),
    )


@router.callback_query(F.data == \"admin_contestants\")""",
    """        reply_markup=users_kb(lang=await get_lang(callback.from_user.id)),
    )


@router.callback_query(F.data == \"admin_contestants\")"""
)

# 6. admin_contestants: use ta()
src = src.replace(
    """    lines = [f\"🏆 <b>KONKURS ISHTIROKCHILARI ({len(users)} ta)</b>\\n\"]
    for i, u in enumerate(users, 1):
        name = f\"{u['full_name'] or ''} {u['last_name_reg'] or ''}\".strip() or \"Noma'lum\"
        tg = f\"@{u['username']}\" if u[\"username\"] else str(u[\"telegram_id\"])
        lines.append(f\"{i}. {name} | {tg} | {u['phone'] or '-'}\")
    await callback.message.edit_text(
        \"\\n\".join(lines) if len(lines) > 1 else \"🏆 Hali ishtirokchilar yo'q.\",
        reply_markup=admin_back_kb(),
    )""",
    """    lang = await get_lang(callback.from_user.id)
    lines = [ta("contestants_list", lang, n=len(users))]
    for i, u in enumerate(users, 1):
        name = f\"{u['full_name'] or ''} {u['last_name_reg'] or ''}\".strip() or \"Noma'lum\"
        tg = f\"@{u['username']}\" if u[\"username\"] else str(u[\"telegram_id\"])
        lines.append(f\"{i}. {name} | {tg} | {u['phone'] or '-'}\")
    await callback.message.edit_text(
        \"\\n\".join(lines) if len(lines) > 1 else ta("contestants_empty", lang),
        reply_markup=admin_back_kb(lang=lang),
    )"""
)

# 7. admin_user_search: search_method_kb()
src = src.replace(
    """        reply_markup=search_method_kb(),
    )""",
    """        reply_markup=search_method_kb(lang=await get_lang(callback.from_user.id)),
    )"""
)

# 8. show_user_detail: use ta()
src = src.replace(
    """async def show_user_detail(message_or_cb, user_row, is_superadmin: bool = False):
    unknown = \"Noma'lum\"
    fn = user_row['full_name'] or ''
    ln = user_row['last_name_reg'] or ''
    name = f\"{fn} {ln}\".strip() or unknown
    tg = f\"@{user_row['username']}\" if user_row[\"username\"] else \"yo'q\"
    banned = bool(user_row[\"is_banned\"])
    ishtirokchi = \"Ha ✅\" if user_row['is_contestant'] else \"Yo'q\"
    bloklangan = \"Ha 🚫\" if banned else \"Yo'q\"
    ph = user_row['phone'] or 'Kiritilmagan'
    age = user_row['age'] or '-'
    prof = user_row['profession'] or '-'
    joined = str(user_row['joined_at'])[:10]
    ref_code = user_row['referral_code'] or '-'
    text = (
        f\"👤 <b>{name}</b>\\n\"
        f\"📱 {ph}\\n\"
        f\"🆔 Telegram ID: <code>{user_row['telegram_id']}</code>\\n\"
        f\"👤 Username: {tg}\\n\"
        f\"📅 Yosh: {age}\\n\"
        f\"💼 Kasb: {prof}\\n\"
        f\"🔗 Refallar: {user_row['referral_count']} | Kod: <code>{ref_code}</code>\\n\"
        f\"🏆 Ishtirokchi: {ishtirokchi}\\n\"
        f\"🚫 Bloklangan: {bloklangan}\\n\"
        f\"📆 Qo'shilgan: {joined}\"
    )
    kb = user_detail_kb(user_row[\"telegram_id\"], banned, is_superadmin=is_superadmin)
    if isinstance(message_or_cb, Message):
        await message_or_cb.answer(text, reply_markup=kb)
    else:
        await message_or_cb.message.edit_text(text, reply_markup=kb)""",
    """async def show_user_detail(message_or_cb, user_row, is_superadmin: bool = False, lang: str = "uz"):
    unknown = \"Noma'lum\"
    fn = user_row['full_name'] or ''
    ln = user_row['last_name_reg'] or ''
    name = f\"{fn} {ln}\".strip() or unknown
    tg = f\"@{user_row['username']}\" if user_row[\"username\"] else \"-\"
    banned = bool(user_row[\"is_banned\"])
    ph = user_row['phone'] or '-'
    prof = user_row['profession'] or '-'
    joined = str(user_row['joined_at'])[:10] if user_row['joined_at'] else '-'
    reg_at = str(user_row['registered_at'])[:10] if user_row.get('registered_at') else '-'
    refs = user_row['referral_count'] or 0
    ishtirokchi = \"Ha ✅\" if user_row['is_contestant'] else \"Yo'q\"
    bloklangan = \"Ha 🚫\" if banned else \"Yo'q\"
    text = ta(\"user_detail\", lang,
        id=user_row['telegram_id'], name=name, phone=ph, prof=prof,
        uname=tg, joined=joined, reg_at=reg_at,
        contestant=ishtirokchi, refs=refs, banned=bloklangan,
    )
    kb = user_detail_kb(user_row[\"telegram_id\"], banned, is_superadmin=is_superadmin, lang=lang)
    if isinstance(message_or_cb, Message):
        await message_or_cb.answer(text, reply_markup=kb)
    else:
        await message_or_cb.message.edit_text(text, reply_markup=kb)"""
)

# 9. admin_view_user: pass lang
src = src.replace(
    """    is_sa = await check_superadmin(callback.from_user.id)
    await show_user_detail(callback, user_row, is_superadmin=is_sa)


""",
    """    is_sa = await check_superadmin(callback.from_user.id)
    lang = await get_lang(callback.from_user.id)
    await show_user_detail(callback, user_row, is_superadmin=is_sa, lang=lang)


"""
)

# 10. admin_ban_user
src = src.replace(
    """    await callback.answer(\"🚫 Foydalanuvchi bloklandi.\", show_alert=True)
    user_row = await db.get_user(tid)
    if user_row:
        is_sa = await check_superadmin(callback.from_user.id)
        await show_user_detail(callback, user_row, is_superadmin=is_sa)""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta(\"user_banned\", lang), show_alert=True)
    user_row = await db.get_user(tid)
    if user_row:
        is_sa = await check_superadmin(callback.from_user.id)
        await show_user_detail(callback, user_row, is_superadmin=is_sa, lang=lang)"""
)

# 11. admin_unban_user
src = src.replace(
    """    await callback.answer(\"✅ Ban olib tashlandi.\", show_alert=True)
    user_row = await db.get_user(tid)
    if user_row:
        is_sa = await check_superadmin(callback.from_user.id)
        await show_user_detail(callback, user_row, is_superadmin=is_sa)""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta(\"user_unbanned\", lang), show_alert=True)
    user_row = await db.get_user(tid)
    if user_row:
        is_sa = await check_superadmin(callback.from_user.id)
        await show_user_detail(callback, user_row, is_superadmin=is_sa, lang=lang)"""
)

# 12. admin_delete_user_confirm
src = src.replace(
    """    if not user_row:
        return await callback.answer(\"❌ Foydalanuvchi topilmadi.\", show_alert=True)
    unknown = \"Noma'lum\"
    fn = user_row[\"full_name\"] or unknown
    ph = user_row[\"phone\"] or \"-\"
    await callback.message.edit_text(
        f\"🗑️ <b>Haqiqatan ham o'chirilsinmi?</b>\\n\\n\"
        f\"👤 {fn}\\n\"
        f\"📱 {ph}\\n\"
        f\"🆔 ID: <code>{tid}</code>\\n\\n\"
        f\"⚠️ Bu amalni <b>bekor qilib bo'lmaydi!</b>\",
        reply_markup=confirm_delete_user_kb(tid),
    )""",
    """    if not user_row:
        lang0 = await get_lang(callback.from_user.id)
        return await callback.answer(ta(\"user_not_found\", lang0), show_alert=True)
    lang = await get_lang(callback.from_user.id)
    fn = user_row[\"full_name\"] or \"-\"
    ph = user_row[\"phone\"] or \"-\"
    await callback.message.edit_text(
        ta(\"delete_confirm\", lang, name=fn, phone=ph),
        reply_markup=confirm_delete_user_kb(tid, lang=lang),
    )"""
)

# 13. admin_confirm_delete_user
src = src.replace(
    """    await callback.answer(\"✅ Foydalanuvchi o'chirildi.\", show_alert=True)
    await callback.message.edit_text(
        f\"✅ <b>Foydalanuvchi o'chirildi!</b>\\n\"
        f\"🆔 ID: <code>{tid}</code>\",
        reply_markup=admin_back_kb(),
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta(\"user_deleted\", lang), show_alert=True)
    await callback.message.edit_text(
        ta(\"user_deleted\", lang) + f\"\\n🆔 ID: <code>{tid}</code>\",
        reply_markup=admin_back_kb(lang=lang),
    )"""
)

# 14. Fix no_access messages (simple replace all)
src = src.replace(
    'return await callback.answer(\"❌ Ruxsat yo\'q.\", show_alert=True)',
    'return await callback.answer(ta(\"no_access\", \"uz\"), show_alert=True)'
)
src = src.replace(
    'return await callback.answer(\"❌ Faqat superadmin o\'chira oladi!\", show_alert=True)',
    'return await callback.answer(ta(\"no_access\", \"uz\"), show_alert=True)'
)

with open("handlers/admin.py", "w", encoding="utf-8") as f:
    f.write(src)

print("Done! Patched admin.py successfully.")
