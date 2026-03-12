"""
Async PostgreSQL database layer using asyncpg connection pool.
Auto-creates the database if it doesn't exist.
"""

import logging
import datetime
from typing import Optional, List, Dict, Any

import asyncpg

from config import config
from database.models import ALL_TABLES, DEFAULT_SETTINGS

logger = logging.getLogger(__name__)

# Global connection pool
_pool: Optional[asyncpg.Pool] = None


async def _create_database_if_not_exists():
    """Connect to 'postgres' system DB and create our DB if missing."""
    try:
        conn = await asyncpg.connect(
            host=config.db_host,
            port=config.db_port,
            user=config.db_user,
            password=config.db_password,
            database="postgres",  # Connect to system DB first
        )
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", config.db_name
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{config.db_name}"')
            logger.info("✅ Database '%s' yaratildi.", config.db_name)
        else:
            logger.info("✅ Database '%s' allaqachon mavjud.", config.db_name)
        await conn.close()
    except Exception as e:
        logger.error("Database yaratishda xato: %s", e)
        raise


async def init_db():
    """Initialize pool, auto-create DB, create all tables, insert defaults."""
    global _pool

    # Step 1: Auto-create database if not exists
    await _create_database_if_not_exists()

    # Step 2: Create connection pool
    _pool = await asyncpg.create_pool(
        host=config.db_host,
        port=config.db_port,
        user=config.db_user,
        password=config.db_password,
        database=config.db_name,
        min_size=2,
        max_size=10,
    )

    # Step 3: Create tables only if they don't exist (PRESERVES data!)
    async with _pool.acquire() as conn:
        for table_sql in ALL_TABLES:
            await conn.execute(table_sql)

        # Migration: safe-add new columns to existing tables
        from database.models import (
            MIGRATE_COURSES_FILE_ID, 
            MIGRATE_USERS_LANGUAGE, 
            MIGRATE_COURSES_CATEGORY,
            MIGRATE_COURSES_CAPTION,
            MIGRATE_CHANNELS_INVITE_LINK,
            MIGRATE_CHANNELS_UNIQUE_ID
        )
        await conn.execute(MIGRATE_COURSES_FILE_ID)
        await conn.execute(MIGRATE_USERS_LANGUAGE)
        await conn.execute(MIGRATE_COURSES_CATEGORY)
        await conn.execute(MIGRATE_COURSES_CAPTION)
        await conn.execute(MIGRATE_CHANNELS_INVITE_LINK)
        await conn.execute(MIGRATE_CHANNELS_UNIQUE_ID)

        # Insert default settings (ON CONFLICT DO NOTHING = no overwrite)
        for key, value in DEFAULT_SETTINGS:
            await conn.execute(
                """INSERT INTO bot_settings (key, value)
                   VALUES ($1, $2)
                   ON CONFLICT (key) DO NOTHING""",
                key, value,
            )

    logger.info("✅ Barcha jadvallar tayyor.")


def pool() -> asyncpg.Pool:
    """Get the active connection pool."""
    if _pool is None:
        raise RuntimeError("Database pool is not initialized. Call init_db() first.")
    return _pool


# ─────────────────────────────────────────────────────────────
# SUPERADMIN & DEFAULT CHANNEL
# ─────────────────────────────────────────────────────────────

async def ensure_superadmin(telegram_id: int):
    async with pool().acquire() as conn:
        await conn.execute(
            """INSERT INTO admins (telegram_id, full_name, role, is_active)
               VALUES ($1, 'Superadmin', 'superadmin', 1)
               ON CONFLICT (telegram_id) DO NOTHING""",
            telegram_id,
        )


async def ensure_default_channel(channel_id: str):
    async with pool().acquire() as conn:
        exists = await conn.fetchval(
            "SELECT id FROM channels WHERE channel_id = $1", channel_id
        )
        if not exists:
            await conn.execute(
                "INSERT INTO channels (channel_id, channel_title, is_active) VALUES ($1, $2, 1)",
                channel_id, "Asosiy kanal",
            )


