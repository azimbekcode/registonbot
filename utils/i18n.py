"""
Internationalization (i18n) for Registon bot.
Supports: uz (O'zbek), ru (Русский), en (English)
"""

TEXTS = {
    # ── Language selection ─────────────────────────────────────
    "choose_language": {
        "uz": "🌐 <b>Tilni tanlang:</b>",
        "ru": "🌐 <b>Выберите язык:</b>",
        "en": "🌐 <b>Choose language:</b>",
    },
    "language_changed": {
        "uz": "✅ Til o'zgartirildi: <b>O'zbek</b> 🇺🇿",
        "ru": "✅ Язык изменён: <b>Русский</b> 🇷🇺",
        "en": "✅ Language changed: <b>English</b> 🇬🇧",
    },

    # ── Settings ───────────────────────────────────────────────
    "settings_title": {
        "uz": "⚙️ <b>SOZLAMALAR</b>",
        "ru": "⚙️ <b>НАСТРОЙКИ</b>",
        "en": "⚙️ <b>SETTINGS</b>",
    },
    "settings_name": {
        "uz": "👤 Ism",
        "ru": "👤 Имя",
        "en": "👤 Name",
    },
    "settings_phone": {
        "uz": "📱 Telefon",
        "ru": "📱 Телефон",
        "en": "📱 Phone",
    },
    "settings_language": {
        "uz": "🌐 Til",
        "ru": "🌐 Язык",
        "en": "🌐 Language",
    },
    "settings_current_lang": {
        "uz": "O'zbek 🇺🇿",
        "ru": "Русский 🇷🇺",
        "en": "English 🇬🇧",
    },
    "settings_change_lang_btn": {
        "uz": "🌐 Tilni o'zgartirish",
        "ru": "🌐 Изменить язык",
        "en": "🌐 Change language",
    },

    # ── Main menu BUTTON LABELS ───────────────────────────────
    # These are the EXACT texts used in ReplyKeyboard buttons
    "btn_invite":         {"uz": "🎁 Do'st taklif qilish",  "ru": "🎁 Пригласить друга",   "en": "🎁 Invite Friends"},
    "btn_referrals":      {"uz": "🎯 Referrallarim",        "ru": "🎯 Мои рефералы",        "en": "🎯 My Referrals"},
    "btn_courses":        {"uz": "🎬 Bepul darslar",        "ru": "🎬 Бесплатные уроки",    "en": "🎬 Free Lessons"},
    "btn_profile":        {"uz": "👤 Profil",              "ru": "👤 Профиль",             "en": "👤 Profile"},
    "btn_stats":          {"uz": "📊 Statistika",           "ru": "📊 Статистика",           "en": "📊 Statistics"},
    "btn_settings":       {"uz": "⚙️ Sozlamalar",           "ru": "⚙️ Настройки",           "en": "⚙️ Settings"},
    "btn_contest":        {"uz": "🏆 Konkurs holati",       "ru": "🏆 Статус конкурса",     "en": "🏆 Contest Status"},
    "btn_contest_rules":  {"uz": "📋 Tanlov shartlari",     "ru": "📋 Условия конкурса",    "en": "📋 Contest Rules"},
    "btn_results":        {"uz": "🏅 Natijalar",            "ru": "🏅 Результаты",           "en": "🏅 Results"},
    "btn_register":       {"uz": "👉 Ro'yxatdan o'tish 👈","ru": "👉 Зарегистрироваться 👈","en": "👉 Register 👈"},
    "btn_cancel":         {"uz": "❌ Bekor qilish",         "ru": "❌ Отмена",               "en": "❌ Cancel"},
    "btn_send_phone":     {"uz": "📱 Raqamni yuborish",    "ru": "📱 Отправить номер",     "en": "📱 Send number"},
    "btn_mandatory_courses": {"uz": "🔐 Majburiy blok darslar", "ru": "🔐 Обязательные уроки", "en": "🔐 Mandatory lessons"},
    "btn_standard_courses":  {"uz": "📖 Darsliklar",            "ru": "📖 Уроки",                "en": "📖 Lessons"},

    # ── Welcome / Start ────────────────────────────────────────
    "main_menu": {
        "uz": "📋 Asosiy menyu:",
        "ru": "📋 Главное меню:",
        "en": "📋 Main menu:",
    },
    "welcome_registered": {
        "uz": "👋 Salom, <b>{name}</b>!\n\n🎯 Referal: {cur}/{req} {filled}{empty}\nQoldi: <b>{left} ta</b>\n\n📋 Asosiy menyu:",
        "ru": "👋 Привет, <b>{name}</b>!\n\n🎯 Рефералы: {cur}/{req} {filled}{empty}\nОсталось: <b>{left}</b>\n\n📋 Главное меню:",
        "en": "👋 Hello, <b>{name}</b>!\n\n🎯 Referrals: {cur}/{req} {filled}{empty}\nRemaining: <b>{left}</b>\n\n📋 Main menu:",
    },
    "welcome_contestant": {
        "uz": "👋 Salom, <b>{name}</b>!\n\n🏆 <b>Siz konkurs ishtirokchisisiz!</b>\nTaklif qilganlar: <b>{cur} ta</b>",
        "ru": "👋 Привет, <b>{name}</b>!\n\n🏆 <b>Вы участник конкурса!</b>\nПриглашений: <b>{cur}</b>",
        "en": "👋 Hello, <b>{name}</b>!\n\n🏆 <b>You are a contest participant!</b>\nInvited: <b>{cur}</b>",
    },
    "welcome_unreg": {
        "uz": "👋 Salom{name}!\n\n<b>Ustoz Ozodbek Qo'chqorov telegram botiga xush kelibsiz!</b>\n\n♻️ Tanlovda ishtirok etish uchun pastdagi\ntugmachani bosib, ro'yxatdan o'ting!",
        "ru": "👋 Привет{name}!\n\n<b>Добро пожаловать в телеграм-бот Учителя Озодбека Кочкорова!</b>\n\n♻️ Нажмите кнопку ниже, чтобы зарегистрироваться и участвовать в конкурсе!",
        "en": "👋 Hello{name}!\n\n<b>Welcome to Teacher Ozodbek Kochkorov's telegram bot!</b>\n\n♻️ Press the button below to register and join the contest!",
    },
    "channel_join_prompt": {
        "uz": "<b>Ustoz Ozodbek Qo'chqorov telegram botiga xush kelibsiz!</b>\n\n🔒 Botdan foydalanish uchun <b>{n} ta</b> kanalga a'zo bo'ling:\n\nA'zo bo'lgach <b>✅ A'zo bo'ldim</b> ni bosing.",
        "ru": "<b>Добро пожаловать в телеграм-бот Учителя Озодбеka Кочкорова!</b>\n\n🔒 Подпишитесь на <b>{n}</b> канал(а) для использования бота:\n\nПосле подписки нажмите <b>✅ Я подписался</b>.",
        "en": "<b>Welcome to Teacher Ozodbek Kochkorov's telegram bot!</b>\n\n🔒 Join <b>{n}</b> channel(s) to use the bot:\n\nAfter joining press <b>✅ I've subscribed</b>.",
    },
    "btn_subscribed":  {"uz": "✅ A'zo bo'ldim", "ru": "✅ Я подписался", "en": "✅ I've subscribed"},
    "not_subscribed":  {
        "uz": "❌ Hali {n} kanalga a'zo emassiz!",
        "ru": "❌ Вы ещё не подписались на {n} канал(а)!",
        "en": "❌ You haven't joined {n} channel(s) yet!",
    },

    # ── Profile ────────────────────────────────────────────────
    "profile_title": {
        "uz": "👤 <b>PROFIL</b>",
        "ru": "👤 <b>ПРОФИЛЬ</b>",
        "en": "👤 <b>PROFILE</b>",
    },
    "profile_fullname": {"uz": "📛 Ism-familya", "ru": "📛 Имя-фамилия", "en": "📛 Full name"},
    "profile_phone":    {"uz": "📱 Telefon",      "ru": "📱 Телефон",     "en": "📱 Phone"},
    "profile_contestant": {"uz": "🏆 Ishtirokchi","ru": "🏆 Участник",    "en": "🏆 Contestant"},
    "profile_reg_date": {"uz": "📆 Ro'yxat sanasi","ru": "📆 Дата регистрации","en": "📆 Registration date"},
    "yes": {"uz": "Ha ✅",  "ru": "Да ✅",  "en": "Yes ✅"},
    "no":  {"uz": "Yo'q",  "ru": "Нет",    "en": "No"},

    # ── Stats ──────────────────────────────────────────────────
    "stats_title": {
        "uz": "📊 <b>STATISTIKA</b>",
        "ru": "📊 <b>СТАТИСТИКА</b>",
        "en": "📊 <b>STATISTICS</b>",
    },
    "stats_invited":    {"uz": "👥 Taklif qilganlar", "ru": "👥 Приглашённые",    "en": "👥 Invited"},
    "stats_contestant": {"uz": "🏆 Ishtirokchi",       "ru": "🏆 Участник",         "en": "🏆 Contestant"},
    "stats_total":      {"uz": "🌍 Jami ishtirokchilar","ru": "🌍 Всего участников", "en": "🌍 Total contestants"},
    "stats_ref_link":   {"uz": "🔗 Referal havolangiz","ru": "🔗 Ваша реферальная ссылка","en": "🔗 Your referral link"},
    "not_yet":          {"uz": "Hali yo'q",             "ru": "Пока нет",              "en": "Not yet"},

    # ── Referrals ──────────────────────────────────────────────
    "referrals_title": {
        "uz": "👥 <b>Referallarim ({n} ta)</b>",
        "ru": "👥 <b>Мои рефералы ({n})</b>",
        "en": "👥 <b>My referrals ({n})</b>",
    },
    "referrals_empty": {
        "uz": "👥 <b>Referallarim</b>\n\nHali hech kim qo'shilmagan.",
        "ru": "👥 <b>Мои рефералы</b>\n\nПока никто не присоединился.",
        "en": "👥 <b>My referrals</b>\n\nNo one has joined yet.",
    },

    # ── Share / Invite ─────────────────────────────────────────
    "share_title": {
        "uz": "👥 <b>DO'ST QO'SHISH</b>",
        "ru": "👥 <b>ПРИГЛАСИТЬ ДРУГА</b>",
        "en": "👥 <b>INVITE FRIENDS</b>",
    },
    "share_desc": {
        "uz": "Konkursda qatnashish uchun <b>{req} ta</b> do'stingizni taklif qiling!",
        "ru": "Пригласите <b>{req}</b> друзей для участия в конкурсе!",
        "en": "Invite <b>{req}</b> friends to join the contest!",
    },
    "share_status": {
        "uz": "📊 Holat: {cur}/{req} {filled}{empty}\nQoldi: <b>{left} ta</b>",
        "ru": "📊 Статус: {cur}/{req} {filled}{empty}\nОсталось: <b>{left}</b>",
        "en": "📊 Status: {cur}/{req} {filled}{empty}\nRemaining: <b>{left}</b>",
    },
    "share_link":  {"uz": "🔗 Sizning havolangiz:", "ru": "🔗 Ваша ссылка:", "en": "🔗 Your link:"},
    "share_btn":   {"uz": "🔗 Havolani ulashish",   "ru": "🔗 Поделиться",  "en": "🔗 Share link"},

    # ── Contest ────────────────────────────────────────────────
    "contest_title": {
        "uz": "🏆 <b>KONKURS HOLATI</b>",
        "ru": "🏆 <b>СТАТУС КОНКУРСА</b>",
        "en": "🏆 <b>CONTEST STATUS</b>",
    },
    "contest_total":   {"uz": "Jami ishtirokchilar: <b>{n}</b>", "ru": "Всего участников: <b>{n}</b>", "en": "Total contestants: <b>{n}</b>"},
    "contest_my_refs": {"uz": "Sizning referallaringiz:",          "ru": "Ваши рефералы:",               "en": "Your referrals:"},
    "contest_none":    {"uz": "  Hali yo'q",                       "ru": "  Пока нет",                   "en": "  None yet"},

    # ── Registration ───────────────────────────────────────────
    "reg_start": {
        "uz": "📋 <b>RO'YXATDAN O'TISH</b>\n\n1️⃣ Ism va familyangizni kiriting:\n<i>(Masalan: Azimbek Abdusalomov)</i>",
        "ru": "📋 <b>РЕГИСТРАЦИЯ</b>\n\n1️⃣ Введите ваше имя и фамилию:\n<i>(Например: Иван Иванов)</i>",
        "en": "📋 <b>REGISTRATION</b>\n\n1️⃣ Enter your full name:\n<i>(Example: John Smith)</i>",
    },
    "reg_name_short":  {"uz": "❌ Ism juda qisqa. Qayta kiriting:", "ru": "❌ Имя слишком короткое. Введите заново:", "en": "❌ Name is too short. Try again:"},
    "reg_name_invalid":{"uz": "❌ Ism-familya faqat <b>harflardan</b> iborat bo'lishi kerak.\nRaqam yoki belgilar kiritish mumkin emas. Qayta urinib ko'ring:", "ru": "❌ ФИО должно состоять только из <b>букв</b>.\nЦифры и спецсимволы недопустимы. Попробуйте снова:", "en": "❌ Name must contain only <b>letters</b>.\nNumbers and symbols are not allowed. Try again:"},
    "reg_choose_prof": {"uz": "2️⃣ <b>Kasbingizni tanlang</b> yoki yozing:", "ru": "2️⃣ <b>Выберите профессию</b> или введите:", "en": "2️⃣ <b>Choose your profession</b> or type:"},
    "reg_confirm": {
        "uz": "✅ <b>Ma'lumotlaringiz:</b>\n\n👤 Ism-familya: <b>{name}</b>\n💼 Kasb: <b>{prof}</b>\n\n📱 Endi telefon raqamingizni tasdiqlang:",
        "ru": "✅ <b>Ваши данные:</b>\n\n👤 ФИО: <b>{name}</b>\n💼 Профессия: <b>{prof}</b>\n\n📱 Подтвердите ваш номер телефона:",
        "en": "✅ <b>Your info:</b>\n\n👤 Name: <b>{name}</b>\n💼 Profession: <b>{prof}</b>\n\n📱 Confirm your phone number:",
    },
    "reg_save_btn":    {"uz": "💾 Saqlash va davom etish", "ru": "💾 Сохранить и продолжить", "en": "💾 Save and continue"},
    "reg_redo_btn":    {"uz": "✏️ Qayta kiritish",         "ru": "✏️ Ввести заново",           "en": "✏️ Re-enter"},
    "reg_ask_phone": {
        "uz": "📱 Telefon raqamingizni tasdiqlang:\nPastdagi <b>\"📱 Raqamni yuborish\"</b> tugmasini bosing.",
        "ru": "📱 Подтвердите ваш номер телефона:\nНажмите кнопку <b>\"📱 Отправить номер\"</b> ниже.",
        "en": "📱 Confirm your phone number:\nPress the <b>\"📱 Send number\"</b> button below.",
    },
    "reg_phone_only": {
        "uz": "📱 Iltimos, faqat <b>\"📱 Raqamni yuborish\"</b> tugmasini bosing.",
        "ru": "📱 Пожалуйста, используйте только кнопку <b>\"📱 Отправить номер\"</b>.",
        "en": "📱 Please use only the <b>\"📱 Send number\"</b> button.",
    },
    "reg_uz_phone_only": {
        "uz": "❌ Faqat O'zbek telefon raqami qabul qilinadi (+998XXXXXXXXX).\nIltimos, O'zbekiston raqami bilan Telegram akkauntiga o'ting.",
        "ru": "❌ Принимаются только узбекские номера (+998XXXXXXXXX).\nПожалуйста, используйте аккаунт Telegram с узбекским номером.",
        "en": "❌ Only Uzbek phone numbers are accepted (+998XXXXXXXXX).\nPlease use a Telegram account with an Uzbek number.",
    },
    "reg_phone_taken": {
        "uz": "❌ Bu raqam allaqachon ro'yxatdan o'tgan.",
        "ru": "❌ Этот номер уже зарегистрирован.",
        "en": "❌ This number is already registered.",
    },
    "reg_success": {
        "uz": "✅ <b>Ro'yxatdan o'tdingiz!</b>\n\n👤 Ism: <b>{name}</b>\n💼 Kasb: <b>{prof}</b>\n📱 Raqam: {phone}\n\nQuyidagi menyudan foydalaning:",
        "ru": "✅ <b>Регистрация завершена!</b>\n\n👤 Имя: <b>{name}</b>\n💼 Профессия: <b>{prof}</b>\n📱 Номер: {phone}\n\nВоспользуйтесь меню ниже:",
        "en": "✅ <b>Registration complete!</b>\n\n👤 Name: <b>{name}</b>\n💼 Profession: <b>{prof}</b>\n📱 Number: {phone}\n\nUse the menu below:",
    },
    "reg_cancelled": {
        "uz": "❌ Ro'yxatdan o'tish bekor qilindi.",
        "ru": "❌ Регистрация отменена.",
        "en": "❌ Registration cancelled.",
    },

    # ── Courses ────────────────────────────────────────────────
    "courses_title": {
        "uz": "📚 <b>BEPUL DARSLIKLAR</b>\n\nKerakli darslikni tanlang:",
        "ru": "📚 <b>БЕСПЛАТНЫЕ УРОКИ</b>\n\nВыберите нужный урок:",
        "en": "📚 <b>FREE COURSES</b>\n\nChoose a course:",
    },
    "courses_empty": {
        "uz": "📚 Hozircha darsliklar mavjud emas.",
        "ru": "📚 Пока уроков нет.",
        "en": "📚 No courses available yet.",
    },

    # ── Errors ────────────────────────────────────────────────
    "not_registered": {
        "uz": "❌ Avval ro'yxatdan o'ting.",
        "ru": "❌ Сначала зарегистрируйтесь.",
        "en": "❌ Please register first.",
    },
}


