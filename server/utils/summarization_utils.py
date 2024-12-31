from langchain_groq import ChatGroq
import logging
from typing import List
from sentence_transformers import SentenceTransformer
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptSummarizer:
    def __init__(self, 
                model_name: str=settings.EMBEDDING_MODEL, 
                token_limit: int=512, 
                overlap_tokens: int=50,
                llm_name=settings.GROQ_LLM_NAME,
                llm_api_key=settings.GROQ_API_KEY
            ):
        """
        Initialize the summarization service.

        Args:
            model_name (str): Pretrained embedding model to use.
            token_limit (int): Maximum number of tokens per chunk.
            overlap_tokens (int): Number of overlapping tokens between chunks.
            llm_name (str): Groq's LLM Name
            llm_api_key: Groq's API KEY.
        """
        self.embedding_model = SentenceTransformer(model_name)
        self.tokenizer = self.embedding_model.tokenizer
        self.token_limit = token_limit
        self.overlap_tokens = overlap_tokens
        logger.info("Transcript Embedding model initialized successfully.")
        self.llm = ChatGroq(
            model_name=llm_name,
            temperature=0.5, 
            max_tokens=4500,
            api_key=llm_api_key
        )
        logger.info(f"GROQ LLM {llm_name} initialized successfully.")

    def chunk_text(self, text: str) -> List[str]:
        """
        Chunk text using a sliding window approach with overlap.

        Args:
            text (str): Input text to chunk.

        Returns:
            List[str]: List of text chunks.
        """
        tokens = self.tokenizer(text, truncation=False, add_special_tokens=False)["input_ids"]
        logger.info(f"Text tokenized into {len(tokens)} tokens.")

        token_chunks = []
        for i in range(0, len(tokens), self.token_limit - self.overlap_tokens):
            chunk = tokens[i:i + self.token_limit]
            token_chunks.append(chunk)

        # Decode tokens back into text chunks
        text_chunks = [self.tokenizer.decode(chunk, skip_special_tokens=True) for chunk in token_chunks]
        logger.info(f"{len(text_chunks)} chunks generated successfully with overlap.")
        return text_chunks

    def generate_embeddings(self, text_chunks: List[str]) -> List[float]:
        """
        Generate embeddings for the input text chunks.

        Args:
            text_chunks (list): List of text chunks.

        Returns:
            list: List of embeddings.
        """
        embeddings = self.embedding_model.encode(text_chunks, batch_size=8, show_progress_bar=True)
        return embeddings

    def process_and_summarize_transcript(self, formatted_segments) -> dict:
        """
        Process the formatted segments and generate a summary for the entire transcript.

        Args:
            formatted_segments (list): List of segments with start, end, speaker, and text.

        Returns:
            dict: A dictionary containing the summary and embeddings.
        """

        all_segment_embeddings = []
        full_transcript = ""
        enriched_segments = []

        # Process each segment and generate chunk embeddings
        for segment in formatted_segments:
            start = segment['start']
            end = segment['end']
            speaker = segment['speaker']
            text = segment['text']
            
            # Chunk the text
            logger.info(f"Processing segment: {speaker} from {start} to {end}")
            text_chunks = self.chunk_text(text)
            
            # Generate embeddings for each chunk
            embeddings = self.generate_embeddings(text_chunks)
            logger.info("Embedding(s) generated successfully.")
            
            # Store the segment embeddings along with the start and end times
            for idx, chunk in enumerate(text_chunks):
                segment_embedding = {
                    "start": start,
                    "end": end,
                    "chunk": chunk,
                    "embedding": embeddings[idx]
                }
                all_segment_embeddings.append(segment_embedding)

            # Add speaker info to the text for context
            enriched_segments.append(f"{speaker}: {text}")
        
        # Combine enriched segments into one full transcript text
        full_transcript = " ".join(enriched_segments)

        # Generate the summary by passing the full transcript to the LLM
        logger.info("Generating summary using LLM...")
        summary = self.generate_summary(full_transcript)

        return {
            "summary": summary,
            "transcript":full_transcript,
            "embeddings": all_segment_embeddings
        }
    
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
        # Invoke the LLM with the prompt
        summary = self.llm.invoke(prompt)
        return summary.content

summarizer=TranscriptSummarizer()
    