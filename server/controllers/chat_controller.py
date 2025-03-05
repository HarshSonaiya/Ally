from fastapi import HTTPException, Request
from services import WebSearch
from utils.helper import send_response
import logging
from models.pydantic_models import WebSearchRequest, AnswerQuery
from utils.summarization_utils import SummarizationService
from utils.const import CLASSIFY_PROMPT
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from models.pydantic_models import ClassifyQuery
from langchain.prompts import PromptTemplate
from newsapi import NewsApiClient
from config import settings
from utils.const import NEWS_SUMMARY_PROMPT
from services import ElasticsearchService, FileProcessingService
from utils.const import SUMMARY_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatController:
    """
    Answers various types of user queries such as,
    1. Web Search
    2. Genearl Chat
    3. Audio Files Realted Chat
    4. PDF Files Realted Chat
    5.  News Explainer Chat
    """

    def __init__(self, mongo_client, es_client):
        self.search_service = WebSearch()
        self.summarization_service = SummarizationService()
        self.newsapi = NewsApiClient(api_key=settings.NEWSAPI_KEY)
        self.es_service = ElasticsearchService(es_client)

    async def web_search(self, request: WebSearchRequest):
        """
        Performs web search using a third party API and provides the resutls as context to the LLM
        to answer the user's query.
        """

        try:
            logger.info(f"Web Search request for the query: {request.query}")
            response = await self.search_service.process_query(
                request.query, request.summary_type
            )
            return send_response(200, f"Web Search successfully", data=response)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error creating workspace: {e}"
            )
    
    async def process_query(self, request: Request, query_request: AnswerQuery):
        """
        Classifies the user query into a category like:
        1. General Query
        2. Audio Files Related Query
        3. PDF file related Query
        4. News Explain Query
        """

        try:
            logger.info("Classifying user query.")

            response = self.classify_query(query_request.query)
            logger.info(f"Query classified successfully: {response.category}")

            # Fetch workspace id.
            workspace_id = await self.es_service.get_workspace_id(
                request.state.user_id, query_request.workspace_name
            )
            if response.category == "News Explain Query":
                return self.fetch_news_articles(
                    response.phrases, query_request.query
                )

            elif response.category == "Audio Files Related Query":
                pass

            else:
                response = {
                    "message": "I could not understand the query. Can you please rephrase it and be more specific."
                }
                return send_response(
                    200, f"Query Answered successfully.", response.get("message")
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error answering the query: {e}"
            )

    def classify_query(self, query: str):
        """Classifies the query using a prompt-based LLM model."""
        output_parser = PydanticOutputParser(pydantic_object=ClassifyQuery)
        output_format = output_parser.get_format_instructions()  

        prompt = PromptTemplate(
            template=CLASSIFY_PROMPT,
            input_variables=["context"],
            partial_variables={"output_format": output_format},
        )

        formatted_prompt = prompt.format_prompt(context=query)
        results = self.summarization_service.generate_summary(
            "None", "None", formatted_prompt.to_string()
        )

        return output_parser.parse(results)

    def fetch_news_articles(self, phrases: list, query: str):
        """Retrieves relevant news articles based on extracted key phrases."""
        unique_articles = {}
        for phrase in phrases:
            articles = self.newsapi.get_everything(
                q=phrase, language="en", sort_by="relevancy", page=1
            )
            if articles.get("status") == "ok":
                for article in articles["articles"][:5]:
                    if article["url"] not in unique_articles:
                        unique_articles[article["url"]] = article

        if not unique_articles:
            return send_response(200, "No relevant news found.", "None")

        context = "\n\n".join(
            [
                f"Title: {a['title']}\nDescription: {a['description']}\nURL: {a['url']}"
                for a in unique_articles.values()
            ]
        )
        summary = self.summarization_service.generate_summary(
            "None", "None", NEWS_SUMMARY_PROMPT.format(query=query, context=context)
        )
        logger.info(summary)
        return send_response(200, "News processed successfully.", {"summary": summary})
