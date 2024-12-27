import logging 
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

class LaBSEEmbeddingService:
    def __init__(self, model_name="sentence-transformers/LaBSE", token_limit=512):
        """
        Initialize the chunking service with a tokenizer-based approach.

        Args:
            model_name (str): Pretrained model to use.
            token_limit (int): Maximum number of tokens in each chunk.
        """
        self.model = SentenceTransformer(model_name)
        self.tokenizer = self.model.tokenizer()
        self.token_limit = token_limit
        logger.info("LaBSE intialized successfully.")
        
    def chunk_text(self, text):
        """
        Chunk text using the tokenizer and the token limit.

        Args:
            text (str): Input text to chunk.

        Returns:
            list: List of text chunks.
        """
        tokens = self.tokenizer(text, truncation=False, add_special_tokens=False)["input_ids"]
        logger.info(f"Transcript tokenized successfully. {len(tokens)}")
        token_chunks = []

        for i in range(0, len(tokens), self.token_limit):
            token_chunks.append(tokens[i:i + self.token_limit])

        # Decode tokens back into text chunks
        text_chunks = [self.tokenizer.decode(chunk, skip_special_tokens=True) for chunk in token_chunks]

        logger.info(f"{len(text_chunks)} Chunks generated successfully.")
        return text_chunks

    def generate_embeddings(self, text):
        """
        Generate embeddings for the input text using simple chunking.

        Args:
            text (str): Input text.

        Returns:
            list: List of embeddings.
        """
        try:
            logger.info(f"Starting chunk generation.")
            chunks = self.chunk_text(text)

            logger.info("Starting embedding generation.")
            embeddings = self.model.encode(chunks)

            logger.info(f"{len(embeddings)} Embeddings generated successfully.")
            return embeddings
        except Exception :
            raise Exception