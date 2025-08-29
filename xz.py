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
    """Отправляет сообщения с задержкой."""
    strings = {
        "name": "SpamModule",
        "start_spam": "<b>Начинаю отправку сообщений с задержкой {delay} секунд.</b>",
        "delayed_message": "Сообщение отправлено.",
        "spam_completed": "<b>Отправка сообщений завершена.</b>",
        "spam_usage": "<b>Используйте:</b> <code>.spam &lt;количество&gt; &lt;текст сообщения&gt;</code>",
        "invalid_count": "<b>Количество должно быть целым числом больше 0.</b>",
        "no_args": "<b>Пожалуйста, укажите количество сообщений и текст.</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig({
            "delay": loader.ConfigValue(
                5,  # Default value
                "Задержка между сообщениями (в секундах)", # Description
                validator=loader.validators.Integer(minimum=1, maximum=60)
            )
        })

    async def send_spam(self, message: Message, text: str, count: int):
        """Отправляет сообщения с заданной задержкой."""
        delay = self.config["delay"]
        if not isinstance(delay, int):
            logger.error(f"Неверный тип задержки: {type(delay)}. Использовано значение по умолчанию (5 секунд).")
            delay = 5  # Fallback to default value

        for i in range(count):
            await utils.answer(message, text)
            logger.info(f"Отправлено сообщение {i + 1}/{count}: {text}")
            await asyncio.sleep(delay)

    @loader.command(
        ru_doc="Отправляет указанное количество сообщений с заданной задержкой.",
        ua_doc="Надсилає вказану кількість повідомлень із заданою затримкою.",
        en_doc="Sends the specified number of messages with a given delay."
    )
    async def spam(self, message: Message):
        """Отправляет сообщения с задержкой.
        .spam <количество> <текст сообщения>
        """
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings["no_args"])
            return

        try:
            count, text = args.split(maxsplit=1)
            count = int(count)
            if count <= 0:
                raise ValueError
        except ValueError:
            await utils.answer(message, self.strings["invalid_count"])
            return

        delay = self.config["delay"]
        await utils.answer(
            message, self.strings["start_spam"].format(delay=delay)
        )
        await self.send_spam(message, text, count)

        await utils.answer(message, self.strings["spam_completed"])
