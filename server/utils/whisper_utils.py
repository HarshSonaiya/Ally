import os 
import whisper
import logging
import datetime

from fastapi import UploadFile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def transcribe_audio(file_path: str) -> str:
    
    start_time = datetime.datetime.now()
    
    logger.info(f"Begining transcription \n Time:{start_time}")
    audio = whisper.load_audio(file_path)
    logger.info("Audio loaded successfully")
    model = whisper.load_model("medium")
    logger.info("Model Loaded successfully")
    result = model.transcribe(audio)
    logger.info(f"Trasncription completed \n Time taken for execution: {datetime.datetime.now() - start_time}")
    return result["segments"]
