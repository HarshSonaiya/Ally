import uuid
from config import settings
from fastapi import HTTPException
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ElasticsearchService:
    def __init__(self, es_client):
        self.es_client = es_client

    async def get_workspace_id(self, user_id: str, workspace_name: str):
        """
        Retrieves the workspace id for the user selected workspace name from the mappings collection.
        """
        mapping_query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"workspace_name": workspace_name}},
                        {"term": {"user_id": user_id}},
                    ]
                }
            },
            "_source": ["workspace_id"],  # Fetch only workspace_id
        }

        mapping_response = self.es_client.search(
            index=settings.MAPPINGS_COLLECTION, body=mapping_query
        )

        if not mapping_response["hits"]["hits"]:
            return {"error": "Workspace not found or unauthorized access."}

        workspace_id = mapping_response["hits"]["hits"][0]["_source"]["workspace_id"]
        return workspace_id

    async def fetch_files(self, user_id: str, workspace_name: str):
        """
        Retrives the user uploaded audio files from a specific workspace from elasticsearch collection.
        """

        # Retrieve the index name from workspace_mappings
        workspace_id = await self.get_workspace_id(user_id, workspace_name)
        logger.info(f"Retrieved workspace id for the workspace name: {workspace_name}")

        # Perform an Elasticsearch search query on the specified workspace index
        query = {"query": {"match_all": {}}}

        # Query Elasticsearch for all documents in the workspace index
        response = self.es_client.search(index=workspace_id, body=query)

        # Check if we got results
        if response["hits"]["total"]["value"] > 0:
            files = []
            for hit in response["hits"]["hits"]:
                # Extract file details
                file_data = hit["_source"]
                files.append(file_data["filename"])
            return files
        else:
            return []  # Return an empty list if no files are found

    async def create_workspace_index(self, user_id: str, workspace_name: str) -> dict:
        """
        Create an index in Elasticsearch for the workspace

        Args:
            workspace_name (str): The user-provided workspace name

        Returns:
            dict: Success or error message
        """
        logger.info(f"User id in create workspace: {user_id}")

        # Check for workspace with existing name
        if self.es_client.indices.exists(index="workspace_mappings"):
            response = self.es_client.search(
                index="workspace_mappings",
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"workspace_name": {"value": workspace_name}}},
                                {"term": {"user_id": {"value": user_id}}},
                            ]
                        }
                    }
                },
            )
            logger.info(response)
            # If any hits are found, the workspace already exists
            if response["hits"]["total"]["value"] > 0:
                return {"message": f"Workspace {workspace_name} already exists."}

        index_name = uuid.uuid4().hex
        response = self.es_client.indices.create(
            index=index_name,
            settings={"number_of_shards": 1, "number_of_replicas": 0},
            mappings={
                "properties": {
                    "file_id": {"type": "keyword"},
                    "filename": {"type": "keyword"},
                    "content_type": {"type": "keyword"},
                    "transcript": {"type": "text"},
                    "transcript_embeddings": {
                        "type": "nested",
                        "properties": {
                            "start": {"type": "float"},
                            "end": {"type": "float"},
                            "text": {"type": "text"},
                            "embedding": {"type": "dense_vector", "dims": 768},
                        },
                    },
                    "pdf_text": {"type": "text"},
                    "pdf_embeddings": {
                        "type": "nested",
                        "properties": {
                            "text": {"type": "text"},
                            "embedding": {"type": "dense_vector", "dims": 768},
                        },
                    },
                }
            },
        )

        if response.get("acknowledged"):
            await self.store_workspace_mapping(user_id, workspace_name, index_name)
            return {"message": f"Index {workspace_name} created successfully."}
        else:
            return {"message": f"Error creating index {workspace_name}."}

    async def store_workspace_mapping(
        self, user_id: str, workspace_name: str, workspace_id: str
    ) -> dict:
        """
        Store the mapping between workspace_name and workspace_id (index name)

        Args:
            workspace_name (str): The user-provided workspace name
            workspace_id (str): The unique ID of the workspace (UUID as the index name)

        Returns:
            dict: Success or error message
        """
        try:
            logger.info(f"User id in store mappings: {user_id}")
            # Ensure the 'workspace_mappings' index exists
            if not self.es_client.indices.exists(index="workspace_mappings"):
                self.es_client.indices.create(
                    index="workspace_mappings",
                    mappings={
                        "properties": {
                            "workspace_name": {"type": "keyword"},
                            "workspace_id": {"type": "keyword"},
                            "user_id": {"type": "keyword"},
                        }
                    },
                )

            # Store the workspace mapping
            doc = {
                "workspace_name": workspace_name,
                "workspace_id": workspace_id,
                "user_id": user_id,
            }

            self.es_client.index(
                index="workspace_mappings", id=workspace_name, body=doc
            )
            return {
                "message": f"Workspace mapping for {workspace_name} stored successfully with ID {workspace_id}."
            }
        except Exception as e:
            return {"error": f"Error storing workspace mapping: {str(e)}"}

    async def get_workspace_mapping(self, user_id: str) -> list:
        """
        Retrieve all workspace mappings.

        Returns:
            list: A list of workspace mappings.
        """
        try:
            # Query to fetch all documents from the workspace_mappings index
            response = self.es_client.search(
                index="workspace_mappings",
                body={
                    "query": {"bool": {"must": [{"term": {"user_id": user_id}}]}},
                    "_source": ["workspace_name"],
                },
            )
            # Extract the source of each document
            workspaces = [
                hit["_source"]["workspace_name"] for hit in response["hits"]["hits"]
            ]
            return workspaces

        except ConnectionError:
            raise HTTPException(
                status_code=500, detail="Unable to connect to Elasticsearch."
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error retrieving workspaces: {str(e)}"
            )

    async def store_in_elastic(
        self,
        workspace_name: str,
        filename: str,
        content_type: str,
        transcript: str,
        summary: str,
        embeddings: list,
    ) -> str:
        """
        Store transcript or PDF text along with embeddings in Elasticsearch.

        Args:
            workspace_name (str): Workspace index.
            filename (str): File name.
            content_type (str): "transcript" or "pdf".
            content (str): Full transcript or extracted PDF text.
            embeddings (list): List of embedding dictionaries.

        Returns:
            str: File ID
        """
        # Generate a unique file ID
        file_id = uuid.uuid4().hex

        # Build the document payload
        doc = {"file_id": file_id, "filename": filename, "content_type": content_type}

        if content_type == "transcript":
            doc["transcript"] = transcript
            doc["summary"] = summary
            doc["transcript_embeddings"] = [
                {
                    "start": segment.get("start", 0.0),
                    "end": segment.get("end", 0.0),
                    "text": segment["chunk"],
                    "embedding": segment["embedding"],
                }
                for segment in embeddings
            ]
        try:
            # Index document into Elasticsearch
            self.es_client.index(index=workspace_name, id=file_id, body=doc)
            logger.info(f"Successfully indexed document with file_id {file_id}")

        except Exception as e:
            logger.error(
                f"Error storing data in Elasticsearch for file {filename}: {str(e)}"
            )
            raise HTTPException(
                status_code=500, detail=f"Error storing data in Elasticsearch: {str(e)}"
            )

    def retrieve_from_elastic(self, workspace_name: str, file_id: str) -> dict:

        try:
            response = self.es_client.get(index=workspace_name, id=file_id)
            return response["_source"]
        except Exception as e:
            return {"error": f"Error retrieving data from {workspace_name}: {str(e)}"}

    async def get_transcript(self, workspace_id: str):
        """Fetches the transcript from the specified workspace collection in Elasticsearch."""
        try:
            response = self.es_client.search(
                index=workspace_id, body={"query": {"match_all": {}}}, size=1000
            )
            logger.info(response)
            hits = response.get("hits", {}).get("hits", [])
            if hits:
                return [
                    hit["_source"] for hit in hits
                ]  # Return a list of transcript records

            return []
        except Exception as e:
            logger.error(f"Error retrieving transcript: {str(e)}")
            return None
