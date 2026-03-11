"""
Middleware to clear FSM state when user clicks main menu buttons.
"""

from typing import Callable, Any, Awaitable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from utils.i18n import TEXTS, ADMIN_TEXTS

def get_all_button_labels():
    labels = set()
    for d in [TEXTS, ADMIN_TEXTS]:
        for key, lang_dict in d.items():
            if isinstance(lang_dict, dict):
                for val in lang_dict.values():
                    if isinstance(val, str) and val:
                        labels.add(val)
    return labels

ALL_BUTTON_LABELS = get_all_button_labels()

class StateCleanupMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        # We only care about messages (ReplyKeyboard clicks)
        state: FSMContext = data.get("state")
        if not state:
            return await handler(event, data)

        # 1. Handle Messages (ReplyKeyboard buttons)
        if isinstance(event, Message) and event.text:
            if event.text in ALL_BUTTON_LABELS:
                await state.clear()
        
        # 2. Handle CallbackQueries (Inline buttons)
        # We clear state for most admin callback queries to ensure fresh start
        elif isinstance(event, CallbackQuery) and event.data:
            # Skip clearing for specific state-related callbacks if any
            # For this bot, most admin buttons should clear any existing state
            if event.data.startswith(("admin_", "sa_", "back_to_admin")):
                await state.clear()
        
        return await handler(event, data)
