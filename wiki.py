import logging
import aiohttp
import urllib.parse
import xml.etree.ElementTree as ET  # Import XML parsing library
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
        "wiki_usage": "Используйте: .wiki <запрос>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig()
        self.user_agent = "MyUserbot/1.0 (https://example.com; myemail@example.com)"

    async def fetch_wikipedia_summary(self, query: str) -> str:
        """Получает краткую информацию из Википедии."""
        try:
            headers = {'User-Agent': self.user_agent}
            encoded_query = urllib.parse.quote_plus(query)  # URL-encode the query
            api_url = f"https://ru.wikipedia.org/w/api.php?action=opensearch&search={encoded_query}&prop=info&format=xml&inprop=url"

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(api_url) as response:
                    if response.status == 200:
                        xml_text = await response.text()
                        try:
                            root = ET.fromstring(xml_text)
                            # Extract data from XML (adapt to the XML structure)
                            items = root.findall(".//Item")  # Adjust based on actual XML structure
                            if items:
                                first_item = items[0]
                                title = first_item.findtext("./Text")
                                description = first_item.findtext("./Description")
                                url = first_item.findtext("./Url")
                                return f"{title}\n{description}\n{url}"
                            else:
                                return self.strings["no_results"]
                        except ET.ParseError as e:
                            logger.error(f"Ошибка парсинга XML: {e}")
                            return self.strings["query_error"]
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
