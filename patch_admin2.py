"""
Patch admin.py — Part 2: stats, channels, courses, settings, admins, broadcast sections.
"""

with open("handlers/admin.py", "r", encoding="utf-8") as f:
    src = f.read()

# ── Channels ─────────────────────────────────────────────────────
src = src.replace(
    """    await callback.message.edit_text(text, reply_markup=channels_kb(channels))""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(text, reply_markup=channels_kb(channels, lang=lang))"""
)

src = src.replace(
    """    await callback.answer(\"✅ Yangilandi.\")
    channels = await db.get_all_channels()
    await callback.message.edit_reply_markup(reply_markup=channels_kb(channels))""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta(\"channel_toggled\", lang))
    channels = await db.get_all_channels()
    await callback.message.edit_reply_markup(reply_markup=channels_kb(channels, lang=lang))"""
)

src = src.replace(
    """    await callback.answer(\"🗑 Kanal o'chirildi.\")
    channels = await db.get_all_channels()
    await callback.message.edit_reply_markup(reply_markup=channels_kb(channels))""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta(\"channel_deleted\", lang))
    channels = await db.get_all_channels()
    await callback.message.edit_reply_markup(reply_markup=channels_kb(channels, lang=lang))"""
)

src = src.replace(
    """    await callback.message.answer(
        \"📢 Kanal username yoki ID yuboring:\\n\"
        \"<i>Masalan: @mening_kanalim yoki -100123456789</i>\\n\\n\"
        \"⚠️ Bot kanalda admin bo'lishi kerak!\",
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(ta(\"channel_add_prompt\", lang))"""
)

# ── Courses ───────────────────────────────────────────────────────
src = src.replace(
    """    await callback.message.edit_text(
        \"📚 <b>DARSLIKLAR BOSHQARUVI</b>\",
        reply_markup=courses_admin_kb(courses),
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        ta(\"course_add_title\", lang).replace(\"Darslik nomini kiriting:\", \"📚 <b>DARSLIKLAR</b>\"),
        reply_markup=courses_admin_kb(courses, lang=lang),
    )"""
)

src = src.replace(
    """    await callback.message.answer(\"📚 Darslik nomini kiriting:\")""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(ta(\"course_add_title\", lang))"""
)

src = src.replace(
    """    await message.answer(\"📝 Darslik tavsifini kiriting (yoki '-' bosing o'tkazsh uchun):\")""",
    """    lang = await get_lang(message.from_user.id)
    await message.answer(ta(\"course_add_desc\", lang))"""
)

src = src.replace(
    """    await callback.answer(\"✅ Yangilandi.\")
    courses = await db.get_all_courses()
    await callback.message.edit_reply_markup(reply_markup=courses_admin_kb(courses))""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.answer(\"✅\")
    courses = await db.get_all_courses()
    await callback.message.edit_reply_markup(reply_markup=courses_admin_kb(courses, lang=lang))"""
)

src = src.replace(
    """    await callback.answer(\"🗑 Darslik o'chirildi.\")
    courses = await db.get_all_courses()
    await callback.message.edit_reply_markup(reply_markup=courses_admin_kb(courses))""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta(\"course_deleted\", lang))
    courses = await db.get_all_courses()
    await callback.message.edit_reply_markup(reply_markup=courses_admin_kb(courses, lang=lang))"""
)

# Add lang to add_course admin_back_kb calls (course forward handler)
src = src.replace(
    """        reply_markup=admin_back_kb(),
    )
    if not await check_admin(message.from_user.id):""",
    """        reply_markup=admin_back_kb(lang=await get_lang(message.from_user.id)),
    )
    if not await check_admin(message.from_user.id):"""
)

