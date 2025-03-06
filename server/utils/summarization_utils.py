import logging
from langchain_groq import ChatGroq
from config import settings
from utils.const import NEWS_SUMMARY_PROMPT
from newsapi import NewsApiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SummarizationService:
    """
    Centralized summarization service with a shared LLM instance.
    """

    _instance = None  # Class-level variable to store the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SummarizationService, cls).__new__(cls)
            cls._instance._initialize(*args, **kwargs)  # Initialize once
        return cls._instance
    
    def _initialize(
        self,
        llm_name: str = settings.GROQ_LLM_NAME,
        llm_api_key: str = settings.GROQ_API_KEY,
    ):
        self.llm = ChatGroq(
            model_name=llm_name, temperature=0.5, max_tokens=4500, api_key=llm_api_key
        )
        self.newsapi = NewsApiClient(api_key=settings.NEWSAPI_KEY)
        logger.info(f"Centralized GROQ LLM {llm_name} initialized successfully.")

    
    def fetch_news_articles(self, query: str):
        """Retrieves relevant news articles based on extracted key phrases."""
        unique_articles = {}
        articles = self.newsapi.get_everything(
            q=query, language="en", sort_by="relevancy", page=1
        )
        if articles.get("status") == "ok":
            for article in articles["articles"][:5]:
                if article["url"] not in unique_articles:
                    unique_articles[article["url"]] = article

        if not unique_articles:
            return "None"

        context = "\n\n".join(
            [
                f"Title: {a['title']}\nDescription: {a['description']}\nURL: {a['url']}"
                for a in unique_articles.values()
            ]
        )
        summary = self.generate_response(
            NEWS_SUMMARY_PROMPT.format(query=query, context=context)
        )
        return summary

    def generate_response(
        self, prompt: str
    ) -> dict:
        logger.info(f"Generating summary using centralized LLM... {prompt}")
        logger.info(prompt)
        summary = self.llm.invoke(prompt)
        logger.info(f"LLM raw response: {summary}")
        
        return summary.content
