from pyannote.audio import Pipeline
from config.settings import settings
import torch
from sklearn.cluster import AgglomerativeClustering
import numpy as np
import logging

# Configure the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class Diarization:
    def __init__(self):
        """
        Initialize the diarization tool.

        Args:
            diarization_model (str): Pretrained model for speaker diarization.
        """
        self.pipeline = Pipeline.from_pretrained(
            settings.DIARIZATION_MODEL_NAME,
            use_auth_token= settings.HUGGING_FACE_API_KEY
        )
    async def perform_diarization(self, audio_file_path: str):
        """
        Send audio file to huggingface api for diarization

        Args:
            audio_file_path (str): Path to the audio file.

        Returns:
            dict: Diarization response from the API.
        """
        logger.info(f"Performing diarization on file: {audio_file_path}")
        # run the pipeline on an audio file
        if self.pipeline:
            logger.info("Initialization successfully")
        else:
            logger.error("issue in pipeline")

        # self.pipeline.to(torch.device("cuda"))

        diarization = self.pipeline(audio_file_path)

        logger.info(f"Diarized content: {diarization} ")
        speaker_segments = []
        for segment, _, label in diarization.itertracks(yield_label=True):
            speaker_segments.append({
                "start": segment.start,
                "end": segment.end,
                "speaker": label
        })

        logger.info(f"Diarization completed. {len(speaker_segments)} segments found.")
        return speaker_segments
        
    def map_speaker_to_transcription_text(self, diarization_segments, transcription_segments):
        """
        Map speaker labels from diarization output to transcription output and format as a single string.

        Args:
            diarization_segments (list): List of diarization segments with 'start', 'end', and 'speaker'.
            transcription_segments (list): List of transcription segments with 'start', 'end', and 'text'.

        Returns:
            str: Formatted string with speakers and their corresponding text.
        """
        speaker_text_mapping = {}

        for diarization in diarization_segments:
            for transcription in transcription_segments:
                # Check if there's an overlap between diarization and transcription timestamps
                if not (diarization["end"] <= transcription["start"] or diarization["start"] >= transcription["end"]):
                    # Get the speaker ID (e.g., 'SPEAKER_00' -> 'Speaker 0')
                    speaker_id = diarization["speaker"].replace("SPEAKER_", "Speaker ")
                    # Initialize speaker text if not already present
                    if speaker_id not in speaker_text_mapping:
                        speaker_text_mapping[speaker_id] = []
                    # Append the transcription text to the speaker's list
                    speaker_text_mapping[speaker_id].append(transcription["text"])

        # Format the result as a single string
        formatted_output = "\n".join(
            f"{speaker}: {' '.join(texts).strip()}" for speaker, texts in speaker_text_mapping.items()
        )

        return formatted_output