# ── Statistics ────────────────────────────────────────────────────
src = src.replace(
    """    top_lines = []
    for i, r in enumerate(stats[\"top_referrers\"], 1):
        name = r[\"full_name\"] or r[\"username\"] or str(r[\"telegram_id\"])
        top_lines.append(f\"  {i}. {name} — {r['referral_count']} kishi\")
    top_text = \"\\n\".join(top_lines) if top_lines else \"  Hali yo'q\"

    text = (
        f\"📊 <b>BOT STATISTIKASI</b>\\n\\n\"
        f\"👥 Jami foydalanuvchilar: <b>{stats['total']}</b>\\n\"
        f\"✅ Ro'yxatdan o'tganlar: <b>{stats['registered']}</b>\\n\"
        f\"🏆 Konkurs ishtirokchilari: <b>{stats['contestants']}</b>\\n\"
        f\"📱 Bugun qo'shildi: <b>{stats['today']}</b>\\n\"
        f\"📅 Bu hafta: <b>{stats['week']}</b>\\n\"
        f\"📆 Bu oy: <b>{stats['month']}</b>\\n\\n\"
        f\"🔗 Eng ko'p referal:\\n{top_text}\"
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=\"📥 Batafsil hisobot (.txt)\", callback_data=\"admin_export_users\")
    )
    builder.row(
        InlineKeyboardButton(text=\"🔙 Admin panel\", callback_data=\"back_to_admin\")
    )
    await callback.message.edit_text(text, reply_markup=builder.as_markup())""",
    """    lang = await get_lang(callback.from_user.id)
    top_lines = []
    for i, r in enumerate(stats[\"top_referrers\"], 1):
        name = r[\"full_name\"] or r[\"username\"] or str(r[\"telegram_id\"])
        top_lines.append(f\"  {i}. {name} — {r['referral_count']}\")
    top_text = \"\\n\".join(top_lines) if top_lines else \"  —\"
    pending = stats.get(\"total\", 0) - stats.get(\"registered\", 0)
    banned = stats.get(\"banned\", 0)

    text = (
        ta(\"admin_stats\", lang,
           total=stats[\"total\"], registered=stats[\"registered\"],
           contestants=stats[\"contestants\"], pending=pending,
           banned=banned, today=stats[\"today\"])
        + f\"\\n\\n🔗 Top referrers:\\n{top_text}\"
    )

    from aiogram.utils.keyboard import InlineKeyboardBuilder as _IKB
    from aiogram.types import InlineKeyboardButton as _IKBBtn
    _builder = _IKB()
    _builder.row(_IKBBtn(text=ta(\"btn_full_report\", lang), callback_data=\"admin_export_users\"))
    _builder.row(_IKBBtn(text=ta(\"btn_back_admin\", lang), callback_data=\"back_to_admin\"))
    await callback.message.edit_text(text, reply_markup=_builder.as_markup())"""
)

# ── Settings ──────────────────────────────────────────────────────
src = src.replace(
    """    await callback.message.edit_text(
        \"⚙️ <b>SOZLAMALAR</b>\",
        reply_markup=settings_kb(settings),
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        ta(\"btn_bot_settings\", lang),
        reply_markup=settings_kb(settings, lang=lang),
    )"""
)

src = src.replace(
    """    settings = await db.get_all_settings()
    await callback.message.edit_reply_markup(reply_markup=settings_kb(settings))


@router.callback_query(F.data.startswith(\"admin_set_reg_\"))""",
    """    lang = await get_lang(callback.from_user.id)
    settings = await db.get_all_settings()
    await callback.message.edit_reply_markup(reply_markup=settings_kb(settings, lang=lang))


@router.callback_query(F.data.startswith(\"admin_set_reg_\"))"""
)

src = src.replace(
    """    settings = await db.get_all_settings()
    await callback.message.edit_reply_markup(reply_markup=settings_kb(settings))


@router.callback_query(F.data == \"admin_set_ref_count\")""",
    """    lang = await get_lang(callback.from_user.id)
    settings = await db.get_all_settings()
    await callback.message.edit_reply_markup(reply_markup=settings_kb(settings, lang=lang))


@router.callback_query(F.data == \"admin_set_ref_count\")"""
)

src = src.replace(
    """    await callback.message.answer(f\"🔢 Hozirgi referal talabi: <b>{current}</b>\\n\\nYangi sonini kiriting (1-100):\")""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(ta(\"set_ref_prompt\", lang) + f\"\\nHozirgi: <b>{current}</b>\")"""
)

src = src.replace(
    """    await message.answer(f\"✅ Referal talabi: <b>{val} ta</b> ga o'zgartirildi.\", reply_markup=admin_back_kb())""",
    """    lang = await get_lang(message.from_user.id)
    await message.answer(ta(\"set_ref_done\", lang, n=val), reply_markup=admin_back_kb(lang=lang))"""
)

