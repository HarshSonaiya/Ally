from sentence_transformers import SentenceTransformer

class TimestampEmbeddingService:
    def __init__(self, model_name="paraphrase-MiniLM-L6-v2", token_limit=128):
        """
        Initialize the embedding service with a pretrained model.

        Args:
            model_name (str): The name of the pretrained model.
            token_limit (int): Maximum number of tokens per chunk.
        """
        self.model = SentenceTransformer(model_name)
        self.tokenizer = self.model.tokenizer
        self.token_limit = token_limit

    def chunk_text(self, text):
        """
        Tokenize and chunk the text into smaller parts without setting a limit during tokenization.

        Args:
            text (str): Input text to chunk.

        Returns:
            list: List of text chunks.
        """
        # Tokenize the entire input text into tokens without truncation
        tokens = self.tokenizer(
            text, 
            truncation=False, 
            add_special_tokens=False
        )["input_ids"]
        
        # Chunk the tokens into groups of self.token_limit
        token_chunks = [
            tokens[i:i + self.token_limit] for i in range(0, len(tokens), self.token_limit)
        ]
        
        # Decode token chunks back to text
        text_chunks = [self.tokenizer.decode(chunk, skip_special_tokens=True) for chunk in token_chunks]
        return text_chunks


    def generate_timestamp_embeddings(self, segments):
        """
        Generate embeddings for transcript segments with timestamps.
        Longer segments are chunked into smaller parts.

        Args:
            segments (list): List of transcript segments with timestamps.
                Each segment is a dict with 'start', 'end', and 'text'.

        Returns:
            list: List of embeddings and corresponding metadata.
        """
        results = []

        for segment in segments:
            text = segment["text"]

            # Chunk the text
            chunks = self.chunk_text(text)
            
            # Generate embeddings for the chunks
            chunk_embeddings = self.model.encode(chunks)
            
            # Aggregate chunk embeddings (e.g., average them to get a single representation for the segment)
            segment_embedding = sum(chunk_embeddings) / len(chunk_embeddings)
            
            # Add metadata with timestamps and aggregated embedding
            results.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": text,
                "embedding": segment_embedding.tolist(),
            })

        return results
