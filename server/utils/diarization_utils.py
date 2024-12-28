from pyannote.audio import Pipeline
from config.settings import settings
from typing import List, Dict
import torch
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
    
    async def map_transcription_to_diarization(transcription: List[Dict], diarization: List[Dict], tolerance: float = 0.5) -> List[Dict]:
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
    
        logger.info(f"Diarization object type: {type(diarization)}")
        logger.info(f"Diarization object content: {diarization}")
        logger.info(f"Transcription object type: {type(transcription)}")
        logger.info(f"Transcription object content: {transcription}")

        # Process transcription segments
        for trans in transcription:
            logger.info(f"Transcription accessed: {trans} of the type: {type(trans)}")
            trans_start = trans.get('start')
            logger.info("Accessed.")
            trans_end = trans['end']
            trans_text = trans['text']
            
            logger.info("Overlaping begins.")
            # Collect all diarization segments overlapping with this transcription
            overlapping_segments = [
                dia for dia in diarization
                if max(dia['start'], trans_start) - min(dia['end'], trans_end) < tolerance
            ]
            logger.info("Overlaping over.")
            # Handle edge cases: no overlap or multiple overlaps
            if not overlapping_segments:
                # No matching diarization, assign as "UNKNOWN"
                unified_transcript.append({
                    "start": trans_start,
                    "end": trans_end,
                    "speaker": "UNKNOWN",
                    "text": trans_text
                })
            else:
                # Map text to overlapping diarization segments
                for dia in overlapping_segments:
                    overlap_start = max(dia['start'], trans_start)
                    overlap_end = min(dia['end'], trans_end)
                    
                    if overlap_start < overlap_end:
                        # Split transcription text proportionally if needed
                        unified_transcript.append({
                            "start": overlap_start,
                            "end": overlap_end,
                            "speaker": dia['speaker'],
                            "text": trans_text  # Adjust splitting logic for detailed mapping
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

        try:   
            logger.info("Mapping begins.")
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
        except Exception as e :
            logger.error(f"Error here: {e}")

        # Format the result as a single string
        formatted_output = "\n".join(
            f"{speaker}: {' '.join(texts).strip()}" for speaker, texts in speaker_text_mapping.items()
        )

        return formatted_output

    def map_speaker_to_transcription_text1(self, diarization_segments, transcription_segments):
        """
        Map speaker labels from diarization to transcription segments as a structured list.

        Args:
            diarization_segments (list): List of diarization segments with 'start', 'end', and 'speaker'.
            transcription_segments (list): List of transcription segments with 'start', 'end', and 'text'.

        Returns:
            list: List of segments with 'speaker', 'start', 'end', and 'text'.
        """
        combined_segments = []

        for diarization in diarization_segments:
            for transcription in transcription_segments:
                # Check if there's an overlap between diarization and transcription timestamps
                if not (diarization["end"] <= transcription["start"] or diarization["start"] >= transcription["end"]):
                    combined_segments.append({
                        "speaker": diarization["speaker"],
                        "start": max(diarization["start"], transcription["start"]),
                        "end": min(diarization["end"], transcription["end"]),
                        "text": transcription["text"]
                    })

        return combined_segments
    
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