# ─────────────────────────────────────────────────────────────
# USER CRUD
# ─────────────────────────────────────────────────────────────

async def get_user(telegram_id: int) -> Optional[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1", telegram_id
        )


async def get_or_create_user(
    telegram_id: int,
    username: Optional[str],
    first_name: Optional[str],
) -> asyncpg.Record:
    async with pool().acquire() as conn:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1", telegram_id
        )
        if not user:
            await conn.execute(
                "INSERT INTO users (telegram_id, username, first_name) VALUES ($1, $2, $3)"
                " ON CONFLICT (telegram_id) DO NOTHING",
                telegram_id, username, first_name,
            )
            user = await conn.fetchrow(
                "SELECT * FROM users WHERE telegram_id = $1", telegram_id
            )
        return user


async def update_user(telegram_id: int, **kwargs):
    if not kwargs:
        return
    set_parts = ", ".join(f"{k} = ${i+2}" for i, k in enumerate(kwargs))
    values = [telegram_id] + list(kwargs.values())
    # reorder: telegram_id should be $1
    query = f"UPDATE users SET {set_parts} WHERE telegram_id = $1"
    # Fix: placeholders are $2..$N for kwargs values, $1 for telegram_id
    set_parts2 = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(kwargs))
    query2 = f"UPDATE users SET {set_parts2} WHERE telegram_id = ${len(kwargs)+1}"
    vals = list(kwargs.values()) + [telegram_id]
    async with pool().acquire() as conn:
        await conn.execute(query2, *vals)


async def register_user(
    telegram_id: int,
    full_name: str,
    last_name: str,
    age: int,
    profession: str,
    phone: str,
    referral_code: str,
    referred_by: Optional[int] = None,
):
    async with pool().acquire() as conn:
        await conn.execute(
            """UPDATE users SET
               full_name = $1,
               last_name_reg = $2,
               age = $3,
               profession = $4,
               phone = $5,
               referral_code = $6,
               referred_by = $7,
               is_registered = 1,
               registered_at = NOW()
               WHERE telegram_id = $8""",
            full_name, last_name, age, profession, phone,
            referral_code, referred_by, telegram_id,
        )


async def get_user_by_phone(phone: str) -> Optional[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE phone = $1", phone
        )


async def get_user_by_referral_code(code: str) -> Optional[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE referral_code = $1", code
        )


async def referral_code_exists(code: str) -> bool:
    async with pool().acquire() as conn:
        row = await conn.fetchval(
            "SELECT id FROM users WHERE referral_code = $1", code
        )
        return row is not None


async def ban_user(telegram_id: int, is_banned: int = 1):
    async with pool().acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_banned = $1 WHERE telegram_id = $2",
            is_banned, telegram_id,
        )


async def delete_user(telegram_id: int):
    async with pool().acquire() as conn:
        await conn.execute(
            "DELETE FROM users WHERE telegram_id = $1", telegram_id
        )


async def search_users(query: str) -> List[asyncpg.Record]:
    pattern = f"%{query}%"
    async with pool().acquire() as conn:
        return await conn.fetch(
            """SELECT * FROM users WHERE
               CAST(telegram_id AS TEXT) LIKE $1 OR
               phone LIKE $2 OR
               full_name ILIKE $3 OR
               username ILIKE $4
               LIMIT 20""",
            pattern, pattern, pattern, pattern,
        )


async def get_all_users(
    registered_only=False,
    contestants_only=False,
    unregistered_only=False,
) -> List[asyncpg.Record]:
    async with pool().acquire() as conn:
        if registered_only:
            return await conn.fetch(
                "SELECT * FROM users WHERE is_registered = 1 AND is_banned = 0"
            )
        elif contestants_only:
            return await conn.fetch(
                "SELECT * FROM users WHERE is_contestant = 1 AND is_banned = 0"
            )
        elif unregistered_only:
            return await conn.fetch(
                "SELECT * FROM users WHERE is_registered = 0 AND is_banned = 0"
            )
        else:
            return await conn.fetch("SELECT * FROM users WHERE is_banned = 0")


