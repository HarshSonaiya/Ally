from fastapi import HTTPException
from services import WebSearch
from utils.helper import send_response
import logging
from models.pydantic_models import WebSearchRequest
from utils.summarization_utils import SummarizationService
from utils.const import CLASSIFY_PROMPT
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from models.pydantic_models import ClassifyQuery
from langchain.prompts import PromptTemplate
from newsapi import NewsApiClient
from config import settings
from utils.const import NEWS_SUMMARY_PROMPT

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

    def __init__(self):
        self.search_service = WebSearch()
        self.summarization_service = SummarizationService()
        self.newsapi = NewsApiClient(api_key=settings.NEWSAPI_KEY)

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

    async def process_query(self, query: str):
        """
        Classifies the user query into a category like:
        1. General Query
        2. Audio Files Related Query
        3. PDF file related Query
        4. News Explain Query
        """

        try:
            logger.info("Classifying user query.")

            # Initialize the Output parser.
            output_parser = PydanticOutputParser(pydantic_object=ClassifyQuery)
            output_format = output_parser.get_format_instructions()

            # Create the prompt template
            prompt = PromptTemplate(
                template=CLASSIFY_PROMPT,
                input_variables=["context"],
                partial_variables={"output_format": output_format},
            )

            _input = prompt.format_prompt(context=query)

            # Classify the query..
            results = self.summarization_service.generate_summary(
                "None", "None", _input.to_string()
            )
            logger.info(f"Query classified successfuly")

            response = output_parser.parse(results)
            if response.category == "News Explain Query":
                unique_articles = {}  # Store unique URLs to avoid duplicates
                for phrase in response.phrases:
                    articles = self.newsapi.get_everything(
                        q=phrase, language="en", sort_by="relevancy", page=1
                    )
                    logger.info(f"News Search successful for phrase '{phrase}': {len(articles.get('articles', []))} results.")

                    if articles.get("status").lower() == "ok": 
                        for article in articles.get("articles", [])[:5]:  
                            url = article["url"]
                            if url not in unique_articles and article["title"] and article["description"] and article["content"]:
                                unique_articles[url] = {
                                    "title": article["title"],
                                    "description": article["description"],
                                    "content": article["content"],
                                    "url": url
                                }

                if not unique_articles:
                    return send_response(200, "No relevant news articles found.", "None")

                # Prepare context for summarization
                context = "\n\n".join(
                    [f"""
                    Title: {article['title']} \n
                    Description: {article['description']} \n
                    URL: {article['url']}""" for article in unique_articles.values()]
                )
                # Summarize the retrieved news
                summary = self.summarization_service.generate_summary(
                    "None", "None", prompt=NEWS_SUMMARY_PROMPT.format(query=query, context=context)
                )

                return send_response(200, "Query answered successfully.", {"summary": summary})

            elif response.category == "Unknown Query":
                return send_response(
                    200, f"Query Answered successfully.", response.category
                )
            else:
                response = {"message": "I could not understand the query. Can you please rephrase it and be more specific."}
                return send_response(
                    200, f"Query Answered successfully.", response.get("message")
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error answering the query: {e}"
            )
