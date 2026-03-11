import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    bot_token: str
    superadmin_id: int
    required_channel: str
    courses_channel: str
    # PostgreSQL
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str


def load_config() -> Config:
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN is not set in .env file")

    superadmin_id = os.getenv("SUPERADMIN_ID")
    if not superadmin_id:
        raise ValueError("SUPERADMIN_ID is not set in .env file")

    return Config(
        bot_token=bot_token,
        superadmin_id=int(superadmin_id),
        required_channel=os.getenv("REQUIRED_CHANNEL", "@registon_markaz"),
        courses_channel=os.getenv("COURSES_CHANNEL", ""),
        db_host=os.getenv("DB_HOST", "localhost"),
        db_port=int(os.getenv("DB_PORT", "5432")),
        db_user=os.getenv("DB_USER", "postgres"),
        db_password=os.getenv("DB_PASSWORD", ""),
        db_name=os.getenv("DB_NAME", "registonbot"),
    )


config = load_config()