async def export_users_txt(registered_only=True) -> str:
    async with pool().acquire() as conn:
        if registered_only:
            rows = await conn.fetch(
                "SELECT * FROM users WHERE is_registered = 1 ORDER BY registered_at DESC"
            )
            title = "Registon O'quv Markaz — Ro'yxatdan o'tganlar"
        else:
            rows = await conn.fetch(
                "SELECT * FROM users ORDER BY joined_at DESC"
            )
            title = "Registon O'quv Markaz — Barcha foydalanuvchilar"

    lines = [f"{title}\n" + "=" * 50]
    for r in rows:
        lines.append(
            f"\n#{r['id']}. {r['full_name'] or ''} {r['last_name_reg'] or ''}\n"
            f"   📱 {r['phone']}\n"
            f"   🆔 TG: {r['telegram_id']}\n"
            f"   👥 Referallar: {r['referral_count']}\n"
            f"   🏆 Ishtirokchi: {'Ha' if r['is_contestant'] else 'Yoq'}\n"
            f"   📅 {r['registered_at']}"
        )
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────
# REFERRAL CRUD
# ─────────────────────────────────────────────────────────────

async def add_referral(inviter_id: int, invitee_id: int) -> bool:
    try:
        async with pool().acquire() as conn:
            async with conn.transaction():
                await conn.execute(
                    "INSERT INTO referrals (inviter_id, invitee_id) VALUES ($1, $2)",
                    inviter_id, invitee_id,
                )
                # Sync referral_count from actual referrals table (more reliable than +1)
                actual_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM referrals WHERE inviter_id = $1",
                    inviter_id,
                )
                await conn.execute(
                    "UPDATE users SET referral_count = $1 WHERE telegram_id = $2",
                    actual_count, inviter_id,
                )
            return True
    except asyncpg.UniqueViolationError:
        return False
    except Exception as e:
        logger.error("add_referral error: %s", e)
        return False


async def get_referral_list(inviter_id: int) -> List[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetch(
            """SELECT u.full_name, u.username, u.joined_at
               FROM referrals r
               JOIN users u ON u.telegram_id = r.invitee_id
               WHERE r.inviter_id = $1
               ORDER BY r.joined_at DESC""",
            inviter_id,
        )


async def sync_referral_counts():
    """Recalculate all referral_count values based on the referrals table."""
    async with pool().acquire() as conn:
        async with conn.transaction():
            # Reset all counts to 0
            await conn.execute("UPDATE users SET referral_count = 0")
            # Set counts based on actual rows in referrals table
            await conn.execute("""
                UPDATE users u
                SET referral_count = r.cnt
                FROM (
                    SELECT inviter_id, COUNT(*) as cnt
                    FROM referrals
                    GROUP BY inviter_id
                ) r
                WHERE u.telegram_id = r.inviter_id
            """)
    logger.info("✅ Referral counts synchronized.")


# ─────────────────────────────────────────────────────────────
# CONTEST
# ─────────────────────────────────────────────────────────────

async def make_contestant(telegram_id: int) -> int:
    async with pool().acquire() as conn:
        await conn.execute(
            "UPDATE users SET is_contestant = 1 WHERE telegram_id = $1",
            telegram_id,
        )
        await conn.execute(
            "INSERT INTO contest_participants (telegram_id) VALUES ($1) ON CONFLICT DO NOTHING",
            telegram_id,
        )
        row = await conn.fetchrow(
            "SELECT id FROM contest_participants WHERE telegram_id = $1",
            telegram_id,
        )
        return row["id"] if row else 0


async def remove_contestant(telegram_id: int):
    async with pool().acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "UPDATE users SET is_contestant = 0 WHERE telegram_id = $1",
                telegram_id,
            )
            await conn.execute(
                "DELETE FROM contest_participants WHERE telegram_id = $1",
                telegram_id,
            )


