import os
import logging
import whisper
import datetime
from fastapi import UploadFile
from utils.diarization_utils import Diarization
from utils.summarization_utils import SummarizationService
from services.transcript_processor import TranscriptProcessor
from utils.const import AUDIO_SUMMARY_PROMPT


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(self):
        self.diarization = Diarization() 
        self.summarization_service = SummarizationService()
        self.transcript_processor = TranscriptProcessor()
    
        
    def transcribe_audio(self, file_path: str) -> str:
        
        start_time = datetime.datetime.now()
        
        logger.info(f"Begining transcription \n Time:{start_time}")
        audio = whisper.load_audio(file_path)
        logger.info("Audio loaded successfully")
        model = whisper.load_model("medium")
        logger.info("Model Loaded successfully")
        result = model.transcribe(audio)
        logger.info(f"Trasncription completed \n Time taken for execution: {datetime.datetime.now() - start_time}")
        return result["segments"]
    
    async def process_audio_video_files(self, file: UploadFile):
        """
        Process the user uploaded audio file and returns the generated transcript and file summary
        """
        try:
            file_extension = os.path.splitext(file.filename)[1].lower()
            logger.info(f"Received file extension: {file_extension}")

            # Validate file type based on content type or extension
            valid_audio_video_extensions = [".wav", ".mp3", ".avi"]

            if file_extension not in valid_audio_video_extensions:
                logger.warning(f"Processing media file {file.filename}")
                return None
            
            file_path = await self.save_file_temporarily(file)
            file_path = os.path.abspath(file_path)
            logger.info(f"filepath: {file_path}")
            
            segments = self.transcribe_audio(file_path)
            
            # Perform Diarization 
            diarized_segments = await self.diarization.perform_diarization(file_path)

            # Map the transcript segments to diarized segemnts.
            formatted_transcript = await self.diarization.map_transcription_to_diarization(segments, diarized_segments)
            logger.info(f"Segments mapped successfully.")

            # Generate full transcript and embeddings.
            processed_data = self.transcript_processor.process_content(formatted_transcript)

            # Generate LaBSE embeddings for the entire transcript
            summary = self.summarization_service.generate_response(formatted_transcript, AUDIO_SUMMARY_PROMPT)
            logger.info(f"Summary and Transcript Embeddings generated successfully")

            logger.info("Summary is %s ", summary)
            
            return {
                "summary": summary,
                "transcript": processed_data.get("transcript", ""),
                "embeddings": processed_data.get("embeddings", [])
            }
        
        except Exception as e :
            logger.error(f"Error : {e}")
            raise Exception
        finally:
            pass
        
    async def save_file_temporarily(self, file: UploadFile):
        """
        Saves the audio file temporarily on the server.
        """
        # Ensure the 'uploads' directory exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)  

        # Save the file locally
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        logger.info(f"File saved temporarily: {file_path}")
        return file_path
    