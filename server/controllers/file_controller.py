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
    def __init__(self):
        self.file_service = FileProcessingService()
        self.elastic_service = ElasticsearchService()

    async def get_files(self, request: Request, workspace_name: str):
        """
        Retrieves a list of files from the specified workspace index in Elasticsearch.

        :param workspace_name: The name of the workspace, which is also the index name in Elasticsearch.
        :return: List of files in the specified workspace.
        """
        try:
            # Retrieve the index name from workspace_mappings
            workspace_id = await self.get_workspace_id(request.state.user_id, workspace_name)
            logger.info(f"Retrieved workspace id for the workspace name: {workspace_name}")

            # Perform an Elasticsearch search query on the specified workspace index
            query = {"query": {"match_all": {}}}

            # Query Elasticsearch for all documents in the workspace index
            response = self.elastic_service.es.search(
                index=workspace_id, body=query
            )

            # Check if we got results
            if response["hits"]["total"]["value"] > 0:
                files = []
                for hit in response["hits"]["hits"]:
                    # Extract file details
                    file_data = hit["_source"]
                    files.append(
                        {
                            "filename": file_data["filename"],
                            "file_id": file_data["file_id"],
                        }
                    )
                return files
            else:
                return []  # Return an empty list if no files are found
        except Exception as e:
            print(f"Error fetching files from workspace '{workspace_name}': {e}")
            return []

    async def process_file(self, request: Request, workspace_name: str, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
        try:
            results = []
            for file in files:
                file_extension = os.path.splitext(file.filename)[1].lower()
                logger.info(f"Received file extension: {file_extension}")

                # Validate file type based on content type or extension
                valid_audio_video_extensions = [".wav", ".mp4", ".avi"]

                if file_extension in valid_audio_video_extensions:
                    logger.info(f"Processing media file {file.filename}")
                    
                    media_results = await self.file_service.process_audio_video_files(file)
                    logger.info(f"Media processing completed for {file.filename} results: {media_results}")
                    
                    workspace_id = await self.get_workspace_id(request.state.user_id, workspace_name)
                    logger.info(f"Workspace ID: {workspace_id}")

                    # Store Transcript in Elasticsearch
                    file_id = await self.elastic_service.store_in_elastic(
                        workspace_name=workspace_id,
                        filename=file.filename,
                        content_type="transcript",
                        transcript=media_results.get("transcript", ""),
                        summary=media_results.get("summary", ""),
                        embeddings=media_results.get("embeddings", []),
                    )
                    results.append({"filename": file.filename, "summary": media_results.get("summary", "")})

                elif file_extension == ".pdf":
                    pass
                    # logger.info(f"Processing file {file.filename}")
    
                    # all_chunks = []
                    # file_uuid_mapping = {}
                    
                    # # Generate a unique ID for the PDF
                    # pdf_id = str(uuid.uuid4())
                    # file_uuid_mapping[file.filename] = pdf_id
                    # logger.info(
                    #     "Generated unique ID for file %s: %s", file.filename, pdf_id
                    # )

                    # chunks = await pdf_service.extract_content_from_pdf(file)

                    # # Assign metadata to chunks
                    # for chunk in chunks:
                    #     chunk.metadata.update(
                    #         {
                    #             "pdf_id": pdf_id,
                    #             "file_name": file.filename,
                    #             "workspace_id": workspace_id,
                    #         }
                    #     )
                    # all_chunks.extend(chunks)
                    # logger.info(
                    #     "File %s processed and %d chunks generated.",
                    #     file.filename,
                    #     len(chunks),
                    # )

                    # pdf_service.index_hybrid_collection(chunks, workspace_id)

                else:
                    raise HTTPException(
                        status_code=400, detail="Unsupported file type."
                    )

                
                background_tasks.add_task(
                    self.schedule_mail,
                    file_name=file.filename,
                    summary=media_results.get("summary", ""),
                )

            if results:
                return send_response(200, "Files processed successfully.", results)
            else:
                return send_response(500, f"File Upload unsuccessfull.")
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

    async def get_workspace_id(self, user_id: str, workspace_name: str):
        mapping_query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"workspace_name": workspace_name}},
                            {"term": {"user_id": user_id}}
                        ]
                    }
                },
                "_source": ["workspace_id"]  # Fetch only workspace_id
            }

        mapping_response = self.elastic_service.es.search(
            index="workspace_mappings", body=mapping_query
        )

        if not mapping_response["hits"]["hits"]:
            return {"error": "Workspace not found or unauthorized access."}

        workspace_id = mapping_response["hits"]["hits"][0]["_source"]["workspace_id"]
        return workspace_id
    