async def get_contest_count() -> int:
    async with pool().acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM contest_participants") or 0


# ─────────────────────────────────────────────────────────────
# CHANNELS CRUD
# ─────────────────────────────────────────────────────────────

async def get_active_channels() -> List[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetch("SELECT * FROM channels WHERE is_active = 1")


async def get_all_channels() -> List[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetch("SELECT * FROM channels ORDER BY added_at DESC")


async def add_channel(channel_id: str, channel_title: str, added_by: int, invite_link: Optional[str] = None):
    async with pool().acquire() as conn:
        await conn.execute(
            """INSERT INTO channels (channel_id, channel_title, added_by, invite_link)
               VALUES ($1, $2, $3, $4) ON CONFLICT (channel_id) DO UPDATE SET
               channel_title = EXCLUDED.channel_title,
               invite_link = EXCLUDED.invite_link,
               is_active = 1""",
            channel_id, channel_title, added_by, invite_link,
        )


async def remove_channel(channel_id: str):
    async with pool().acquire() as conn:
        # Match by channel_id (string, can be numeric or username)
        await conn.execute(
            "DELETE FROM channels WHERE channel_id = $1", str(channel_id)
        )


async def toggle_channel(channel_db_id: int, is_active: int):
    async with pool().acquire() as conn:
        await conn.execute(
            "UPDATE channels SET is_active = $1 WHERE id = $2",
            is_active, channel_db_id,
        )


# ─────────────────────────────────────────────────────────────
# COURSES CRUD
# ─────────────────────────────────────────────────────────────

async def get_active_courses(category: str = "standard") -> List[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM courses WHERE is_active = 1 AND category = $1 ORDER BY added_at ASC, id ASC",
            category
        )


async def get_all_courses() -> List[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetch("SELECT * FROM courses ORDER BY added_at ASC, id ASC")


async def get_course(course_id: int) -> Optional[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM courses WHERE id = $1", course_id
        )


async def add_course(title: str, description: str, message_id: int, file_id: str, file_type: str, added_by: int, category: str = "standard", original_caption: Optional[str] = None):
    async with pool().acquire() as conn:
        await conn.execute(
            """INSERT INTO courses (title, description, message_id, file_id, file_type, added_by, category, original_caption)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""",
            title, description, message_id, file_id, file_type, added_by, category, original_caption
        )


async def toggle_course(course_id: int, is_active: int):
    async with pool().acquire() as conn:
        await conn.execute(
            "UPDATE courses SET is_active = $1 WHERE id = $2",
            is_active, course_id,
        )


async def delete_course(course_id: int):
    async with pool().acquire() as conn:
        await conn.execute("DELETE FROM courses WHERE id = $1", course_id)


# ─────────────────────────────────────────────────────────────
# ADMINS CRUD
# ─────────────────────────────────────────────────────────────

async def get_admin(telegram_id: int) -> Optional[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM admins WHERE telegram_id = $1 AND is_active = 1",
            telegram_id,
        )


async def get_all_admins() -> List[asyncpg.Record]:
    async with pool().acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM admins WHERE is_active = 1 ORDER BY added_at DESC"
        )


async def add_admin(telegram_id: int, username: Optional[str], full_name: Optional[str], added_by: int):
    async with pool().acquire() as conn:
        await conn.execute(
            """INSERT INTO admins (telegram_id, username, full_name, added_by, is_active, role)
               VALUES ($1, $2, $3, $4, 1, 'admin')
               ON CONFLICT (telegram_id) DO UPDATE SET
                 is_active = 1,
                 username = EXCLUDED.username,
                 full_name = EXCLUDED.full_name,
                 added_by = EXCLUDED.added_by""",
            telegram_id, username, full_name, added_by,
        )


async def remove_admin(telegram_id: int):
    async with pool().acquire() as conn:
        await conn.execute(
            "UPDATE admins SET is_active = 0 WHERE telegram_id = $1",
            telegram_id,
        )


async def is_admin(telegram_id: int, superadmin_id: int) -> bool:
    if telegram_id == superadmin_id:
        return True
    row = await get_admin(telegram_id)
    return row is not None


async def is_superadmin(telegram_id: int, superadmin_id: int) -> bool:
    if telegram_id == superadmin_id:
        return True
    row = await get_admin(telegram_id)
    return row is not None and row["role"] == "superadmin"


# ─────────────────────────────────────────────────────────────
# BOT SETTINGS CRUD
# ─────────────────────────────────────────────────────────────

async def get_setting(key: str) -> Optional[str]:
    async with pool().acquire() as conn:
        return await conn.fetchval(
            "SELECT value FROM bot_settings WHERE key = $1", key
        )


async def set_setting(key: str, value: str, updated_by: Optional[int] = None):
    async with pool().acquire() as conn:
        await conn.execute(
            """INSERT INTO bot_settings (key, value, updated_by, updated_at)
               VALUES ($1, $2, $3, NOW())
               ON CONFLICT (key) DO UPDATE SET
               value = EXCLUDED.value,
               updated_by = EXCLUDED.updated_by,
               updated_at = EXCLUDED.updated_at""",
            key, value, updated_by,
        )


async def get_all_settings() -> Dict[str, str]:
    async with pool().acquire() as conn:
        rows = await conn.fetch("SELECT key, value FROM bot_settings")
        return {row["key"]: row["value"] for row in rows}


# ─────────────────────────────────────────────────────────────
# STATISTICS
# ─────────────────────────────────────────────────────────────

async def get_stats() -> Dict[str, Any]:
    async with pool().acquire() as conn:
        total = await conn.fetchval("SELECT COUNT(*) FROM users") or 0
        registered = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE is_registered = 1"
        ) or 0
        contestants = await conn.fetchval(
            "SELECT COUNT(*) FROM contest_participants"
        ) or 0
        today = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE joined_at::date = CURRENT_DATE"
        ) or 0
        week = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE joined_at >= NOW() - INTERVAL '7 days'"
        ) or 0
        month = await conn.fetchval(
            "SELECT COUNT(*) FROM users WHERE DATE_TRUNC('month', joined_at) = DATE_TRUNC('month', NOW())"
        ) or 0
        top_referrers = await conn.fetch(
            """SELECT id, telegram_id, username, full_name, referral_count
               FROM users WHERE referral_count > 0
               ORDER BY referral_count DESC LIMIT 5"""
        )
    return {
        "total": total,
        "registered": registered,
        "contestants": contestants,
        "today": today,
        "week": week,
        "month": month,
        "top_referrers": top_referrers,
    }


