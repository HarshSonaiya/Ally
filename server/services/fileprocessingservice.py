import os
import logging
import torch
from ffmpeg import FFmpeg
from fastapi import UploadFile
from utils.diarization_utils import Diarization
from utils.summarization_utils import summarizer
from utils.whisper_utils import transcribe_audio


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(self):
        self.diarization = Diarization() 
        self.summarizer = summarizer
    
    async def process_audio_video_files(self, file: UploadFile):

        try:
            file_path = await self.save_file_temporarily(file)

            wav_file_path = self.convert_to_wav(file_path)

            logger.info(f"Wav file path {wav_file_path}")

            segments = transcribe_audio(wav_file_path)
            
            # Perform Diarization 
            diarized_segments = await self.diarization.perform_diarization(wav_file_path)

            # Map the transcript segments to diarized segemnts.
            formatted_transcript = await self.diarization.map_transcription_to_diarization(segments, diarized_segments)
            logger.info(f"Segments mapped successfully.")

            # Generate LaBSE embeddings for the entire transcript
            summary_results = self.summarizer.process_and_summarize_transcript(formatted_transcript)
            logger.info(f"Summary and Transcript Embeddings generated successfully")

            logger.info("Summary is %s ", summary_results.get("summary",""))
            
            return summary_results
        except Exception as e :
            logger.error(f"Error : {e}")
            raise Exception
        finally:
            os.remove(wav_file_path)
            os.remove(file_path)
 
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
    
    def convert_to_wav(self, input_file_path: str) -> str:
        """
        Convert any audio/video file to .wav format using ffmpeg.
        
        Args:
            input_file_path (str): Path to the input audio or video file.

        Returns:
            str: Path to the converted .wav file.
        """
        wav_file_path = input_file_path.rsplit('.', 1)[0] + '.wav'  # Change extension to .wav

        try:
            ffmpeg = FFmpeg()
            ffmpeg.input(input_file_path).output(
                wav_file_path,
                acodec="pcm_s16le",  
                ar=16000,            
                ac=1).execute()
            
            logger.info(f"Converted {input_file_path} to {wav_file_path}")
            return wav_file_path
        except Exception as e:
            logger.error(f"Error converting file {input_file_path} to .wav: {str(e)}")
            raise e
        
file_processing_service = FileProcessingService()
