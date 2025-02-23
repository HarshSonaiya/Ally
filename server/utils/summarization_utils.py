import logging
from typing import Type
from langchain_groq import ChatGroq
from config import settings
from services.processor import Processor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SummarizationService:
    """
    Centralized summarization service with a shared LLM instance.
    """
    def __init__(self, llm_name: str = settings.GROQ_LLM_NAME, llm_api_key: str = settings.GROQ_API_KEY):
        self.llm = ChatGroq(
            model_name=llm_name,
            temperature=0.5,
            max_tokens=4500,
            api_key=llm_api_key
        )
        logger.info(f"Centralized GROQ LLM {llm_name} initialized successfully.")
    
    def generate_summary(self, processor: Type[Processor], content, prompt: str) -> dict:
        if not content == "None":
            processed_data = processor.process_content(content)
            prompt = prompt.format(context=processed_data["processed_text"])
            logger.info("Generating summary using centralized LLM...")
        summary = self.llm.invoke(prompt)
        return summary.content
        # return {"summary": summary, "processed_data": processed_data}