# -*- coding: utf-8 -*-
# meta developer: @negrmefrdron
# scope: heroku_only

import logging
import asyncio
from herokutl.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class SpamModule(loader.Module):
    strings = {
        "name": "SpamModule",
        "start_spam": "Запуск спама с задержкой в {delay} секунд.",
        "delayed_message": "Сообщение отправлено.",
        "spam_completed": "Спам завершён."
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "delay",  # Задержка по умолчанию
            int(8),  # 8 секунд
            lambda: "Задержка между сообщениями"
        )

    async def send_spam(self, message: Message, text: str, count: int):
        """Отправляет сообщения с заданной задержкой."""
        for i in range(count):
            await message.respond(text)
            await asyncio.sleep(self.config["delay"])  # Задержка между сообщениями
            logger.info(f"Отправлено сообщение {i+1}: {text}")

    @loader.command
    async def spam(self, message: Message):
        """Запускает спам сообщений.
        
        Пример использования:
        .spam <количество> <текст сообщения>
        """
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.respond("Используйте: .spam <количество> <текст сообщения>")
            return

        try:
            count = int(args[1])
            text = args[2]
        except ValueError:
            await message.respond("Количество должно быть числом.")
            return

        await message.respond(self.strings["start_spam"].format(delay=self.config["delay"]))
        await self.send_spam(message, text, count)
        await message.respond(self.strings["spam_completed"])
