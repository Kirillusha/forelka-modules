# -*- coding: utf-8 -*-
# meta developer: @negrmefrdron
# scope: heroku_only

import logging
import aiohttp
from herokutl.tl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class WikipediaModule(loader.Module):
    strings = {
        "name": "WikipediaModule",
        "query_success": "Вот что я нашел на Википедии:\n{}",
        "query_error": "Не удалось получить информацию из Википедии.",
        "no_results": "К сожалению, по вашему запросу ничего не найдено.",
        "wiki_usage": "Используйте: .wiki <запрос>"  # Добавлено описание использования
    }

    def __init__(self):
        self.config = loader.ModuleConfig()

    async def fetch_wikipedia_summary(self, query: str) -> str:
        """Получает краткую информацию из Википедии."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={query}&utf8=1"
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        pages = data.get("query", {}).get("search", [])
                        
                        if pages:
                            title = pages[0]["title"]
                            snippet = pages[0]["snippet"]
                            return f"{title}\n{snippet}"
                        else:
                            return self.strings["no_results"]
                    else:
                        logger.error(f"Ошибка API Википедии: {response.status}")
                        return self.strings["query_error"]
        except Exception as e:
            logger.error(f"Ошибка при запросе к Википедии: {e}")
            return self.strings["query_error"]

    @loader.command(ru_doc="Ищет информацию в Википедии.", ua_doc="Шукає інформацію у Вікіпедії.", en_doc="Searches Wikipedia for information.")
    async def wiki(self, message: Message):
        """Ищет информацию в Википедии по запросу.

        Пример использования:
        .wiki Python
        """
        user_query = utils.get_args_raw(message)
        if user_query:
            summary = await self.fetch_wikipedia_summary(user_query)
            await utils.answer(message, self.strings["query_success"].format(summary))
        else:
            await utils.answer(message, self.strings["wiki_usage"])
