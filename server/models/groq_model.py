import logging
import datetime

from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchResults
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)    

class LLMManager:
    def __init__(self, model_name: str, api_key: str):
        """
        Initialize the LLMManager to interact with Groq and manage the tools.
        
        Args:
            model_name (str): The Groq model name (e.g., "llama3.3-70").
            api_key (str): The Groq API key.
        """
        self.llm = ChatGroq(
            model_name=model_name, 
            api_key=api_key,
            temprature = 0.5,
            max_tokens = 3500
        )
        self.web_search_tool = WebSearchTool()  
        # self.pdf_processing_tool = PdfProcessingTool()  

        # Create tools list that will be passed to the agent
        self.tools = [self.web_search_tool]

        # Initialize the agent with the tools
        self.agent = initialize_agent(
            tools=self.tools,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            llm=self.llm,
            verbose=True,
        )
        logger.info(f"Agent and LLM Initialized successfully \n Time: {datetime.datetime.now()}")

    def run(self, query: str):
        """
        Run the LLM agent with the given query, invoking the appropriate tools as necessary.
        
        Args:
            query (str): The query to be processed.
        
        Returns:
            
        """
        logger.info(f"Running query: {query} \n Time: {datetime.datetime.now()}")
        # Run the query through the agent
        response = self.agent.run(query)
        logger.info(f"{query} executed successfully \n Time: {datetime.datetime.now()}")

        return response