def t(key: str, lang: str = "uz", **kwargs) -> str:
    """Get translated text. Falls back to 'uz' if key or lang missing."""
    lang = lang if lang in ("uz", "ru", "en") else "uz"
    entry = TEXTS.get(key, {})
    text = entry.get(lang) or entry.get("uz") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text


# ── All variants for each menu button (for F.text.in_() filters) ──

def all_btn(key: str) -> set:
    """Returns a set of all language variants for a button label."""
    entry = TEXTS.get(key, {})
    return {v for v in entry.values() if v}


# Pre-built sets for use in filters
BTN_INVITE         = all_btn("btn_invite")
BTN_REFERRALS      = all_btn("btn_referrals")
BTN_COURSES        = all_btn("btn_courses")
BTN_PROFILE        = all_btn("btn_profile")
BTN_STATS          = all_btn("btn_stats")
BTN_SETTINGS       = all_btn("btn_settings")
BTN_CONTEST        = all_btn("btn_contest")
BTN_CONTEST_RULES  = all_btn("btn_contest_rules")
BTN_RESULTS        = all_btn("btn_results")
BTN_REGISTER       = all_btn("btn_register")
BTN_CANCEL         = all_btn("btn_cancel")

def refresh_btn_sets(custom_labels: dict):
    """Adds custom labels from DB to the button sets."""
    mapping = {
        "label_btn_courses": BTN_COURSES,
        "label_btn_profile": BTN_PROFILE,
        "label_btn_invite": BTN_INVITE,
        "label_btn_contest_rules": BTN_CONTEST_RULES,
        "label_btn_results": BTN_RESULTS,
    }
    for key, val in custom_labels.items():
        if key in mapping and val:
            mapping[key].add(val)


