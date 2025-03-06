import logging
from config import settings
from sentence_transformers import SentenceTransformer
from typing import List


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptProcessor():
    """
    Processor for handling transcripts.
    """
    _instance = None

    def __new__(cls, model_name: str = settings.EMBEDDING_MODEL, token_limit: int = 512, overlap_tokens: int = 50):
        if cls._instance is None:
            cls._instance = super(TranscriptProcessor, cls).__new__(cls)
            cls._instance._initialize(model_name, token_limit, overlap_tokens)
            logger.info("TranscriptProcessor initialized with SentenceTransformer.")
        return cls._instance

    def _initialize(self, model_name, token_limit, overlap_tokens):
        self.embedding_model = SentenceTransformer(model_name)
        self.tokenizer = self.embedding_model.tokenizer
        self.token_limit = token_limit
        self.overlap_tokens = overlap_tokens

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
    
    def process_content(self, formatted_segments) -> dict:
        all_segment_embeddings = []
        structured_transcript = []

        for segment in formatted_segments:
            start, end, speaker, text = segment['start'], segment['end'], segment['speaker'], segment['text']
            logger.info(f"Processing segment: {speaker} from {start} to {end}")
            
            text_chunks = self.chunk_text(text)
            embeddings = self.generate_embeddings(text_chunks)
            logger.info("Embedding(s) generated successfully.")
            
            for idx, chunk in enumerate(text_chunks):
                all_segment_embeddings.append({
                    "start": start,
                    "end": end,
                    "chunk": chunk,
                    "embedding": embeddings[idx]
                })

            structured_transcript.append(f"[{start} - {end}] {speaker}: {text}")

        transcript_string = "\n".join(structured_transcript)

        return {
            "transcript": transcript_string,
            "embeddings": all_segment_embeddings
        }