async def get_referral_leaderboard(limit: int = None) -> List[asyncpg.Record]:
    """Referral yig'uvchilarni kamayish tartibida qaytaradi. limit=None bo'lsa hammasi."""
    async with pool().acquire() as conn:
        if limit is None:
            return await conn.fetch(
                """
                SELECT id, telegram_id, username, full_name, last_name_reg, referral_count
                FROM users
                WHERE referral_count > 0 AND is_banned = 0
                ORDER BY referral_count DESC
                """
            )
        return await conn.fetch(
            """
            SELECT id, telegram_id, username, full_name, last_name_reg, referral_count
            FROM users
            WHERE referral_count > 0 AND is_banned = 0
            ORDER BY referral_count DESC
            LIMIT $1
            """,
            limit,
        )


async def get_contest_participants_ids() -> List[asyncpg.Record]:
    """Konkurs ishtirokchilarining Telegram IDlari va asosiy ma'lumotlari."""
    async with pool().acquire() as conn:
        return await conn.fetch(
            """
            SELECT cp.telegram_id, cp.joined_contest_at,
                   u.full_name, u.last_name_reg, u.username, u.referral_count
            FROM contest_participants cp
            LEFT JOIN users u ON u.telegram_id = cp.telegram_id
            ORDER BY cp.joined_contest_at ASC
            """
        )


