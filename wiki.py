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
                        #print(f"XML Response: {xml_text}")  # Remove comment to see XML
                        try:
                            root = ET.fromstring(xml_text)
                            # Try different XML structures
                            title = root.find(".//Text")
                            description = root.find(".//Description")
                            url = root.find(".//Url")

                            if title is not None and description is not None and url is not None:
                                title_text = title.text if title.text else "N/A"  # Handle empty text
                                description_text = description.text if description.text else "N/A"  # Handle empty text
                                url_text = url.text if url.text else "N/A" # Handle empty text
                                return f"{title_text}\n{description_text}\n{url_text}"
                            else:
                                # Try alternative structure:
                                item = root.find(".//Item")