src = src.replace(
    """    await callback.message.answer(
        f\"✉️ Hozirgi xush kelibsiz xabar:\\n<i>{current}</i>\\n\\nYangi xabar yuboring:\"
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(
        ta(\"set_welcome_prompt\", lang) + f\"\\n\\n<i>{current}</i>\"
    )"""
)

src = src.replace(
    """    await message.answer(\"✅ Xush kelibsiz xabar yangilandi.\", reply_markup=admin_back_kb())""",
    """    lang = await get_lang(message.from_user.id)
    await message.answer(ta(\"set_welcome_done\", lang), reply_markup=admin_back_kb(lang=lang))"""
)

# ── Admins ────────────────────────────────────────────────────────
src = src.replace(
    """    text = f\"👮 <b>ADMINLAR ({len(admins)} ta)</b>\"
    await callback.message.edit_text(
        text,
        reply_markup=admins_kb(admins, config.superadmin_id),
    )""",
    """    lang = await get_lang(callback.from_user.id)
    text = f\"👮 <b>ADMINLAR ({len(admins)} ta)</b>\"
    await callback.message.edit_text(
        text,
        reply_markup=admins_kb(admins, config.superadmin_id, lang=lang),
    )"""
)

src = src.replace(
    """    await callback.message.answer(\"👮 Yangi admin Telegram ID sini yuboring:\")""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(ta(\"admin_add_prompt\", lang))"""
)

src = src.replace(
    """    await message.answer(
        f\"✅ Admin qo'shildi: <code>{new_admin_id}</code>\",
        reply_markup=admin_back_kb(),
    )""",
    """    lang = await get_lang(message.from_user.id)
    await message.answer(
        ta(\"admin_added\", lang) + f\" <code>{new_admin_id}</code>\",
        reply_markup=admin_back_kb(lang=lang),
    )"""
)

src = src.replace(
    """    await callback.answer(\"✅ Admin o'chirildi.\")
    admins = await db.get_all_admins()
    await callback.message.edit_reply_markup(
        reply_markup=admins_kb(admins, config.superadmin_id)
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.answer(ta(\"admin_removed\", lang))
    admins = await db.get_all_admins()
    await callback.message.edit_reply_markup(
        reply_markup=admins_kb(admins, config.superadmin_id, lang=lang)
    )"""
)

# ── Broadcast ─────────────────────────────────────────────────────
src = src.replace(
    """    await callback.message.edit_text(
        \"📣 <b>XABAR YUBORISH</b>\\n\\nMaqsadli guruhni tanlang:\",
        reply_markup=broadcast_target_kb(),
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.edit_text(
        ta(\"broadcast_write\", lang),
        reply_markup=broadcast_target_kb(lang=lang),
    )"""
)

src = src.replace(
    """    await callback.message.answer(
        f\"📤 <b>{len(users)} kishi</b>ga xabar yuboriladi.\\n\\n\"
        \"Xabarni yuboring (matn, rasm, video — hammasi ishlaydi):\"
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(ta(\"broadcast_write\", lang) + f\"\\n\\n({len(users)} ta)\")"""
)

src = src.replace(
    """    await message.answer(
        f\"📋 <b>Ko'rib chiqish</b>\\n\\n\"
        f\"Maqsad: {label_map.get(target, target)}\\n\"
        f\"Oluvchilar: {count} kishi\\n\\n\"
        \"Yuborishni tasdiqlaysizmi?\",
        reply_markup=broadcast_confirm_kb(target, count),
    )""",
    """    lang = await get_lang(message.from_user.id)
    await message.answer(
        ta(\"broadcast_preview\", lang) + f\"\\n\\n({count} ta)\",
        reply_markup=broadcast_confirm_kb(target, count, lang=lang),
    )"""
)

src = src.replace(
    """    await callback.message.answer(
        f\"✅ <b>Xabar yuborildi!</b>\\n\\n\"
        f\"Muvaffaqiyatli: <b>{sent}</b>\\n\"
        f\"Xato: <b>{failed}</b>\",
        reply_markup=admin_back_kb(),
    )""",
    """    lang = await get_lang(callback.from_user.id)
    await callback.message.answer(
        ta(\"broadcast_done\", lang, ok=sent, fail=failed),
        reply_markup=admin_back_kb(lang=lang),
    )"""
)

with open("handlers/admin.py", "w", encoding="utf-8") as f:
    f.write(src)

print("Patch 2 done!")
