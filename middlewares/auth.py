"""
Authentication middleware for Registon O'quv Markaz bot.
- On every update: get or create user in DB
- Add user data to middleware_data
- Block banned users
- Log all messages
"""

import logging
from typing import Callable, Any, Awaitable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, Update

from database import db

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # Extract user info from event
        user = None
        if isinstance(event, Update):
            if event.message:
                user = event.message.from_user
            elif event.callback_query:
                user = event.callback_query.from_user
            elif event.my_chat_member:
                user = event.my_chat_member.from_user

        if user:
            try:
                db_user = await db.get_or_create_user(
                    telegram_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                )
                data["db_user"] = db_user

                # Log message
                logger.info(
                    "[%s] @%s (%s) — %s",
                    user.id,
                    user.username or "no_username",
                    user.first_name or "",
                    type(event).__name__,
                )

                # --- GLOBAL GUARDS ---
                # 1. If user was deleted from DB, get_or_create_user will return a new unregistered user.
                # 2. Redirect unregistered users to start if they try to use other features.
                is_reg = db_user.get("is_registered", False) if db_user else False
                
                # Check for subscription on every message/callback (if registered)
                if is_reg:
                    # We only check for messages/callbacks that aren't about checking subscription itself
                    is_check_cb = isinstance(event, Update) and event.callback_query and event.callback_query.data == "check_subscription"
                    
                    if not is_check_cb:
                        channels = await db.get_active_channels()
                        if channels:
                            from utils.channel_check import check_subscriptions
                            from keyboards.user_kb import channel_check_kb
                            from utils.i18n import t
                            
                            all_sub, results = await check_subscriptions(data["bot"], user.id, channels)
                            if not all_sub:
                                lang = db_user.get("language", "uz")
                                not_joined = [ch for ch, ok in zip(channels, results) if not ok]
                                
                                if isinstance(event, Update):
                                    if event.message:
                                        await event.message.answer(
                                            t("channel_join_prompt", lang, n=len(not_joined)),
                                            reply_markup=channel_check_kb(not_joined, lang=lang),
                                        )
                                    elif event.callback_query:
                                        await event.callback_query.message.answer(
                                            t("channel_join_prompt", lang, n=len(not_joined)),
                                            reply_markup=channel_check_kb(not_joined, lang=lang),
                                        )
                                        await event.callback_query.answer()
                                return  # Stop processing for unsubscribed users

            except Exception as e:
                logger.error("AuthMiddleware error for user %s: %s", user.id if user else "?", e)
                data["db_user"] = None
        else:
            data["db_user"] = None

        return await handler(event, data)
