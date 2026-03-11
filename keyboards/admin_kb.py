"""
Admin panel keyboard builders — multilingual via i18n.
"""

from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from utils.i18n import ta


def admin_main_kb(is_superadmin: bool = False, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=ta("btn_users", lang),         callback_data="admin_users"))
    builder.row(InlineKeyboardButton(text=ta("btn_contestants", lang),   callback_data="admin_contestants"))
    builder.row(InlineKeyboardButton(text="🏆 Konkurs IDlar & G'olib",   callback_data="admin_contest_ids"))
    builder.row(InlineKeyboardButton(text="📊 Referral reytingi",        callback_data="admin_ref_leaderboard"))
    builder.row(InlineKeyboardButton(text=ta("btn_channels", lang),      callback_data="admin_channels"))
    builder.row(InlineKeyboardButton(text=ta("btn_admin_courses", lang), callback_data="admin_courses"))
    builder.row(InlineKeyboardButton(text=ta("btn_admin_stats", lang),   callback_data="admin_stats"))
    builder.row(InlineKeyboardButton(text=ta("btn_bot_settings", lang),  callback_data="admin_settings"))
    builder.row(InlineKeyboardButton(text=ta("btn_broadcast", lang),     callback_data="admin_broadcast"))
    if is_superadmin:
        builder.row(InlineKeyboardButton(text=ta("btn_admins", lang),    callback_data="admin_admins"))
        builder.row(InlineKeyboardButton(text=ta("btn_db_viewer", lang), callback_data="sa_db_viewer"))
    return builder.as_markup()


def admin_back_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=ta("btn_back_admin", lang), callback_data="back_to_admin"))
    return builder.as_markup()


# ── USERS ──────────────────────────────────────────────────────

def users_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👥 Barcha foydalanuvchilarni ko'rish", callback_data="admin_all_users_0"))
    builder.row(InlineKeyboardButton(text=ta("btn_search_user", lang),  callback_data="admin_user_search"))
    builder.row(InlineKeyboardButton(text=ta("btn_export_users", lang), callback_data="admin_export_users"))
    builder.row(InlineKeyboardButton(text=ta("btn_back_admin", lang),   callback_data="back_to_admin"))
    return builder.as_markup()


def search_method_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=ta("btn_search_phone", lang),   callback_data="search_by_phone"))
    builder.row(InlineKeyboardButton(text=ta("btn_search_username", lang),callback_data="search_by_username"))
    builder.row(InlineKeyboardButton(text=ta("btn_search_name", lang),    callback_data="search_by_name"))
    builder.row(InlineKeyboardButton(text=ta("btn_search_id", lang),      callback_data="search_by_id"))
    builder.row(InlineKeyboardButton(text=ta("btn_search_all", lang),     callback_data="search_by_all"))
    builder.row(InlineKeyboardButton(text=ta("btn_back", lang),           callback_data="admin_users"))
    return builder.as_markup()


def user_detail_kb(telegram_id: int, is_banned: bool, is_superadmin: bool = False, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_banned:
        builder.row(InlineKeyboardButton(text=ta("btn_unban", lang), callback_data=f"admin_unban_{telegram_id}"))
    else:
        builder.row(InlineKeyboardButton(text=ta("btn_ban", lang),   callback_data=f"admin_ban_{telegram_id}"))
    if is_superadmin:
        builder.row(InlineKeyboardButton(text=ta("btn_delete_user", lang), callback_data=f"admin_delete_user_{telegram_id}"))
    builder.row(InlineKeyboardButton(text=ta("btn_back", lang), callback_data="admin_users"))
    return builder.as_markup()


def confirm_delete_user_kb(telegram_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=ta("btn_yes_delete", lang),    callback_data=f"admin_confirm_delete_{telegram_id}"),
        InlineKeyboardButton(text=ta("btn_cancel_action", lang), callback_data=f"admin_view_user_{telegram_id}"),
    )
    return builder.as_markup()


# ── CHANNELS ───────────────────────────────────────────────────

