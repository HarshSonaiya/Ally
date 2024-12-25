from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, BackgroundTasks
from models.pydantic_models import AudioVideoFileRequest
from services.fileprocessingservice import FileProcessingService
from utils.mail_utils import send_email
from services.elasticsearch_service import ElasticsearchService
from starlette.concurrency import run_in_threadpool

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileController:
    def __init__(self):
        self.file_service = FileProcessingService()
        self.elastic_service = ElasticsearchService()

    async def process_file(self, background_tasks: BackgroundTasks, file: UploadFile = File(...), body: AudioVideoFileRequest = Depends(), ):
        if file.content_type in ["audio/mpeg", "audio/mp3", "audio/avi", "video/mp4"]:
            logger.info(f"Processing media file {file.filename}")
            transcript = await self.file_service.process_audio_video_files(file)
        elif file.content_type == "application/pdf":
            pass
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
        
        # Store Transcript in Elasticsearch
        try: 
            file_id = await self.elastic_service.store_in_elastic(
                workspace_name=body.workspace_name,
                transcript=transcript,
                participants=body.participants
            )

            background_tasks.add_task(self.schedule_mail, workspace_name=body.workspace_name, file_id=file_id)
            return {"message": "File processed, and email task scheduled successfully."}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error storing data in Elasticsearch: {str(e)}")
    
    async def schedule_mail(self,workspace_name: str, file_id: str):
        try:
            logger.info(f"Scheduling email for {file_id} via gmail.")
            await run_in_threadpool(send_email, workspace_name, file_id, self.elastic_service)
            logger.info("Email successfully sent.")
            return {"message": "Email Scheduled to send successfully"}
        except Exception as e:
            logger.error(f"Failed to send email for file_id: {file_id}. Error: {str(e)}")

        