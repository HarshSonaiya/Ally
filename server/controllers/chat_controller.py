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
from services import ElasticsearchService
from controllers import FileController
from sentence_transformers import SentenceTransformer
from typing import List
from utils.const import summary_prompt

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
        self.es_service = ElasticsearchService()
        self.fc = FileController()
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)

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
        
    def get_embedding(self, query: str) -> List[float]:
        embeddings = self.embedding_model.encode(query, show_progress_bar=True)
        return embeddings
    
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
            workspace_id = await self.fc.get_workspace_id(
                request.state.user_id, query_request.workspace_name
            )
            if response.category == "News Explain Query":
                return self.fetch_news_articles(
                    response.phrases, query_request.query
                )

            elif response.category in [
                "Audio Files Related Query",
                "PDF File Related Query",
            ]:
                retrieved_results = await self.retrieve_relevant_records(response, workspace_id)

                # Generate context for the LLM.
                context = "\n\n".join([
                    f"Start Time: {segment['start']}s | End Time: {segment['end']}s\n"
                    f"Text: {segment['text']}"
                    for segment in retrieved_results
                ])

                # Formulate the prompt.
                prompt  = summary_prompt.format(query=query_request.query, context=context)
                llm_response = self.summarization_service.generate_summary("None", "None", prompt)

                return send_response(200, "Query answered successfully.", {"response": llm_response})

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

    async def retrieve_relevant_records(self, response: ClassifyQuery, workspace_id: str):
        """Fetches relevant documents using keyword-based and embedding search."""

        query_keywords = response.keywords if response.keywords else []
        
        # Get query embedding (768-dimensional)
        query_embedding = self.get_embedding(response.query)
        logger.info(f"Generated query embedding: {query_embedding[:5]}...")  

        should_clauses = []

        # If there are keywords, perform keyword search in transcript & summary
        if query_keywords:
            should_clauses += [{"match": {"summary": kw}} for kw in query_keywords]

        # Dense vector search (always performed)
        vector_search = {
            "nested": {
                "path": "transcript_embeddings",
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'transcript_embeddings.embedding') + 1.0",
                            "params": {"query_vector": query_embedding}
                        }
                    }
                }
            }
        }

        # Final Elasticsearch query
        es_query = {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1 if should_clauses else 0,
                "filter": vector_search  
            }
        }

        # Execute search query
        results = self.es_service.es.search(index=workspace_id, query=es_query, size=10)
        logger.info(f"Elasticsearch response: {results}")

        # Extract timestamps & filter (if required)
        filtered_results = []
        for hit in results["hits"]["hits"]:
            source = hit["_source"]
            if "transcript_embeddings" in source:
                for segment in source["transcript_embeddings"]:
                    if "start" in segment and "end" in segment:
                        filtered_results.append({
                            "text": segment["text"],
                            "start": segment["start"],
                            "end": segment["end"],
                            "score": hit["_score"]
                        })

        if not filtered_results:
            return send_response(200, "No relevant records found.", "None")

        return filtered_results

