import logging
import requests
import datetime
from bs4 import BeautifulSoup
from langchain_community.tools import DuckDuckGoSearchResults


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearchTool:
    def __init__(self, max_content_Length=1000, timeout=10):
        """
        Initialise the Web Search Tool with configurable parameters

        Args: 
            max_content_Length (int): Maximum length of content to be fetched from the web
            timeout (int): Timeout for the request to fetch the content
        """
        self.search_tool = DuckDuckGoSearchResults()
        self.max_content_length = max_content_Length
        self.timeout = timeout
        
    def fetch_link_content(self, link: str) -> str:
        """
        Fetch the content of the link.

        Args:
            link (str): The link to fetch content from.

        Returns:
            str: The content of the link.
        """
        try: 
            logger.info(f"Fetching content from link: {link} \n Time: {datetime.datetime.now()}")
            response = requests.get(link, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract text and remove uneccessary characters and tags
            content  = " ".join(soup.stripped_strings)
            return content[:self.max_content_length]
        except Exception as e:
            raise 
        
    def web_search(self, query: str, top_n: int = 5):
        """
        Perform web search and fetch the most relevant results.

        Args:
            query (str): The search query.
            top_n (int): The number of results to fetch.

        Returns:
            list: list of dictornaries conataiing the title, link, 
            snippet and content of the links
        """
        start_time = datetime.datetime.now()
        logger.info(f"Performing web search for query: {query} \n Time: {start_time}")
        search_results = self.search_tool.invoke(query, top_n)
        response_to_llm = []

        for result in search_results:
            try:
                link_content = self.fetch_link_content(result["link"])
                response_to_llm.append({
                    "title": result["title"],
                    "link": result["link"],
                    "snippet": result["snippet"],
                    "content": link_content
                })
            except Exception as e:
                response_to_llm.append({
                    "title": result["title"],
                    "link": result["link"],
                    "snippet": result["snippet"],
                    "content": f"error fetching link content: {str(e)}"
                })
        end_time = datetime.datetime.now()
        logger.info(f"Web search completed for query: {query} \n Time taken: {end_time - start_time}")   
        return response_to_llm
        
        