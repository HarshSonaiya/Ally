import os
from fastapi import UploadFile
from utils.whisper_utils import transcribe_audio

class FileProcessingService:
    def __init__(self):
        pass 
    
    async def process_audio_video_files(self, file: UploadFile):
        # Ensure the 'uploads' directory exists
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)  

        # Save the file locally
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())  

        # Generate transcript
        transcript = transcribe_audio(file_path)

        return {"transcript": transcript}