async def pick_random_contestant() -> Optional[asyncpg.Record]:
    """Konkurs ishtirokchilari orasidan random bir kishini tanlaydi."""
    async with pool().acquire() as conn:
        return await conn.fetchrow(
            """
            SELECT cp.telegram_id, cp.joined_contest_at,
                   u.full_name, u.last_name_reg, u.username, u.phone, u.referral_count
            FROM contest_participants cp
            LEFT JOIN users u ON u.telegram_id = cp.telegram_id
            ORDER BY RANDOM()
            LIMIT 1
            """
        )


# ─────────────────────────────────────────────────────────────
# DATABASE VIEWER (SUPERADMIN ONLY)
# ─────────────────────────────────────────────────────────────

async def db_get_all_users_full() -> List[asyncpg.Record]:
    """Barcha userlarni to'liq ma'lumot bilan qaytaradi."""
    async with pool().acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM users ORDER BY joined_at DESC"
        )


async def db_get_all_referrals() -> List[asyncpg.Record]:
    """Barcha referral yozuvlarini qaytaradi."""
    async with pool().acquire() as conn:
        return await conn.fetch(
            """
            SELECT r.id, r.inviter_id, r.invitee_id, r.joined_at,
                   u1.full_name AS inviter_name, u1.username AS inviter_username,
                   u2.full_name AS invitee_name, u2.username AS invitee_username
            FROM referrals r
            LEFT JOIN users u1 ON u1.telegram_id = r.inviter_id
            LEFT JOIN users u2 ON u2.telegram_id = r.invitee_id
            ORDER BY r.joined_at DESC
            """
        )


async def db_get_all_contest_participants() -> List[asyncpg.Record]:
    """Konkurs ishtirokchilarini to'liq ma'lumot bilan qaytaradi."""
    async with pool().acquire() as conn:
        return await conn.fetch(
            """
            SELECT cp.id, cp.telegram_id, cp.joined_contest_at,
                   u.full_name, u.username, u.phone, u.referral_count
            FROM contest_participants cp
            LEFT JOIN users u ON u.telegram_id = cp.telegram_id
            ORDER BY cp.joined_contest_at DESC
            """
        )


async def db_get_table_counts() -> Dict[str, int]:
    """Har bir jadval uchun yozuvlar sonini qaytaradi."""
    async with pool().acquire() as conn:
        tables = [
            "users", "admins", "channels", "courses",
            "referrals", "contest_participants", "bot_settings"
        ]
        counts = {}
        for table in tables:
            counts[table] = await conn.fetchval(f"SELECT COUNT(*) FROM {table}") or 0
        return counts


UNKNOWN = "Noma'lum"

