import logging
from typing import List
from sentence_transformers import SentenceTransformer
from config import settings
from summarization_utils import summarizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptSummarizer:
    def __init__(self, 
                model_name: str=settings.EMBEDDING_MODEL, 
                token_limit: int=512, 
                overlap_tokens: int=50
            ):
        """
        Initialize the summarization service.

        Args:
            model_name (str): Pretrained embedding model to use.
            summarization_model (str): Pretrained summarization model to use.
            token_limit (int): Maximum number of tokens per chunk.
            overlap_tokens (int): Number of overlapping tokens between chunks.
        """
        self.embedding_model = SentenceTransformer(model_name)
        self.tokenizer = self.embedding_model.tokenizer
        self.token_limit = token_limit
        self.overlap_tokens = overlap_tokens
        logger.info("Transcript Embedding model initialized successfully.")

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

    def process_and_summarize_transcript(self, formatted_segments) -> str:
        """
        Process the formatted segments and generate a summary for the entire transcript.

        Args:
            formatted_segments (list): List of segments with start, end, speaker, and text.

        Returns:
            str: Summary of the entire transcript.
        """

        for segment in formatted_segments:
            start = segment['start']
            end = segment['end']
            speaker = segment['speaker']
            text = segment['text']
            
            # Chunk the text
            logger.info(f"Processing segment: {speaker} from {start} to {end}")
            text_chunks = self.chunk_text(text)
            
            # Generate embeddings
            embeddings = self.generate_embeddings(text_chunks)

            # Store each chunk in Elasticsearch
            for i, embedding in enumerate(embeddings):
                doc = {
                    "start": start,
                    "end": end,
                    "speaker": speaker,
                    "chunk_index": i,
                    "chunk_text": text_chunks[i],
                    "embedding": embedding  # Store embedding as a dense_vector in ES
                }
                self.es.index(index=self.index_name, body=doc)
                logger.info(f"Stored chunk {i} for segment {speaker} ({start} - {end}) in Elasticsearch.")

        # Add speaker info to the text for context
        enriched_segments = [
            f"{segment['speaker']}: {segment['text']}" for segment in formatted_segments
        ]

        # Combine enriched segments into one text
        full_text = " ".join(enriched_segments)

        # Chunk the text
        logger.info("Starting chunking process...")
        text_chunks = self.chunk_text(full_text)

        # Generate embeddings (optional, can be used for semantic analysis later)
        logger.info("Generating embeddings for text chunks...")
        embeddings = self.generate_embeddings(text_chunks)

        # Generate the summary
        logger.info("Generating transcript summary...")
        summary = summarizer.generate_summary

        return {
            "summary":summary,
            "embeddings":embeddings
        }