def channels_kb(channels: list, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        status = "✅" if ch["is_active"] else "❌"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {ch['channel_title'] or ch['channel_id']}",
                callback_data=f"admin_ch_toggle_{ch['id']}_{1 if not ch['is_active'] else 0}",
            ),
            InlineKeyboardButton(text="🗑", callback_data=f"admin_ch_delete_{ch['channel_id']}"),
        )
    builder.row(InlineKeyboardButton(text=ta("btn_add_channel", lang), callback_data="admin_ch_add"))
    builder.row(InlineKeyboardButton(text=ta("btn_back_admin", lang),  callback_data="back_to_admin"))
    return builder.as_markup()


# ── COURSES ────────────────────────────────────────────────────

def courses_admin_kb(courses: list, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for course in courses:
        status = "✅" if course["is_active"] else "❌"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {course['title'][:30]}",
                callback_data=f"admin_course_toggle_{course['id']}_{1 if not course['is_active'] else 0}",
            ),
            InlineKeyboardButton(text="🗑", callback_data=f"admin_course_delete_{course['id']}"),
        )
    builder.row(InlineKeyboardButton(text=ta("btn_add_course", lang), callback_data="admin_course_add"))
    builder.row(InlineKeyboardButton(text=ta("btn_back_admin", lang), callback_data="back_to_admin"))
    return builder.as_markup()


# ── SETTINGS ───────────────────────────────────────────────────

def settings_kb(settings: dict, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    contest_active = settings.get("contest_active", "1") == "1"
    reg_open = settings.get("registration_open", "1") == "1"
    req_ref = settings.get("required_referrals", "5")

    contest_status = ta("contest_active", lang) if contest_active else ta("contest_off", lang)
    reg_status = ta("reg_open", lang) if reg_open else ta("reg_closed", lang)
    contest_next = 0 if contest_active else 1
    reg_next = 0 if reg_open else 1

    builder.row(InlineKeyboardButton(
        text=ta("btn_contest_label", lang, status=contest_status),
        callback_data=f"admin_set_contest_{contest_next}",
    ))
    builder.row(InlineKeyboardButton(
        text=ta("btn_reg_label", lang, status=reg_status),
        callback_data=f"admin_set_reg_{reg_next}",
    ))
    builder.row(InlineKeyboardButton(
        text=ta("btn_ref_count", lang, n=req_ref),
        callback_data="admin_set_ref_count",
    ))
    builder.row(InlineKeyboardButton(
        text=ta("btn_welcome_msg", lang),
        callback_data="admin_set_welcome",
    ))
    
    # Lesson category toggles
    std_active = settings.get("standard_lessons_active", "1") == "1"
    man_active = settings.get("mandatory_lessons_active", "1") == "1"
    
    std_icon = "✅" if std_active else "❌"
    man_icon = "✅" if man_active else "❌"
    
    builder.row(
        InlineKeyboardButton(text=f"{std_icon} Standart darsliklar", callback_data=f"admin_set_std_lessons_{0 if std_active else 1}"),
        InlineKeyboardButton(text=f"{man_icon} Majburiy blok", callback_data=f"admin_set_man_lessons_{0 if man_active else 1}"),
    )
    
    builder.row(InlineKeyboardButton(
        text="🎨 Tugma va Matnlar sozlamalari",
        callback_data="admin_interface_settings",
    ))
    builder.row(InlineKeyboardButton(text=ta("btn_back_admin", lang), callback_data="back_to_admin"))
    return builder.as_markup()


def interface_settings_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    # Buttons
    builder.row(InlineKeyboardButton(text="🔘 'Bepul darslar' nomi", callback_data="admin_set_lb_courses"))
    builder.row(InlineKeyboardButton(text="🔘 'Profil' nomi", callback_data="admin_set_lb_profile"))
    builder.row(InlineKeyboardButton(text="🔘 'Taklif qilish' nomi", callback_data="admin_set_lb_invite"))
    builder.row(InlineKeyboardButton(text="🔘 'Tanlov' nomi", callback_data="admin_set_lb_rules"))
    builder.row(InlineKeyboardButton(text="🔘 'Natijalar' nomi", callback_data="admin_set_lb_results"))
    
    builder.row(
        InlineKeyboardButton(text="🔘 'Majburiy' nomi", callback_data="admin_set_lb_mandatory"),
        InlineKeyboardButton(text="🔘 'Darsliklar' nomi", callback_data="admin_set_lb_standard")
    )
    
    # Texts
    builder.row(InlineKeyboardButton(text="📝 Profil matni", callback_data="admin_set_txt_profile"))
    builder.row(InlineKeyboardButton(text="📝 Natijalar matni", callback_data="admin_set_txt_results"))
    builder.row(InlineKeyboardButton(text="📝 Darsliklar bosh matni", callback_data="admin_set_txt_courses_main"))
    builder.row(InlineKeyboardButton(text="📝 Standart darslar matni", callback_data="admin_set_txt_courses_std"))
    builder.row(InlineKeyboardButton(text="📝 Majburiy darslar matni", callback_data="admin_set_txt_courses_man"))
    builder.row(InlineKeyboardButton(text="📩 Taklif qilish matni", callback_data="admin_set_txt_invite"))
    builder.row(InlineKeyboardButton(text="📋 Tanlov shartlari matni", callback_data="admin_set_txt_rules"))
    
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="admin_settings"))
    return builder.as_markup()


