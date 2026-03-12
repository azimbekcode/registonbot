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
                # Check if user is an admin or superadmin to exempt them from subscription checks
                from config import config
                is_admin_user = (user.id == int(config.superadmin_id))
                if not is_admin_user:
                    admin_row = await db.get_admin(user.id)
                    is_admin_user = admin_row is not None
                
                # Check for subscription on every message/callback (EXCEPT FOR ADMINS)
                if not is_admin_user:
                    # We only check for messages/callbacks that aren't about checking subscription itself
                    is_check_cb = False
                    if isinstance(event, Update):
                        if event.callback_query and event.callback_query.data == "check_subscription":
                            is_check_cb = True
                    
                    if not is_check_cb:
                        channels = await db.get_active_channels()
                        if channels:
                            from utils.channel_check import check_subscriptions
                            from keyboards.user_kb import channel_check_kb
                            from utils.i18n import t
                            
                            all_sub, results = await check_subscriptions(data["bot"], user.id, channels)
                            if not all_sub:
                                # Get user language, fallback to 'uz'
                                lang = db_user.get("language", "uz") if db_user else "uz"
                                not_joined = [ch for ch, ok in zip(channels, results) if not ok]
                                
                                # Send subscription prompt based on event type
                                prompt_text = t("channel_join_prompt", lang, n=len(not_joined))
                                kb = channel_check_kb(not_joined, lang=lang)
                                
                                if isinstance(event, Update):
                                    if event.message:
                                        await event.message.answer(prompt_text, reply_markup=kb)
                                    elif event.callback_query:
                                        await event.callback_query.message.answer(prompt_text, reply_markup=kb)
                                        await event.callback_query.answer()
                                return  # Stop processing for unsubscribed users

            except Exception as e:
                logger.error("AuthMiddleware error for user %s: %s", user.id if user else "?", e)
                data["db_user"] = None
        else:
            data["db_user"] = None

        return await handler(event, data)
