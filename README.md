# 🎓 Registon O'quv Markaz — Telegram Bot

Professional Telegram bot for **Registon O'quv Markaz** built with Python 3.11 + aiogram 3.x.

## ✨ Features

- ✅ Mandatory channel subscription check
- 📝 Multi-step FSM registration (name, age, profession, Uzbek phone)
- 🔗 Referral system with progress tracking
- 🏆 Auto-promotion to contest participant at 5 referrals
- 📚 Free courses forwarded from a private channel
- ⚙️ Full admin panel with 7 sections
- 📣 Async broadcast to targeted user groups
- 🚫 User ban/unban system
- 📊 Live statistics dashboard

---

## 🛠 Tech Stack

| Component   | Technology                      |
|-------------|--------------------------------|
| Language    | Python 3.11                    |
| Framework   | aiogram 3.4.1 (async)          |
| Database    | PostgreSQL + asyncpg           |
| Config      | python-dotenv                  |
| Phone       | phonenumbers library           |

---

## 📁 Project Structure

```
registon_bot/
├── bot.py                   ← Entry point
├── config.py                ← Settings loader
├── .env                     ← Secrets (not committed)
├── requirements.txt
├── database/
│   ├── db.py                ← All async CRUD operations
│   └── models.py            ← SQL table schemas
├── handlers/
│   ├── start.py             ← /start + channel check
│   ├── registration.py      ← FSM registration
│   ├── referral.py          ← Referral panel
│   ├── contest.py           ← Contest info
│   ├── courses.py           ← Free lessons
│   └── admin.py             ← Full admin panel
├── keyboards/
│   ├── user_kb.py           ← User keyboards
│   └── admin_kb.py          ← Admin keyboards
├── middlewares/
│   └── auth.py              ← Auth + ban check
└── utils/
    ├── channel_check.py     ← Subscription checker
    ├── referral_gen.py      ← Code generator
    └── phone_validator.py   ← Uzbek phone validator
```

---

## ⚙️ Setup

### 1. Clone / navigate to the project

```bash
cd registon_bot
```

### 2. Create a virtual environment

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure `.env`

Edit the `.env` file:

```env
BOT_TOKEN=your_bot_token_here          # Get from @BotFather
SUPERADMIN_ID=123456789                # Your Telegram numeric ID
REQUIRED_CHANNEL=@your_channel        # Main channel username
COURSES_CHANNEL=-100123456789          # Private channel numeric ID
DATABASE_PATH=registon.db
```

> **Get your Telegram ID**: Send `/start` to [@userinfobot](https://t.me/userinfobot)
>
> **Get private channel ID**: Forward a message from the channel to [@username_to_id_bot](https://t.me/username_to_id_bot)

### 5. Add bot as admin to channels

- **Required channel** (`REQUIRED_CHANNEL`): Bot must be **admin** to check membership
- **Courses channel** (`COURSES_CHANNEL`): Bot must be **admin** to forward messages

### 6. Run the bot

```bash
python bot.py
```

---

## 👥 User Flow

```
/start
  │
  ├─► Not subscribed → Show channel subscribe button
  │
  ├─► Subscribed, not registered → Registration form (5 steps)
  │     └─► After register → Referral panel
  │
  ├─► Registered, referrals < 5 → Referral progress panel
  │
  └─► Registered, referrals ≥ 5 → Contestant panel 🏆
```

---

## ⚙️ Admin Panel

Access with `/admin` command (only for admins).

| Section | Description |
|---------|-------------|
| 👥 Foydalanuvchilar | Search, view, ban, delete, export users |
| 🏆 Ishtirokchilar | View all contest participants |
| 📢 Kanallar | Add/remove/toggle required channels |
| 📚 Darsliklar | Add courses via forward from private channel |
| 📊 Statistika | Live stats + top referrers |
| ⚙️ Sozlamalar | Toggle contest/registration, set referral count |
| 👮 Adminlar | Add/remove admins (superadmin only) |
| 📣 Broadcast | Send messages to targeted user groups |

---

## 🔒 Security Notes

- All admin commands silently ignored for non-admins
- Users cannot refer themselves
- Duplicate referrals are ignored (DB UNIQUE constraint)
- Phone numbers validated against Uzbek operators only
- Superadmin cannot be deleted or demoted
- All DB operations wrapped in try/except with logging

---

## 📋 Database Tables

| Table | Purpose |
|-------|---------|
| `users` | All bot users + registration data |
| `referrals` | Referral relationships |
| `channels` | Required subscription channels |
| `courses` | Free lesson entries |
| `admins` | Admin accounts |
| `bot_settings` | Runtime-configurable settings |
| `contest_participants` | Contest participant records |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `BOT_TOKEN not set` | Check your `.env` file |
| Channel check fails | Ensure bot is admin in the channel |
| Course forwarding fails | Ensure bot is admin in courses channel, check COURSES_CHANNEL ID |
| Phone validation fails | Input must be valid Uzbek number (+998XX) |

---

## 📜 License

Private project for Registon O'quv Markaz. All rights reserved.