# ── ADMINS ─────────────────────────────────────────────────────

def admins_kb(admins: list, superadmin_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for adm in admins:
        name = adm["full_name"] or adm["username"] or str(adm["telegram_id"])
        role_emoji = "👑" if adm["role"] == "superadmin" else "👮"
        row_buttons = [InlineKeyboardButton(
            text=f"{role_emoji} {name[:20]}",
            callback_data=f"admin_adm_view_{adm['telegram_id']}",
        )]
        if adm["telegram_id"] != superadmin_id:
            row_buttons.append(InlineKeyboardButton(
                text="🗑",
                callback_data=f"admin_adm_remove_{adm['telegram_id']}",
            ))
        builder.row(*row_buttons)
    builder.row(InlineKeyboardButton(text=ta("btn_add_admin", lang),  callback_data="admin_adm_add"))
    builder.row(InlineKeyboardButton(text=ta("btn_back_admin", lang), callback_data="back_to_admin"))
    return builder.as_markup()


# ── BROADCAST ──────────────────────────────────────────────────

def broadcast_target_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=ta("btn_broadcast_all", lang),  callback_data="broadcast_all"))
    builder.row(InlineKeyboardButton(text=ta("btn_broadcast_reg", lang),  callback_data="broadcast_registered"))
    builder.row(InlineKeyboardButton(text=ta("btn_broadcast_cont", lang), callback_data="broadcast_contestants"))
    builder.row(InlineKeyboardButton(text=ta("btn_broadcast_unreg", lang),callback_data="broadcast_unregistered"))
    builder.row(InlineKeyboardButton(text=ta("btn_cancel_action", lang),  callback_data="back_to_admin"))
    return builder.as_markup()


def broadcast_confirm_kb(target: str, count: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text=ta("btn_broadcast_send", lang, n=count),
        callback_data=f"broadcast_confirm_{target}",
    ))
    builder.row(InlineKeyboardButton(text=ta("btn_cancel_action", lang), callback_data="back_to_admin"))
    return builder.as_markup()


def confirm_action_kb(yes_data: str, no_data: str, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=ta("btn_confirm_yes", lang), callback_data=yes_data),
        InlineKeyboardButton(text=ta("btn_confirm_no", lang),  callback_data=no_data),
    )
    return builder.as_markup()


# ── DATABASE VIEWER (SUPERADMIN) ───────────────────────────────

def db_viewer_main_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👥 Users jadvali",          callback_data="sa_db_users"))
    builder.row(InlineKeyboardButton(text="👮 Admins jadvali",          callback_data="sa_db_admins"))
    builder.row(InlineKeyboardButton(text="📢 Channels jadvali",        callback_data="sa_db_channels"))
    builder.row(InlineKeyboardButton(text="📚 Courses jadvali",         callback_data="sa_db_courses"))
    builder.row(InlineKeyboardButton(text="🔗 Referals jadvali",        callback_data="sa_db_referrals"))
    builder.row(InlineKeyboardButton(text="🏆 Contest Participants",    callback_data="sa_db_contest"))
    builder.row(InlineKeyboardButton(text="⚙️ Bot Settings jadvali",   callback_data="sa_db_settings"))
    builder.row(InlineKeyboardButton(text=ta("btn_full_report", lang),  callback_data="sa_db_export_full"))
    builder.row(InlineKeyboardButton(text=ta("btn_back_admin", lang),   callback_data="back_to_admin"))
    return builder.as_markup()