async def db_export_full_report() -> str:
    """To'liq database hisobotini matn ko'rinishida qaytaradi."""
    async with pool().acquire() as conn:
        users = await conn.fetch("SELECT * FROM users ORDER BY joined_at DESC")
        admins = await conn.fetch("SELECT * FROM admins ORDER BY added_at DESC")
        channels = await conn.fetch("SELECT * FROM channels ORDER BY added_at DESC")
        courses = await conn.fetch("SELECT * FROM courses ORDER BY added_at ASC, id ASC")
        referrals = await conn.fetch(
            """
            SELECT r.inviter_id, r.invitee_id, r.joined_at,
                   u1.full_name AS inviter_name, u2.full_name AS invitee_name
            FROM referrals r
            LEFT JOIN users u1 ON u1.telegram_id = r.inviter_id
            LEFT JOIN users u2 ON u2.telegram_id = r.invitee_id
            ORDER BY r.joined_at DESC
            """
        )
        contest = await conn.fetch(
            "SELECT cp.telegram_id, cp.joined_contest_at, u.full_name, u.phone "
            "FROM contest_participants cp LEFT JOIN users u ON u.telegram_id = cp.telegram_id "
            "ORDER BY cp.joined_contest_at"
        )
        settings = await conn.fetch("SELECT * FROM bot_settings")

    sep = "=" * 60
    lines = [
        "REGISTON O'QUV MARKAZ — TO'LIQ DATABASE HISOBOT",
        sep,
        "",
        f"📅 Sana: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"{'─'*60}",
        f"👥 FOYDALANUVCHILAR ({len(users)} ta)",
        f"{'─'*60}",
    ]
    for u in users:
        name = f"{u['full_name'] or ''} {u['last_name_reg'] or ''}".strip() or "Noma'lum"
        reg = "✅" if u['is_registered'] else "❌"
        ban = " 🚫BAN" if u['is_banned'] else ""
        lines.append(
            f"#{u['id']}. {name}{ban}\n"
            f"   TG: {u['telegram_id']} | @{u['username'] or '-'}\n"
            f"   Tel: {u['phone'] or '-'} | Yosh: {u['age'] or '-'} | Kasb: {u['profession'] or '-'}\n"
            f"   Reg:{reg} | Referal:{u['referral_count']} | Qo'shildi:{str(u['joined_at'])[:10]}"
        )

    lines += [
        "",
        f"{'─'*60}",
        f"👮 ADMINLAR ({len(admins)} ta)",
        f"{'─'*60}",
    ]
    for i, a in enumerate(admins, 1):
        lines.append(
            f"{i}. {a['full_name'] or UNKNOWN} | @{a['username'] or '-'} "
            f"| {a['role']} | TG:{a['telegram_id']}"
        )

    lines += [
        "",
        f"{'─'*60}",
        f"📢 KANALLAR ({len(channels)} ta)",
        f"{'─'*60}",
    ]
    for i, c in enumerate(channels, 1):
        st = "✅" if c['is_active'] else "❌"
        lines.append(f"{i}. {st} {c['channel_title'] or '-'} — {c['channel_id']}")

    lines += [
        "",
        f"{'─'*60}",
        f"📚 DARSLIKLAR ({len(courses)} ta)",
        f"{'─'*60}",
    ]
    for i, c in enumerate(courses, 1):
        st = "✅" if c['is_active'] else "❌"
        lines.append(f"{i}. {st} {c['title']} | {c['file_type']} | msg_id:{c['message_id']}")

    lines += [
        "",
        f"{'─'*60}",
        f"🔗 REFERALLAR ({len(referrals)} ta)",
        f"{'─'*60}",
    ]
    for i, r in enumerate(referrals, 1):
        lines.append(
            f"{i}. {r['inviter_name'] or r['inviter_id']} → "
            f"{r['invitee_name'] or r['invitee_id']} | {str(r['joined_at'])[:10]}"
        )

    lines += [
        "",
        f"{'─'*60}",
        f"🏆 KONKURS ISHTIROKCHILARI ({len(contest)} ta)",
        f"{'─'*60}",
    ]
    for i, c in enumerate(contest, 1):
        lines.append(
            f"{i}. {c['full_name'] or UNKNOWN} | Tel:{c['phone'] or '-'} "
            f"| TG:{c['telegram_id']} | {str(c['joined_contest_at'])[:10]}"
        )

    lines += [
        "",
        f"{'─'*60}",
        f"⚙️ BOT SOZLAMALARI ({len(settings)} ta)",
        f"{'─'*60}",
    ]
    for s in settings:
        lines.append(f"  {s['key']}: {s['value']}")

    return "\n".join(lines)


# ── LANGUAGE HELPERS ─────────────────────────────────────────────────

async def get_user_language(telegram_id: int) -> str:
    """Returns user's language code: 'uz', 'ru', or 'en'. Default: 'uz'."""
    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT language FROM users WHERE telegram_id = $1", telegram_id
        )
    if row and row["language"] in ("uz", "ru", "en"):
        return row["language"]
    return "uz"


async def set_user_language(telegram_id: int, lang: str) -> None:
    """Set user language: 'uz', 'ru', or 'en'."""
    if lang not in ("uz", "ru", "en"):
        lang = "uz"
    async with _pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET language = $1 WHERE telegram_id = $2",
            lang, telegram_id,
        )

