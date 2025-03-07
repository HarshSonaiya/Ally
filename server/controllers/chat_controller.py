from fastapi import HTTPException, Request
from services import WebSearch
from utils.helper import send_response
import logging
from models.pydantic_models import WebSearchRequest, AnswerQuery
from utils.summarization_utils import SummarizationService
from utils.const import CLASSIFY_PROMPT
from langchain_core.output_parsers.pydantic import PydanticOutputParser
from models.pydantic_models import ClassifyQuery, PlaygroundQueryRequest
from langchain.prompts import PromptTemplate
from services import ElasticsearchService
from utils.const import SUMMARY_PROMPT, PLAYGROUND_PROMPT
from langchain_groq import ChatGroq
from config import settings

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
        3. News Explain Query
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
                summary = self.summarization_service.fetch_news_articles(response.query)
                if summary:
                    return send_response(
                        200, "News processed successfully.", {"summary": summary}
                    )
                else:
                    return send_response(200, "No relevant news found.", "None")

            elif response.category == "Audio Files Related Query":
                return await self.handle_audio_query(workspace_id, response)

            elif response.category == "Audio Files Related Query":
                prompt = PLAYGROUND_PROMPT.format(user_query=query_request.query)
                summary = await self.summarization_service.generate_response(prompt)
                return send_response(
                        200, "Response generated successfully.", {"summary": summary}
                    )
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

    async def process_playground_query(self, request: PlaygroundQueryRequest) -> dict:
        """
        Handles Playground Queries, determining whether it's a user query or an assistant query.
        """
        logger.info(
            f"Initializing Groq LLM {request.model_name} with max_tokens {request.max_tokens} and temperature={request.temperature}"
        )

        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=request.model_name,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        if "user" in request.query_data:
            logger.info("User query detected. Applying general prompt.")
            query = PLAYGROUND_PROMPT.format(user_query=request.query_data["user"])

            logger.info("Generating PLayground LLM Response.")
            response = llm.invoke(query)
        elif "assistant" in request.query_data:
            logger.info("Assistant query detected. Passing directly to LLM.")
            query = request.query_data["assistant"]

            logger.info("Generating PLayground LLM Response.")
            response = llm.invoke(query)
        else:
            return {
                "error": "Invalid query format. Expected 'user' or 'assistant' as key."
            }

        return send_response(200, "Response generated successfully.", response.content)

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
        results = self.summarization_service.generate_response(formatted_prompt.text)

        return output_parser.parse(results)

    async def handle_audio_query(
        self, workspace_id: str, classified_query: ClassifyQuery
    ):
        """
        Processes audio-related queries by retrieving the transcript from Elasticsearch,
        constructing a prompt based on extracted keywords and timestamps, and summarizing the response.
        """

        try:
            logger.info(f"Fetching transcript from workspace: {workspace_id}")

            # Query Elasticsearch to get the transcript
            transcript_data = await self.es_service.get_transcript(workspace_id)
            if not transcript_data:
                return send_response(
                    200, "No transcript found for this workspace.", "None"
                )

            transcript = transcript_data.get("transcript", "")
            logger.info(transcript)

            # Build the context using transcript and extracted query details
            context = (
                f"Transcript:\n{transcript}\n\nUser Query: {classified_query.query}"
            )

            if classified_query.start_timestamp and classified_query.end_timestamp:
                context += f"\nTime stamps are in seconds in context and from user query as well, focus on the segment between {classified_query.start_timestamp} and {classified_query.end_timestamp}."

            elif classified_query.keywords:
                keyword_str = ", ".join(classified_query.keywords)
                context += (
                    f"\nFocus on sections related to these keywords: {keyword_str}."
                )

            # Format the prompt
            prompt = SUMMARY_PROMPT.format(
                context=context, query=classified_query.query
            )

            logger.info("Generating response using SummarizationService.")
            response = self.summarization_service.generate_response(prompt)

            return send_response(
                200, "Audio query processed successfully.", {"summary": response}
            )

        except Exception as e:
            logger.error(f"Error processing audio query: {str(e)}")
            raise HTTPException(
                status_code=500, detail=f"Error processing audio query: {str(e)}"
            )