def db_viewer_back_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=ta("btn_db_menu", lang), callback_data="sa_db_viewer"))
    return builder.as_markup()


def db_users_page_kb(page: int, total_pages: int, lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text=ta("btn_prev", lang), callback_data=f"sa_db_users_p_{page - 1}"
        ))
    nav_buttons.append(InlineKeyboardButton(
        text=f"{page + 1}/{total_pages}", callback_data="noop"
    ))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            text=ta("btn_next", lang), callback_data=f"sa_db_users_p_{page + 1}"
        ))
    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text=ta("btn_db_menu", lang), callback_data="sa_db_viewer"))
    return builder.as_markup()


def db_users_page_with_delete_kb(
    page: int, total_pages: int, user_ids: list, lang: str = "uz"
) -> InlineKeyboardMarkup:
    """DB viewer users sahifasi — har bir foydalanuvchi yonida o'chirish tugmasi."""
    builder = InlineKeyboardBuilder()
    for tid in user_ids:
        builder.row(
            InlineKeyboardButton(
                text=f"🆔 {tid}",
                callback_data="noop",
            ),
            InlineKeyboardButton(
                text="🗑️ O'chir",
                callback_data=f"sa_del_user_{tid}",
            ),
        )
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(
            text=ta("btn_prev", lang), callback_data=f"sa_db_users_p_{page - 1}"
        ))
    nav_buttons.append(InlineKeyboardButton(
        text=f"{page + 1}/{total_pages}", callback_data="noop"
    ))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(
            text=ta("btn_next", lang), callback_data=f"sa_db_users_p_{page + 1}"
        ))
    if nav_buttons:
        builder.row(*nav_buttons)
    builder.row(InlineKeyboardButton(text=ta("btn_db_menu", lang), callback_data="sa_db_viewer"))
    return builder.as_markup()


# ── CONTEST IDs & RANDOM WINNER ───────────────────────────────────

def contest_ids_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎲 Random g'olibni aniqlash", callback_data="admin_pick_winner"))
    builder.row(InlineKeyboardButton(text="📥 IDlarni fayl sifatida yuklab olish", callback_data="admin_export_contest_ids"))
    builder.row(InlineKeyboardButton(text=ta("btn_back_admin", lang), callback_data="back_to_admin"))
    return builder.as_markup()


# ── REFERRAL LEADERBOARD ──────────────────────────────────────────

def ref_leaderboard_admin_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="10 ta",  callback_data="admin_ref_lb_10"),
        InlineKeyboardButton(text="20 ta",  callback_data="admin_ref_lb_20"),
        InlineKeyboardButton(text="50 ta",  callback_data="admin_ref_lb_50"),
        InlineKeyboardButton(text="100 ta", callback_data="admin_ref_lb_100"),
    )
    builder.row(InlineKeyboardButton(text=ta("btn_back_admin", lang), callback_data="back_to_admin"))
    return builder.as_markup()


# ── USER REFERRAL LEADERBOARD LIMIT ──────────────────────────────

def user_ref_leaderboard_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Foydalanuvchi uchun referral reytingini ko'rish tugmalari."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🌐 Hammasi", callback_data="user_ref_lb_all_options"),
    )
    return builder.as_markup()


def user_ref_lb_options_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    """Hammasi bosilganda chiqadigan limit tanlash tugmalari."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="10 talab",  callback_data="user_ref_lb_10"),
        InlineKeyboardButton(text="20 talab",  callback_data="user_ref_lb_20"),
    )
    builder.row(
        InlineKeyboardButton(text="50 talab",  callback_data="user_ref_lb_50"),
        InlineKeyboardButton(text="100 talab", callback_data="user_ref_lb_100"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Barchasi", callback_data="user_ref_lb_all"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_results"),
    )
    return builder.as_markup()