# ── ADMIN PANEL TEXTS ─────────────────────────────────────────────

ADMIN_TEXTS = {
    # ── Main panel ─────────────────────────────────────────────
    "admin_title": {
        "uz": "⚙️ <b>ADMIN PANEL</b>\nRegiston O'quv Markaz Bot\n\n👥 Foydalanuvchilar: {total}\n✅ Ro'yxatdagilar: {registered}\n🏆 Ishtirokchilar: {contestants}\n📅 Bugun: {today}",
        "ru": "⚙️ <b>ADMIN PANEL</b>\nRegiston O'quv Markaz Bot\n\n👥 Пользователи: {total}\n✅ Зарегистрированы: {registered}\n🏆 Участники: {contestants}\n📅 Сегодня: {today}",
        "en": "⚙️ <b>ADMIN PANEL</b>\nRegiston O'quv Markaz Bot\n\n👥 Users: {total}\n✅ Registered: {registered}\n🏆 Contestants: {contestants}\n📅 Today: {today}",
    },
    "no_access":    {"uz": "❌ Ruxsat yo'q.",   "ru": "❌ Нет доступа.", "en": "❌ Access denied."},

    # ── Keyboard buttons ────────────────────────────────────────
    "btn_users":          {"uz": "👥 Foydalanuvchilar",          "ru": "👥 Пользователи",          "en": "👥 Users"},
    "btn_contestants":    {"uz": "🏆 Konkurs ishtirokchilari",   "ru": "🏆 Участники конкурса",    "en": "🏆 Contestants"},
    "btn_channels":       {"uz": "📢 Kanallar boshqaruvi",       "ru": "📢 Управление каналами",   "en": "📢 Channels"},
    "btn_admin_courses":  {"uz": "📚 Darsliklar boshqaruvi",     "ru": "📚 Управление уроками",    "en": "📚 Courses"},
    "btn_admin_stats":    {"uz": "📊 Statistika",                 "ru": "📊 Статистика",             "en": "📊 Statistics"},
    "btn_bot_settings":   {"uz": "⚙️ Bot sozlamalari",           "ru": "⚙️ Настройки бота",        "en": "⚙️ Bot settings"},
    "btn_broadcast":      {"uz": "📣 Xabar yuborish",             "ru": "📣 Рассылка",               "en": "📣 Broadcast"},
    "btn_admins":         {"uz": "👮 Adminlar boshqaruvi",       "ru": "👮 Управление админами",    "en": "👮 Admins"},
    "btn_db_viewer":      {"uz": "🗄️ Database ko'rish",          "ru": "🗄️ Просмотр БД",           "en": "🗄️ Database viewer"},
    "btn_back_admin":     {"uz": "🔙 Admin panel",                "ru": "🔙 Админ панель",           "en": "🔙 Admin panel"},
    "btn_back":           {"uz": "🔙 Orqaga",                     "ru": "🔙 Назад",                  "en": "🔙 Back"},
    "btn_search_user":    {"uz": "🔍 Foydalanuvchi qidirish",    "ru": "🔍 Поиск пользователя",    "en": "🔍 Search user"},
    "btn_export_users":   {"uz": "📋 Ro'yxatni yuklab olish",    "ru": "📋 Скачать список",         "en": "📋 Export users"},
    "btn_add_channel":    {"uz": "➕ Kanal qo'shish",             "ru": "➕ Добавить канал",         "en": "➕ Add channel"},
    "btn_add_course":     {"uz": "➕ Darslik qo'shish",           "ru": "➕ Добавить урок",          "en": "➕ Add course"},
    "btn_add_admin":      {"uz": "➕ Admin qo'shish",             "ru": "➕ Добавить администратора","en": "➕ Add admin"},
    "btn_ban":            {"uz": "🚫 Ban",                        "ru": "🚫 Заблокировать",          "en": "🚫 Ban"},
    "btn_unban":          {"uz": "✅ Ban ochish",                  "ru": "✅ Разблокировать",          "en": "✅ Unban"},
    "btn_delete_user":    {"uz": "🗑️ O'chirish",                 "ru": "🗑️ Удалить",               "en": "🗑️ Delete"},
    "btn_yes_delete":     {"uz": "✅ Ha, o'chirish",               "ru": "✅ Да, удалить",             "en": "✅ Yes, delete"},
    "btn_cancel_action":  {"uz": "❌ Bekor",                       "ru": "❌ Отмена",                  "en": "❌ Cancel"},
    "btn_confirm_yes":    {"uz": "✅ Ha",                           "ru": "✅ Да",                      "en": "✅ Yes"},
    "btn_confirm_no":     {"uz": "❌ Yo'q",                        "ru": "❌ Нет",                     "en": "❌ No"},
    "btn_db_menu":        {"uz": "🔙 Database menyusi",            "ru": "🔙 Меню БД",                "en": "🔙 DB menu"},
    "btn_prev":           {"uz": "◀️ Oldingi",                     "ru": "◀️ Назад",                  "en": "◀️ Prev"},
    "btn_next":           {"uz": "Keyingi ▶️",                     "ru": "Вперёд ▶️",                 "en": "Next ▶️"},
    "btn_full_report":    {"uz": "📥 To'liq hisobot (.txt)",       "ru": "📥 Полный отчёт (.txt)",    "en": "📥 Full report (.txt)"},
    "btn_welcome_msg":    {"uz": "✉️ Xush kelibsiz xabarni o'zgartirish","ru": "✉️ Изменить приветствие","en": "✉️ Welcome message"},
    "btn_broadcast_all":  {"uz": "👥 Hammaga",                     "ru": "👥 Всем",                   "en": "👥 Everyone"},
    "btn_broadcast_reg":  {"uz": "✅ Ro'yxatdagilarga",            "ru": "✅ Зарегистрированным",     "en": "✅ Registered"},
    "btn_broadcast_cont": {"uz": "🏆 Ishtirokchilarga",            "ru": "🏆 Участникам",             "en": "🏆 Contestants"},
    "btn_broadcast_unreg":{"uz": "⏳ Ro'yxatdan o'tmaganlarga",   "ru": "⏳ Незарегистрированным",  "en": "⏳ Unregistered"},
    "btn_broadcast_send": {"uz": "✅ Yuborish — {n} kishi",        "ru": "✅ Отправить — {n} чел.",   "en": "✅ Send — {n} users"},
    "btn_search_phone":   {"uz": "📱 Telefon raqam",               "ru": "📱 Номер телефона",         "en": "📱 Phone number"},
    "btn_search_username":{"uz": "👤 Username (@...)",             "ru": "👤 Юзернейм (@...)",        "en": "👤 Username (@...)"},
    "btn_search_name":    {"uz": "🏷️ Ism bo'yicha",               "ru": "🏷️ По имени",              "en": "🏷️ By name"},
    "btn_search_id":      {"uz": "🆔 Telegram ID",                 "ru": "🆔 Telegram ID",            "en": "🆔 Telegram ID"},
    "btn_search_all":     {"uz": "🔍 Barchasi bo'yicha",           "ru": "🔍 По всем полям",          "en": "🔍 Search all"},
    "contest_active":     {"uz": "✅ Faol",   "ru": "✅ Активен",  "en": "✅ Active"},
    "contest_off":        {"uz": "❌ O'chiq", "ru": "❌ Выключен", "en": "❌ Off"},
    "reg_open":           {"uz": "✅ Ochiq",  "ru": "✅ Открыта",  "en": "✅ Open"},
    "reg_closed":         {"uz": "❌ Yopiq",  "ru": "❌ Закрыта",  "en": "❌ Closed"},
    "btn_contest_label":  {"uz": "🏆 Konkurs: {status}",           "ru": "🏆 Конкурс: {status}",      "en": "🏆 Contest: {status}"},
    "btn_reg_label":      {"uz": "📝 Ro'yxat: {status}",           "ru": "📝 Регистрация: {status}",  "en": "📝 Registration: {status}"},
    "btn_ref_count":      {"uz": "🔢 Referal talabi: {n} ta",      "ru": "🔢 Рефералов нужно: {n}",  "en": "🔢 Referrals needed: {n}"},

    # ── User info ──────────────────────────────────────────────
    "user_detail": {
        "uz": "👤 <b>FOYDALANUVCHI MA'LUMOTI</b>\n\n🔢 Tartib raqami: <b>{index}</b>\n🆔 Telegram ID: <code>{id}</code>\n👤 Ism: {name}\n📱 Telefon: {phone}\n💼 Kasb: {prof}\n🔗 Username: {uname}\n📅 Qo'shilgan: {joined}\n📝 Ro'yxat: {reg_at}\n\n🏆 Ishtirokchi: {contestant}\n👥 Referallar: {refs}\n🚫 Ban: {banned}",
        "ru": "👤 <b>ДАННЫЕ ПОЛЬЗОВАТЕЛЯ</b>\n\n🔢 Порядковый номер: <b>{index}</b>\n🆔 Telegram ID: <code>{id}</code>\n👤 Имя: {name}\n📱 Телефон: {phone}\n💼 Профессия: {prof}\n🔗 Юзернейм: {uname}\n📅 Присоединился: {joined}\n📝 Регистрация: {reg_at}\n\n🏆 Участник: {contestant}\n👥 Рефералы: {refs}\n🚫 Бан: {banned}",
        "en": "👤 <b>USER INFO</b>\n\n🔢 Sequential ID: <b>{index}</b>\n🆔 Telegram ID: <code>{id}</code>\n👤 Name: {name}\n📱 Phone: {phone}\n💼 Profession: {prof}\n🔗 Username: {uname}\n📅 Joined: {joined}\n📝 Registered: {reg_at}\n\n🏆 Contestant: {contestant}\n👥 Referrals: {refs}\n🚫 Banned: {banned}",
    },
    "delete_confirm": {
        "uz": "⚠️ <b>FOYDALANUVCHINI O'CHIRISH</b>\n\n👤 {name}\n📱 {phone}\n\n❗️ Bu amalni bekor qilib bo'lmaydi!\nFoydalanuvchi va uning barcha ma'lumotlari o'chib ketadi.",
        "ru": "⚠️ <b>УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ</b>\n\n👤 {name}\n📱 {phone}\n\n❗️ Это действие нельзя отменить!\nПользователь и все его данные будут удалены.",
        "en": "⚠️ <b>DELETE USER</b>\n\n👤 {name}\n📱 {phone}\n\n❗️ This cannot be undone!\nAll data will be permanently deleted.",
    },
    "user_deleted":         {"uz": "✅ Foydalanuvchi o'chirildi.",    "ru": "✅ Пользователь удалён.",      "en": "✅ User deleted."},
    "user_banned":          {"uz": "🚫 Foydalanuvchi banlandi.",      "ru": "🚫 Пользователь заблокирован.","en": "🚫 User banned."},
    "user_unbanned":        {"uz": "✅ Foydalanuvchi banidan chiqdi.","ru": "✅ Пользователь разблокирован.","en": "✅ User unbanned."},
    "user_not_found":       {"uz": "❌ Foydalanuvchi topilmadi.",     "ru": "❌ Пользователь не найден.",   "en": "❌ User not found."},
    "search_prompt":        {"uz": "🔍 Qidiruv so'rovini kiriting:",  "ru": "🔍 Введите запрос поиска:",    "en": "🔍 Enter search query:"},
    "search_no_results":    {"uz": "❌ Hech narsa topilmadi.",         "ru": "❌ Ничего не найдено.",         "en": "❌ No results found."},

    # ── Stats ──────────────────────────────────────────────────
    "admin_stats": {
        "uz": "📊 <b>BOT STATISTIKASI</b>\n\n👥 Jami: {total}\n✅ Ro'yxatdagilar: {registered}\n🏆 Ishtirokchilar: {contestants}\n⏳ Kutayotganlar: {pending}\n🚫 Banlangan: {banned}\n📅 Bugun: {today}",
        "ru": "📊 <b>СТАТИСТИКА БОТА</b>\n\n👥 Всего: {total}\n✅ Зарегистрированы: {registered}\n🏆 Участники: {contestants}\n⏳ Ожидающие: {pending}\n🚫 Заблокированы: {banned}\n📅 Сегодня: {today}",
        "en": "📊 <b>BOT STATISTICS</b>\n\n👥 Total: {total}\n✅ Registered: {registered}\n🏆 Contestants: {contestants}\n⏳ Pending: {pending}\n🚫 Banned: {banned}\n📅 Today: {today}",
    },
    "contestants_list":     {"uz": "🏆 <b>Konkurs Ishtirokchilari</b> ({n} ta)\n","ru": "🏆 <b>Участники конкурса</b> ({n})\n","en": "🏆 <b>Contest Participants</b> ({n})\n"},
    "contestants_empty":    {"uz": "🏆 Hozircha ishtirokchilar yo'q.", "ru": "🏆 Участников пока нет.","en": "🏆 No contestants yet."},

    # ── Broadcast ──────────────────────────────────────────────
    "broadcast_write":      {"uz": "📣 Yubormoqchi bo'lgan xabaringizni yozing:", "ru": "📣 Напишите сообщение для рассылки:", "en": "📣 Write the broadcast message:"},
    "broadcast_preview":    {"uz": "👆 Xabar shunday ko'rinadi.\n\nKimga yuborilsin?", "ru": "👆 Сообщение выглядит так.\n\nКому отправить?", "en": "👆 Here's the message preview.\n\nWho to send to?"},
    "broadcast_done":       {"uz": "✅ Xabar yuborildi!\n✅ Muvaffaqiyatli: {ok}\n❌ Xatolik: {fail}", "ru": "✅ Рассылка завершена!\n✅ Успешно: {ok}\n❌ Ошибок: {fail}", "en": "✅ Broadcast done!\n✅ Sent: {ok}\n❌ Failed: {fail}"},

    # ── Channels ───────────────────────────────────────────────
    "channel_add_prompt":   {"uz": "📢 Kanal username yoki ID ni kiriting:", "ru": "📢 Введите username или ID канала:", "en": "📢 Enter channel username or ID:"},
    "channel_added":        {"uz": "✅ Kanal qo'shildi: {ch}",   "ru": "✅ Канал добавлен: {ch}",  "en": "✅ Channel added: {ch}"},
    "channel_deleted":      {"uz": "🗑 Kanal o'chirildi.",        "ru": "🗑 Канал удалён.",          "en": "🗑 Channel deleted."},
    "channel_toggled":      {"uz": "✅ Holat o'zgartirildi.",     "ru": "✅ Статус изменён.",        "en": "✅ Status changed."},
    "channels_empty":       {"uz": "📢 Kanallar yo'q.",           "ru": "📢 Каналов нет.",           "en": "📢 No channels."},

    # ── Courses ────────────────────────────────────────────────
    "course_add_title":     {"uz": "📚 Darslik nomini kiriting:",      "ru": "📚 Введите название урока:", "en": "📚 Enter course title:"},
    "course_add_desc":      {"uz": "✍️ Darslik tavsifini kiriting:",  "ru": "✍️ Введите описание:",       "en": "✍️ Enter description:"},
    "course_add_forward":   {"uz": "📩 Kanaldan xabarni forward qiling:", "ru": "📩 Перешлите сообщение:", "en": "📩 Forward a message:"},
    "course_added":         {"uz": "✅ Darslik qo'shildi: {title}",   "ru": "✅ Урок добавлен: {title}",  "en": "✅ Course added: {title}"},
    "course_deleted":       {"uz": "🗑 Darslik o'chirildi.",           "ru": "🗑 Урок удалён.",             "en": "🗑 Course deleted."},
    "courses_empty":        {"uz": "📚 Darsliklar yo'q.",              "ru": "📚 Уроков нет.",              "en": "📚 No courses."},

    # ── Settings ───────────────────────────────────────────────
    "set_ref_prompt":       {"uz": "🔢 Yangi referal talabini kiriting (raqam):", "ru": "🔢 Введите новое требование (число):", "en": "🔢 Enter new requirement (number):"},
    "set_ref_done":         {"uz": "✅ Referal talabi {n} ga o'zgartirildi.", "ru": "✅ Требование изменено на {n}.", "en": "✅ Changed to {n}."},
    "set_welcome_prompt":   {"uz": "✉️ Yangi xush kelibsiz xabarni kiriting:", "ru": "✉️ Введите новое приветствие:", "en": "✉️ Enter new welcome message:"},
    "set_welcome_done":     {"uz": "✅ Xabar yangilandi.", "ru": "✅ Сообщение обновлено.", "en": "✅ Message updated."},

    # ── Admins ─────────────────────────────────────────────────
    "admin_add_prompt":         {"uz": "👮 Yangi admin Telegram ID sini kiriting:", "ru": "👮 Введите Telegram ID нового админа:", "en": "👮 Enter new admin's Telegram ID:"},
    "admin_added":              {"uz": "✅ Admin qo'shildi.",                  "ru": "✅ Администратор добавлен.",  "en": "✅ Admin added."},
    "admin_removed":            {"uz": "🗑 Admin o'chirildi.",                 "ru": "🗑 Администратор удалён.",    "en": "🗑 Admin removed."},
    "admin_not_found":          {"uz": "❌ Admin topilmadi.",                  "ru": "❌ Администратор не найден.", "en": "❌ Admin not found."},
    "superadmin_protected":     {"uz": "❌ Superadmini o'chirib bo'lmaydi.",  "ru": "❌ Нельзя удалить суперадмина.", "en": "❌ Cannot remove superadmin."},
}


def ta(key: str, lang: str = "uz", **kwargs) -> str:
    """Get admin panel translated text. Falls back to 'uz'."""
    lang = lang if lang in ("uz", "ru", "en") else "uz"
    entry = ADMIN_TEXTS.get(key, {})
    text = entry.get(lang) or entry.get("uz") or key
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text



