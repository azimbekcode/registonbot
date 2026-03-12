"""
PostgreSQL table schemas for Registon O'quv Markaz bot.
Uses $1, $2 placeholders (asyncpg style).
SERIAL = auto-increment primary key.
"""

CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    telegram_id     BIGINT UNIQUE NOT NULL,
    username        TEXT,
    first_name      TEXT,
    full_name       TEXT,
    last_name_reg   TEXT,
    age             INTEGER,
    profession      TEXT,
    phone           TEXT UNIQUE,
    referral_code   TEXT UNIQUE,
    referred_by     BIGINT,
    referral_count  INTEGER DEFAULT 0,
    is_registered   SMALLINT DEFAULT 0,
    is_contestant   SMALLINT DEFAULT 0,
    is_banned       SMALLINT DEFAULT 0,
    joined_at       TIMESTAMP DEFAULT NOW(),
    registered_at   TIMESTAMP
);
"""

CREATE_REFERRALS_TABLE = """
CREATE TABLE IF NOT EXISTS referrals (
    id          SERIAL PRIMARY KEY,
    inviter_id  BIGINT NOT NULL,
    invitee_id  BIGINT NOT NULL,
    joined_at   TIMESTAMP DEFAULT NOW(),
    UNIQUE(invitee_id)
);
"""

CREATE_CHANNELS_TABLE = """
CREATE TABLE IF NOT EXISTS channels (
    id            SERIAL PRIMARY KEY,
    channel_id    TEXT NOT NULL,
    channel_title TEXT,
    invite_link   TEXT,
    is_active     SMALLINT DEFAULT 1,
    added_by      BIGINT,
    added_at      TIMESTAMP DEFAULT NOW()
);
"""

CREATE_COURSES_TABLE = """
CREATE TABLE IF NOT EXISTS courses (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT,
    message_id  BIGINT,
    file_id     TEXT,
    file_type   TEXT,
    category    TEXT DEFAULT 'standard',
    original_caption TEXT,
    is_active   SMALLINT DEFAULT 1,
    added_by    BIGINT,
    added_at    TIMESTAMP DEFAULT NOW()
);
"""

# Migration: add file_id column if missing
MIGRATE_COURSES_FILE_ID = """
ALTER TABLE courses ADD COLUMN IF NOT EXISTS file_id TEXT;
"""

# Migration: add category column if missing
MIGRATE_COURSES_CATEGORY = """
ALTER TABLE courses ADD COLUMN IF NOT EXISTS category TEXT DEFAULT 'standard';
"""

# Migration: add original_caption column if missing
MIGRATE_COURSES_CAPTION = """
ALTER TABLE courses ADD COLUMN IF NOT EXISTS original_caption TEXT;
"""

MIGRATE_CHANNELS_INVITE_LINK = """
ALTER TABLE channels ADD COLUMN IF NOT EXISTS invite_link TEXT;
"""

# Migration: add language column to users
MIGRATE_USERS_LANGUAGE = """
ALTER TABLE users ADD COLUMN IF NOT EXISTS language TEXT DEFAULT 'uz';
"""


CREATE_ADMINS_TABLE = """
CREATE TABLE IF NOT EXISTS admins (
    id          SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username    TEXT,
    full_name   TEXT,
    role        TEXT DEFAULT 'admin',
    added_by    BIGINT,
    added_at    TIMESTAMP DEFAULT NOW(),
    is_active   SMALLINT DEFAULT 1
);
"""

CREATE_BOT_SETTINGS_TABLE = """
CREATE TABLE IF NOT EXISTS bot_settings (
    key        TEXT PRIMARY KEY,
    value      TEXT,
    updated_by BIGINT,
    updated_at TIMESTAMP DEFAULT NOW()
);
"""

CREATE_CONTEST_PARTICIPANTS_TABLE = """
CREATE TABLE IF NOT EXISTS contest_participants (
    id                SERIAL PRIMARY KEY,
    telegram_id       BIGINT UNIQUE,
    joined_contest_at TIMESTAMP DEFAULT NOW()
);
"""

ALL_TABLES = [
    CREATE_USERS_TABLE,
    CREATE_REFERRALS_TABLE,
    CREATE_CHANNELS_TABLE,
    CREATE_COURSES_TABLE,
    CREATE_ADMINS_TABLE,
    CREATE_BOT_SETTINGS_TABLE,
    CREATE_CONTEST_PARTICIPANTS_TABLE,
]

DEFAULT_SETTINGS = [
    ("contest_active", "1"),
    ("required_referrals", "5"),
    ("welcome_message", "Assalomu alaykum! Registon O'quv Markazga xush kelibsiz!"),
    ("registration_open", "1"),
    ("standard_lessons_active", "1"),
    ("mandatory_lessons_active", "1"),
    ("label_btn_courses", "🎬 Bepul darslar"),
    ("label_btn_profile", "👤 Profil"),
    ("label_btn_invite", "🎁 Do'st taklif qilish"),
    ("label_btn_contest_rules", "📋 Tanlov shartlari"),
    ("label_btn_results", "🏅 Natijalar"),
    ("label_btn_mandatory", "🔐 Majburiy blok darslar"),
    ("label_btn_standard", "📖 Darsliklar"),
    ("text_profile", "👤 <b>PROFIL</b>\n\nIsm: {name}\nTel: {phone}\nReferallaringiz: {ref_count} ta"),
    ("text_courses_main", "📚 <b>BEPUL DARSLIKLAR</b>\n\nKerakli darslikni tanlang:"),
    ('text_courses_standard', '📚 <b>DARSLIKLAR</b>'),
    ('text_courses_mandatory', '🔐 <b>MAJBURIY BLOK DARSLAR</b>'),
    ('text_results_main', '🏅 <b>NATIJALAR</b>'),
]
