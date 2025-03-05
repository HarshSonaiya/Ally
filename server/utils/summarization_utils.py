import logging
from langchain_groq import ChatGroq
from config import settings

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
        logger.info(f"Centralized GROQ LLM {llm_name} initialized successfully.")

    def generate_response(
        self, context, prompt: str
    ) -> dict:
        prompt = prompt.format(context=context)
        logger.info("Generating summary using centralized LLM...")
        summary = self.llm.invoke(prompt)
        
        return summary.content
