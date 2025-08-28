# -*- coding: utf-8 -*-
# meta developer: @negrmefrdron
# scope: heroku_only

import logging
import aiohttp
from herokutl.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class ScreenshotModule(loader.Module):
    strings = {
        "name": "ScreenshotModule",
        "waiting_response": "Подождите, пожалуйста, я получаю снимок экрана...",
        "error": "Произошла ошибка при получении снимка экрана.",
        "no_image": "Не удалось получить изображение."
    }

    def __init__(self):
        self.config = loader.ModuleConfig()

    async def get_screenshot(self, url: str) -> str:
        """Отправляет URL в @siteshot_bot и получает изображение."""
        try:
            async with aiohttp.ClientSession() as session:
                # Отправка ссылки в бот
                async with session.get(f"https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage", 
                                        params={"chat_id": "@siteshot_bot", "text": url}) as response:
                    if response.status == 200:
                        await utils.sleep(5)  # Ждем некоторое время, чтобы бот успел обработать запрос
                        
                        # Получение результата (можно адаптировать под ваш случай)
                        response = await session.get(f"https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
                        data = await response.json()
                        
                        # Находим последнее сообщение от @siteshot_bot
                        for update in data.get('result', []):
                            if 'message' in update and '@siteshot_bot' in update['message'].get('text', ''):
                                # Извлечение ссылки на изображение
                                return update['message']['photo']  # Или что-то другое в зависимости от формата ответа
                    else:
                        logger.error(f"Ошибка отправки сообщения: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка при взаимодействии с @siteshot_bot: {e}")
            return None

    @loader.command
    async def screenshot(self, message: Message):
        """Получает снимок экрана по указанной ссылке.

        Пример использования:
        .screenshot https://example.com
        """
        url = message.text.strip()
        if url:
            await message.respond(self.strings["waiting_response"])
            image_id = await self.get_screenshot(url)
            if image_id:
                await message.respond(image_id)  # Здесь лучше обработать получение правильной ссылки на изображение
            else:
                await message.respond(self.strings["no_image"])
        else:
            await message.respond("Пожалуйста, введите ссылку для получения снимка экрана.")
