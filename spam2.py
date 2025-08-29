# -*- coding: utf-8 -*-
# meta developer: @negrmefrdron
# scope: heroku_only

import logging
import asyncio
from herokutl.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__) # Исправлено: __name__

@loader.tds
class SpamModule(loader.Module):
    strings = {
        "name": "SpamModule",
        "start_spam": "Запуск отправки сообщений с задержкой в {delay} секунд.",
        "delayed_message": "Сообщение отправлено.",
        "spam_completed": "Отправка сообщений завершена.",
        "spam_usage": "Используйте: .spam <количество> <текст сообщения>" # Добавлено
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            {
                "delay": loader.ConfigValue(
                    8,
                    "Задержка между сообщениями в секундах",
                    validator=loader.validators.Integer(minimum=1)  # Минимальная задержка 1 секунда
                )
            }
        )

    async def send_spam(self, message: Message, text: str, count: int):
        """Отправляет сообщения с заданной задержкой."""
        for i in range(count):
            await utils.answer(message, text) # Исправлено: utils.answer
            await asyncio.sleep(self.config["delay"])  # Задержка между сообщениями
            logger.info(f"Отправлено сообщение {i+1}: {text}")

    @loader.command(ru_doc="Отправляет сообщения с задержкой.", ua_doc="Надсилає повідомлення із затримкою.", en_doc="Sends messages with a delay.")
    async def spam(self, message: Message):
        """Отправляет сообщения с заданной задержкой.
        
        Пример использования:
        .spam <количество> <текст сообщения>
        """
        args = utils.get_args_raw(message) # Исправлено: utils.get_args_raw
        if not args:
            await utils.answer(message, self.strings["spam_usage"]) # Исправлено: utils.answer
            return

        args_list = args.split(maxsplit=1) # Исправлено: args.split
        if len(args_list) < 2:
            await utils.answer(message, self.strings["spam_usage"]) # Исправлено: utils.answer
            return

        try:
            count = int(args_list[0])
            text = args_list[1]
        except ValueError:
            await utils.answer(message, "Количество должно быть числом.") # Исправлено: utils.answer
            return

        await utils.answer(message, self.strings["start_spam"].format(delay=self.config["delay"])) # Исправлено: utils.answer
        await self.send_spam(message, text, count)
        await utils.answer(message, self.strings["spam_completed"]) # Исправлено: utils.answer
