import logging
from config.settings import settings
from langchain_groq import ChatGroq
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Summarization:
    def __init__(self):
        """
        Initialize the Summarization Tool and the LLM.
        """
        self.llm = ChatGroq(
            model_name=settings.GROQ_LLM_NAME,
            temperature=0.5, 
            max_tokens=4500,
            api_key=settings.GROQ_API_KEY
        )  

    def generate_summary(self, context: str):
    
        """
        Generate final summary from the provided context.

        Args: 
            context (str): Contais orignal transcript as well as clustered summaries.
        
        Returns:
            str: Summary of the file.
        """
        prompt = (f"""
            Summarize the following context concisely and focus on the topic, ignoring speaker labels
            which consists of the orignal transcript with the heading "Transcript:" 
            and the Mapped segments after the heading "Mapped Segments:"\n\n {context}.
            Ensure the summary is clear and retains the main points of the text.
          """)

        logger.debug(f"Generated prompt: {prompt}")
        # Invoke the LLM with the prompt
        summary = self.llm.invoke(prompt)
        return summary.content

    