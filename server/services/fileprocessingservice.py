import os
import logging
import torch
from ffmpeg import FFmpeg
from fastapi import UploadFile
from utils.diarization_utils import Diarization
from utils.summarization_utils import Summarization
from utils.whisper_utils import transcribe_audio
from utils.timestamp_embed_utils import TimestampEmbeddingService
from utils.labse_utils import LaBSEEmbeddingService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileProcessingService:
    def __init__(self):
        self.diarization = Diarization() 
        self.summarize = Summarization()
        # self.labse_service = LaBSEEmbeddingService()
        # self.timestamp_service = TimestampEmbeddingService()
    
    async def process_audio_video_files(self, file: UploadFile):

        try:
            file_path = await self.save_file_temporarily(file)

            wav_file_path = self.convert_to_wav(file_path)

            logger.info(f"Wav file path {wav_file_path}")

            transcript, segments = transcribe_audio(wav_file_path)

            # Perform Diarization 
            diarized_segments = await self.diarization.perform_diarization(wav_file_path) 

            # Map the segments to transcript to ensure no issues with the segments.
            mapped_segments = self.diarization.map_speaker_to_transcription_text(diarized_segments, segments)

            # Generate LaBSE embeddings for the entire transcript
            # transcript_embeddings = self.labse_service.generate_embeddings(transcript)

            # Generate timestamp embeddings for segments
            # timestamp_embeddings = self.timestamp_service.generate_timestamp_embeddings(diarized_segments)

            context = f"""
                Transcript: {transcript}
                Mapped Segments: {mapped_segments}
            """
            summary = self.summarize.generate_summary(context)
            logger.info("Summary is %s ", summary)
            
            return transcript, summary
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
        
    