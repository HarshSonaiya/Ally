import os
import logging
import torch
from ffmpeg import FFmpeg
from fastapi import UploadFile
from utils.diarization_utils import Diarization
from utils.summarization_utils import TranscriptSummarizer
from utils.whisper_utils import transcribe_audio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(self):
        self.diarization = Diarization() 
        self.summarizer = TranscriptSummarizer()
    
    async def process_audio_video_files(self, file: UploadFile):

        try:
            file_path = await self.save_file_temporarily(file)

            segments = transcribe_audio(file_path)
            
            # Perform Diarization 
            diarized_segments = await self.diarization.perform_diarization(file_path)

            # Map the transcript segments to diarized segemnts.
            formatted_transcript = await self.diarization.map_transcription_to_diarization(segments, diarized_segments)
            logger.info(f"Segments mapped successfully.")

            # Generate LaBSE embeddings for the entire transcript
            summary_results = self.summarizer.process_and_summarize_transcript(formatted_transcript)
            logger.info(f"Summary and Transcript Embeddings generated successfully")

            logger.info("Summary is %s ", summary_results.get("summary",""))
            
            return {
                "transcript": summary_results.get("transcript", ""),
                "summary": summary_results.get("summary", ""),
                "embeddings": summary_results.get("embeddings", [])
            }
        
        except Exception as e :
            logger.error(f"Error : {e}")
            raise Exception
        finally:
            pass
        
    async def save_file_temporarily(self, file: UploadFile):
        # Ensure the 'uploads' directory exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)  

        # Save the file locally
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        logger.info(f"File saved temporarily: {file_path}")
        return file_path
    