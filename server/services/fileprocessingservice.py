import os
import logging
import torch
from ffmpeg import FFmpeg
from fastapi import UploadFile
from utils.diarization_utils import Diarization
from utils.summarization_utils import SummarizationService
from services.transcript_processor import TranscriptProcessor
from utils.whisper_utils import transcribe_audio
from utils.const import AUDIO_SUMMARY_PROMPT


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(self):
        self.diarization = Diarization() 
        self.summarization_service = SummarizationService()
        self.transcript_processor = TranscriptProcessor()
    
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
            summary_results = self.summarization_service.generate_summary(self.transcript_processor, formatted_transcript, AUDIO_SUMMARY_PROMPT)
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
    