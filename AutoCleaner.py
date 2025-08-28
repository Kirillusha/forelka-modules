import asyncio
import logging

from herokutl.tl.types import Message
from telethon.tl.functions.messages import DeleteHistoryRequest

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class AutoCleanerMod(loader.Module):
    """Deletes your old messages after a specified time."""

    strings = {
        "name": "AutoCleaner",
        "clean_usage": "🚫 <b>Usage:</b> <code>.clean &lt;time&gt;</code> (e.g., <code>.clean 10m</code>)",
        "invalid_time": "🚫 <b>Invalid time format.</b> Use: 30s, 10m, 2h, 1d",
        "clean_scheduled": "✅ <b>Message cleaning scheduled in:</b> <code>{}</code>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig()

    async def client_ready(self, client, db):
        self._client = client

    def _parse_time(self, time_str: str) -> int or None:
        """Parses time from string to seconds."""
        time_str = time_str.lower()
        patterns = {
            "s": r"(\d+)s",  # seconds
            "m": r"(\d+)m",  # minutes
            "h": r"(\d+)h",  # hours
            "d": r"(\d+)d",  # days
        }

        for unit, pattern in patterns.items():
            match = re.match(pattern, time_str)
            if match:
                value = int(match.group(1))
                multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
                return value * multipliers[unit]

        return None

    async def _delete_messages(self, chat_id: int, delay: int):
        """Deletes messages after a delay."""
        await asyncio.sleep(delay)
        try:
            await self._client(DeleteHistoryRequest(peer=chat_id, max_id=0, just_clear=False))
            logger.info(f"Successfully cleaned chat {chat_id}")
        except Exception as e:
            logger.exception(f"Error cleaning chat {chat_id}:")

    @loader.command(ru_doc="Удаляет старые сообщения через заданное время.", ua_doc="Видаляє старі повідомлення через заданий час.", de_doc="Löscht alte Nachrichten nach einer bestimmten Zeit.")
    async def clean(self, message: Message):
        """Deletes your old messages after a specified time."""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["clean_usage"])
            return

        delay = self._parse_time(args)
        if delay is None:
            await utils.answer(message, self.strings["invalid_time"])
            return

        chat_id = message.chat_id
        asyncio.create_task(self._delete_messages(chat_id, delay))

        time_formatted = self._format_time(delay)
        await utils.answer(message, self.strings["clean_scheduled"].format(time_formatted))

    def _format_time(self, seconds: int) -> str:
        """Formats time in a readable way."""
        if seconds < 60:
            return f"{seconds} сек"
        elif seconds < 3600:
            return f"{seconds // 60} мин"
        elif seconds < 86400:
            return f"{seconds // 3600} час"
        else:
            return f"{seconds // 86400} дн"
