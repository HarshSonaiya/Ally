import logging
from services.processor import Processor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranscriptProcessor(Processor):
    """
    Processor for handling transcripts.
    """
    def process_content(self, formatted_segments) -> dict:
        all_segment_embeddings = []
        full_transcript = ""
        enriched_segments = []

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

            enriched_segments.append(f"{speaker}: {text}")
        
        full_transcript = " ".join(enriched_segments)
        return {"processed_text": full_transcript, "embeddings": all_segment_embeddings}

