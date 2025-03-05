from fastapi import UploadFile, HTTPException, File, BackgroundTasks, Request
from fastapi.responses import FileResponse
from typing import List
from utils.helper import send_response
from services import FileProcessingService, ElasticsearchService
from utils.mail_utils import send_email
from starlette.concurrency import run_in_threadpool

import logging
import os
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileController:
    def __init__(self, es_client):
        self.file_service = FileProcessingService()
        self.elastic_service = ElasticsearchService(es_client)

    async def get_files(self, request: Request, workspace_name: str):
        """
        Retrieves a list of files from the specified workspace index in Elasticsearch.

        :param workspace_name: The name of the workspace, which is also the index name in Elasticsearch.
        :return: List of files in the specified workspace.
        """
        try:
            files = await self.elastic_service.fetch_files(
                request.state.user_id,
                workspace_name
            )
            if files: 
                return send_response(200, "Files retrieved successfully.", files)
            else: 
                return send_response(200, "No files found.", files)
        except Exception as e:
            print(f"Error fetching files from workspace '{workspace_name}': {e}")
            return []

    async def process_file(self, request: Request, workspace_name: str, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
        try:
            workspace_id = await self.elastic_service.get_workspace_id(request.state.user_id, workspace_name)
            logger.info(f"Workspace ID fetched successfully.")

            results = []

            for file in files:
                logger.info(f"Received file: {file.filename}")

                media_results = await self.file_service.process_audio_video_files(file)
                if media_results:
                    logger.info(f"Media processing completed for {file.filename}")
                    
                    logger.info(f"Storing {file.filename} processed content in elasticsearch collection.")
                    
                    # Store Transcript in Elasticsearch
                    await self.elastic_service.store_in_elastic(
                        workspace_name=workspace_id,
                        filename=file.filename,
                        content_type="transcript",
                        transcript=media_results.get("transcript", ""),
                        summary=media_results.get("summary", ""),
                        embeddings=media_results.get("embeddings", []),
                    )
                    results.append({"filename": file.filename, "summary": media_results.get("summary", "")})
                else:
                    raise HTTPException(
                        status_code=400, detail=f"Unsupported file type for {file.filename}."
                    )
                
                background_tasks.add_task(
                    self.schedule_mail,
                    file_name=file.filename,
                    summary=media_results.get("summary", ""),
                )

            if results:
                return send_response(200, "Files processed successfully.", results)
            else:
                return send_response(500, f"File Upload unsuccessfull.", None)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error storing data in Elasticsearch: {str(e)}"
            )

    async def schedule_mail(self, file_name: str, summary: str):
        try:
            logger.info(f"Scheduling email for {file_name} via gmail.")
            await run_in_threadpool(
                send_email, file_name, summary
            )
            logger.info("Email successfully sent.")
            return {"message": "Email Scheduled to send successfully"}
        except Exception as e:
            logger.error(
                f"Failed to send email for file: {file_name}. Error: {str(e)}"
            )

    
    # async def remove_file(self, request: RemoveFileRequest) :
    #     pass