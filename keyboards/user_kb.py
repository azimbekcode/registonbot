"""
User-facing keyboard builders for Registon O'quv Markaz bot.
Supports multilingual (uz/ru/en) via i18n.
"""

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from utils.i18n import t


# ── Channel subscription ───────────────────────────────────────

def channel_check_kb(channels: list, lang: str = "uz") -> InlineKeyboardMarkup:
    """Inline buttons to open channels + check subscription."""
    builder = InlineKeyboardBuilder()
    for ch in channels:
        ch_id = ch["channel_id"]
        title = ch["channel_title"] or ch_id
        if ch_id.startswith("@"):
            link = f"https://t.me/{ch_id[1:]}"
        else:
            link = f"https://t.me/c/{str(ch_id).replace('-100', '')}"
        builder.row(InlineKeyboardButton(text=f"📢 {title}", url=link))
    builder.row(
        InlineKeyboardButton(text=t("btn_subscribed", lang), callback_data="check_subscription")
    )
    return builder.as_markup()


# ── Registration prompt (ReplyKeyboard — bottom bar) ──────────

def reg_prompt_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Single 'Register' button shown at bottom."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=t("btn_register", lang)))
    return builder.as_markup(resize_keyboard=True)


# ── Phone request (ReplyKeyboard — contact only) ───────────────

def phone_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Only contact-share button — no manual input."""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=t("btn_send_phone", lang), request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


# ── Main menu (ReplyKeyboard — bottom bar) ─────────────────────

def main_menu_kb(
    is_registered: bool = False,
    is_contestant: bool = False,
    lang: str = "uz",
    labels: dict = None,
) -> ReplyKeyboardMarkup:
    """Main menu as ReplyKeyboard shown in the bottom bar."""
    builder = ReplyKeyboardBuilder()
    if labels is None: labels = {}

    def get_lb(key, fallback_key):
        return labels.get(f"label_{key}") or t(fallback_key, lang)

    if not is_registered:
        builder.row(KeyboardButton(text=t("btn_register", lang)))
    else:
        # Bepul darslar — yuqorida yagona tugma
        builder.row(KeyboardButton(text=get_lb("btn_courses", "btn_courses")))
        # Profil | Do'st taklif qilish
        builder.row(
            KeyboardButton(text=get_lb("btn_profile", "btn_profile")),
            KeyboardButton(text=get_lb("btn_invite", "btn_invite")),
        )
        # Tanlov shartlari | Natijalar
        builder.row(
            KeyboardButton(text=get_lb("btn_contest_rules", "btn_contest_rules")),
            KeyboardButton(text=get_lb("btn_results", "btn_results")),
        )

    return builder.as_markup(resize_keyboard=True)


# ── Referral share (Inline — for share link) ───────────────────

def referral_kb(ref_link: str, count: int, required: int, lang: str = "uz") -> InlineKeyboardMarkup:
    # Faqat havolani o'zini ulashish uchun text qismini olib tashlaymiz
    share_url = f"https://t.me/share/url?url={ref_link}"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=t("share_btn", lang), url=share_url))
    return builder.as_markup()


# ── Course selection ───────────────────────────────────────────

def courses_kb(courses: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    for i, course in enumerate(courses):
        emoji = emojis[i] if i < len(emojis) else "📖"
        builder.row(
            InlineKeyboardButton(
                text=f"{emoji} {course['title']}",
                callback_data=f"course_{course['id']}",
            )
        )
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="show_course_cats"))
    return builder.as_markup()


def course_categories_kb(
    lang: str = "uz", 
    standard_active: bool = True, 
    mandatory_active: bool = True,
    labels: dict = None
) -> InlineKeyboardMarkup:
    """Kurs kategoriyalarini tanlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    if labels is None: labels = {}
    
    if mandatory_active:
        btn_text = labels.get("label_btn_mandatory") or t("btn_mandatory_courses", lang)
        builder.row(
            InlineKeyboardButton(text=btn_text, callback_data="courses_cat_mandatory")
        )
    if standard_active:
        btn_text = labels.get("label_btn_standard") or t("btn_standard_courses", lang)
        builder.row(
            InlineKeyboardButton(text=btn_text, callback_data="courses_cat_standard")
        )
    
    return builder.as_markup()


# ── Misc ───────────────────────────────────────────────────────

def cancel_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=t("btn_cancel", lang)))
    return builder.as_markup(resize_keyboard=True)


def remove_kb() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def back_kb() -> InlineKeyboardMarkup:
    """Simple inline back button."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main"))
    return builder.as_markup()


def registration_start_kb() -> InlineKeyboardMarkup:
    """Inline registration start button (used in some handlers)."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Ro'yxatdan o'tish", callback_data="start_registration"))
    return builder.as_markup()
