from pyannote.audio import Pipeline
from config.settings import settings
from typing import List, Dict
import torch
import logging

from fastapi import UploadFile

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
            use_auth_token= settings.HUGGING_FACE_ACCESS_TOKEN
        )
    async def perform_diarization(self, audio_file: str):
        """
        Send audio file to huggingface api for diarization

        Args:
            audio_file_path (str): Path to the audio file.

        Returns:
            dict: Diarization response from the API.
        """
        logger.info(f"Performing diarization on file")
        # run the pipeline on an audio file
        if self.pipeline:
            logger.info("Initialization successfully")
        else:
            logger.error("issue in pipeline")

        # self.pipeline.to(torch.device("cuda"))

        diarization = self.pipeline(audio_file)

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
    
    async def map_transcription_to_diarization(self, transcription: List[Dict], diarization: List[Dict], tolerance: float = 0.5) -> List[Dict]:
        """
        Maps transcription segments to speaker diarization segments.
        
        Args:
            transcription (List[Dict]): List of transcription segments with `start`, `end`, and `text`.
            diarization (List[Dict]): List of diarization segments with `start`, `end`, and `speaker`.
            tolerance (float): Time tolerance in seconds for aligning transcription and diarization.

        Returns:
            List[Dict]: Unified transcript with speaker attribution and text.
        """
        # Resultant unified transcript
        unified_transcript = []
        logger.info("Mapping begins.")

        # Process transcription segments
        for segment in transcription:
            segment_start = segment['start']
            segment_end = segment['end']
            segment_text = segment['text']

            # Collect all diarization segments overlapping with this transcription
            overlapping_segments = [
                dia for dia in diarization
                if max(dia['start'], segment_start) - min(dia['end'], segment_end) < tolerance
            ]

            # Handle edge cases: no overlap or multiple overlaps
            if not overlapping_segments:
                # No matching diarization, assign as "UNKNOWN"
                unified_transcript.append({
                    "start": segment_start,
                    "end": segment_end,
                    "speaker": "UNKNOWN",
                    "text": segment_text
                })
            else:
                # Map text to overlapping diarization segments
                for dia in overlapping_segments:
                    overlap_start = max(dia['start'], segment_start)
                    overlap_end = min(dia['end'], segment_end)
                    
                    if overlap_start < overlap_end:
                        # Split transcription text proportionally if needed
                        unified_transcript.append({
                            "start": overlap_start,
                            "end": overlap_end,
                            "speaker": dia['speaker'],
                            "text": segment_text  # Adjust splitting logic for detailed mapping
                        })
        
        # Merge adjacent segments with the same speaker
        merged_transcript = []
        for seg in unified_transcript:
            if merged_transcript and seg['speaker'] == merged_transcript[-1]['speaker']:
                # Extend the previous segment
                merged_transcript[-1]['end'] = seg['end']
                merged_transcript[-1]['text'] += " " + seg['text']
            else:
                # Add a new segment
                merged_transcript.append(seg)
        
        return merged_transcript
    
    def format_combined_segments(self, combined_segments):
        """
        Format combined segments into a unified transcript string.

        Args:
            combined_segments (list): List of segments with 'speaker', 'start', 'end', and 'text'.

        Returns:
            str: Unified transcript string.
        """
        formatted_transcript = "\n".join(
            f"[{segment['start']:.2f}-{segment['end']:.2f}] {segment['speaker']}: {segment['text']}"
            for segment in combined_segments
        )
        return formatted_transcript
