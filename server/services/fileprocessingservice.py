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
        self.labse_service = LaBSEEmbeddingService()
        self.timestamp_service = TimestampEmbeddingService()
    
    async def process_audio_video_files(self, file: UploadFile):

        try:
            file_path = await self.save_file_temporarily(file)

            wav_file_path = self.convert_to_wav(file_path)

            logger.info(f"Wav file path {wav_file_path}")

            transcript, segments = transcribe_audio(wav_file_path)
            logger.info(f"Segemnts inform: {segments[0]} are of type: {type(segments[0])}")

            # Perform Diarization 
            # diarized_segments = await self.diarization.perform_diarization(wav_file_path) 
            dummy_diarized_segment= [{'id': 0, 'seek': 0, 'start': 0.0, 'end': 6.7, 'text': ' A quantum computer is a digital computer capable of exploiting quantum coherence among the', 'tokens': [50364, 316, 13018, 3820, 307, 257, 4562, 3820, 8189, 295, 12382, 1748, 13018, 26528, 655, 3654, 264, 50699], 'temperature': 0.0, 'avg_logprob': -0.27646356640440045, 'compression_ratio': 1.38135593220339, 'no_speech_prob': 0.5273738503456116}, {'id': 1, 'seek': 0, 'start': 6.7, 'end': 10.0, 'text': ' physical two-state systems that store the binary arithmetic information.', 'tokens': [50699, 4001, 732, 12, 15406, 3652, 300, 3531, 264, 17434, 42973, 1589, 13, 50864], 'temperature': 0.0, 'avg_logprob': -0.27646356640440045, 'compression_ratio': 1.38135593220339, 'no_speech_prob': 0.5273738503456116}]
            # Map the segments to transcript to ensure no issues with the segments.
            # mapped_transcript = self.diarization.map_speaker_to_transcription_text(diarized_segments, segments)

            # combined_segments = self.diarization.map_speaker_to_transcription_text1(diarized_segments,segments)
            formatted_transcript = await self.diarization.map_transcription_to_diarization(segments, dummy_diarized_segment)
            logger.info(f"Formatted Segments: {formatted_transcript}")

            # formatted_segments = self.diarization.format_combined_segments(combined_segments)
            # logger.info(f"Formatted Segments: {formatted_segments}")

            # Generate LaBSE embeddings for the entire transcript
            # transcript_embeddings = self.labse_service.generate_embeddings(mapped_transcript)
            # logger.info(f"Transcript Embeddings generated successfully")

            # Generate timestamp embeddings for segments
            # timestamp_embeddings = self.timestamp_service.generate_timestamp_embeddings(segments)
            # logger.info(f"Time stamp Embeddings generated successfully")

            context = f"""
                Transcript: {transcript}
                Mapped Segments: {mapped_transcript}
            """
            summary = self.summarize.generate_summary(context)
            logger.info("Summary is %s ", summary)
            
            return transcript, summary, [], []
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
        
    