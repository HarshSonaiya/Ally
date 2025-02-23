from config import settings
import logging
from sentence_transformers import SentenceTransformer
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Processor:
    """
    Base class for processing different content types (Transcript, PDF, etc.).
    """
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL, token_limit: int = 512, overlap_tokens: int = 50):
        self.embedding_model = SentenceTransformer(model_name)
        self.tokenizer = self.embedding_model.tokenizer
        self.token_limit = token_limit
        self.overlap_tokens = overlap_tokens
        logger.info(f"{self.__class__.__name__} initialized successfully.")

    def chunk_text(self, text: str) -> List[str]:
        tokens = self.tokenizer(text, truncation=False, add_special_tokens=False)["input_ids"]
        logger.info(f"Text tokenized into {len(tokens)} tokens.")

        token_chunks = []
        for i in range(0, len(tokens), self.token_limit - self.overlap_tokens):
            chunk = tokens[i:i + self.token_limit]
            token_chunks.append(chunk)

        text_chunks = [self.tokenizer.decode(chunk, skip_special_tokens=True) for chunk in token_chunks]
        logger.info(f"{len(text_chunks)} chunks generated successfully with overlap.")
        return text_chunks

    def generate_embeddings(self, text_chunks: List[str]) -> List[float]:
        embeddings = self.embedding_model.encode(text_chunks, batch_size=8, show_progress_bar=True)
        return embeddings

    def process_content(self, content):
        raise NotImplementedError("Subclasses must implement process_content method.")

