# -*- coding: utf-8 -*-
# meta developer: @negrmefrdron
# scope: heroku_only

import logging
import aiohttp
from herokutl.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__) # Исправлено

@loader.tds
class ScreenshotModule(loader.Module):
    strings = {
        "name": "ScreenshotModule",
        "waiting_response": "Подождите, пожалуйста, я получаю снимок экрана...",
        "error": "Произошла ошибка при получении снимка экрана.",
        "no_image": "Не удалось получить изображение.",
        "screenshot_usage": "Используйте: .screenshot <URL>" # Добавлено
    }

    def __init__(self):
        self.config = loader.ModuleConfig()

    async def get_screenshot(self, url: str) -> str:
        """Отправляет URL в @siteshot_bot и получает изображение."""
        try:
            async with aiohttp.ClientSession() as session:
                bot_username = "@siteshot_bot"

                # Отправка ссылки в бот
                send_message_url = f"https://api.telegram.org/bot/sendMessage" # No token needed
                params = {"chat_id": bot_username, "text": url}
                async with session.get(send_message_url, params=params) as response:
                    if response.status == 200:
                        await asyncio.sleep(10)  # Ждем, пока бот обработает ссылку

                        # Получаем обновления, чтобы найти фото, отправленное ботом
                        get_updates_url = f"https://api.telegram.org/bot/getUpdates" # No token needed
                        async with session.get(get_updates_url) as updates_response:
                            updates_data = await updates_response.json()

                            # Ищем последнее сообщение от бота с фотографией
                            for update in reversed(updates_data.get('result', [])):
                                if 'message' in update and 'photo' in update['message'] and update['message']['chat']['username'] == bot_username.replace("@",""):
                                    # Предполагаем, что бот отправляет фото
                                    photos = update['message']['photo']
                                    best_photo = max(photos, key=lambda x: x['file_size'])
                                    file_id = best_photo['file_id']
                                    return file_id # or the url if it sends url

                    else:
                        logger.error(f"Ошибка отправки сообщения: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка при взаимодействии с @siteshot_bot: {e}")
            return None

    @loader.command(ru_doc="Получает снимок экрана.", ua_doc="Отримує знімок екрана.", en_doc="Gets a screenshot.") #Добавлено
    async def screenshot(self, message: Message):
        """Получает снимок экрана по указанной ссылке.

        Пример использования:
        .screenshot https://example.com
        """
        url = utils.get_args_raw(message) #Исправлено
        if url:
            await utils.answer(message, self.strings["waiting_response"])  # Исправлено

            image_id = await self.get_screenshot(url)

            if image_id:
                 try:
                    await self._client.send_photo(message.chat_id, photo=image_id, reply_to=message.id)
                 except Exception as e:
                    logger.error(f"Ошибка при отправке фото: {e}")
                    await utils.answer(message, self.strings["error"])

            else:
                await utils.answer(message, self.strings["no_image"]) #Исправлено
        else:
             await utils.answer(message, self.strings["screenshot_usage"]) #Исправлено

    async def client_ready(self, client, db):
        self._client = client
