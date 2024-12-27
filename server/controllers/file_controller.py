from fastapi import UploadFile, HTTPException, Depends, BackgroundTasks
from typing import List
from models.pydantic_models import AudioVideoFileRequest
from services.fileprocessingservice import FileProcessingService
from utils.mail_utils import send_email
from services.elasticsearch_service import ElasticsearchService
from starlette.concurrency import run_in_threadpool

import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileController:
    def __init__(self):
        self.file_service = FileProcessingService()
        self.elastic_service = ElasticsearchService()

    async def process_file(self, background_tasks: BackgroundTasks, files: List[UploadFile], body: AudioVideoFileRequest = Depends(), ):
        
        try:
            for file in files:
                file_extension = os.path.splitext(file.filename)[1].lower()
                logger.info(f"Received file extension: {file_extension}")
                
                # Validate file type based on content type or extension 
                valid_audio_video_extensions = [".mp3", ".mp4", ".avi"]

                if file_extension in valid_audio_video_extensions:
                    logger.info(f"Processing media file {file.filename}")
                    transcript, summary = await self.file_service.process_audio_video_files(file)
                    
                elif file_extension == ".pdf":
                    pass
                else:
                    raise HTTPException(status_code=400, detail="Unsupported file type.")  
                
                # Store Transcript in Elasticsearch
                file_id = await self.elastic_service.store_in_elastic(
                    workspace_name=body.workspace_name,
                    transcript=transcript,
                    participants=body.participants,
                    filename=file.filename
                )

                background_tasks.add_task(self.schedule_mail, workspace_name=body.workspace_name, file_id=file_id, summary=summary)
                
                return {
                    "transcript":transcript,
                    "summary":summary
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing data in Elasticsearch: {str(e)}")
    
    async def schedule_mail(self,workspace_name: str, file_id: str, summary: str):
        try:
            logger.info(f"Scheduling email for {file_id} via gmail.")
            await run_in_threadpool(send_email, workspace_name, file_id, summary, self.elastic_service)
            logger.info("Email successfully sent.")
            return {"message": "Email Scheduled to send successfully"}
        except Exception as e:
            logger.error(f"Failed to send email for file_id: {file_id}. Error: {str(e)}")

        