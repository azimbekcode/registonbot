"""
Channel subscription checker utility.
"""

import logging
from typing import List, Tuple
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

logger = logging.getLogger(__name__)


async def check_subscriptions(
    bot: Bot, user_id: int, channels: list
) -> Tuple[bool, List[bool]]:
    """
    Check if user is subscribed to all active channels.
    Returns (all_subscribed, list_of_results_per_channel).
    
    NOTE: Bot must be admin in the channel to check membership.
    If bot is NOT admin, we assume user is NOT subscribed (strict mode).
    """
    results = []
    for ch in channels:
        channel_id = ch["channel_id"]
        try:
            member = await bot.get_chat_member(channel_id, user_id)
            is_member = member.status in ("member", "administrator", "creator")
            results.append(is_member)

        except TelegramForbiddenError:
            # Bot is not admin — cannot check membership
            # Strict mode: treat as NOT subscribed and warn admin
            logger.warning(
                "⚠️ Bot kanalda admin emas: %s — obunani tekshirib bo'lmadi. "
                "Botni kanalga admin qiling!",
                channel_id,
            )
            results.append(False)

        except TelegramBadRequest as e:
            if "user not found" in str(e).lower():
                # User never interacted with this channel
                results.append(False)
            else:
                logger.warning("BadRequest checking channel %s: %s", channel_id, e)
                results.append(False)

        except Exception as e:
            logger.error("Error checking channel %s: %s", channel_id, e)
            results.append(False)

    all_ok = all(results) if results else True
    return all_ok, results
