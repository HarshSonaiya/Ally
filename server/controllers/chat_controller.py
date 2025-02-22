from fastapi import HTTPException
from services import WebSearch
from utils.helper import send_response
import logging
from models.pydantic_models import WebSearchRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatController:
    """
    Answers various types of user queries such as,
    1. Web Search
    2. Genearl Chat
    3. Audio Files Realted Chat
    4. PDF Files Realted Chat
    """
    def __init__(self):
        self.search_service = WebSearch()

    async def web_search(self, request: WebSearchRequest):
        """
        Performs web search using a third party API and provides the resutls as context to the LLM 
        to answer the user's query.
        """
        
        try:
            logger.info(f"Web Search request for the query: {request.query}")
            response = await self.search_service.process_query(request.query, request.summary_type)
            return send_response(200, f"Web Search successfully", data=response)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating workspace: {e}")
