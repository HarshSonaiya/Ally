import uuid
from config.elasticsearch import get_es_client
from fastapi import HTTPException

class ElasticsearchService:
    def __init__(self):
        self.es = get_es_client()

    async def create_workspace_index(self, workspace_name: str) -> dict:
        """
        Create an index in Elasticsearch for the workspace

        Args:
            workspace_name (str): The user-provided workspace name
        
        Returns:
            dict: Success or error message
        """

        # Check for workspace with existing name
        response = self.es.search(
                index="workspace_mappings",
                body={"query": { "match": { "workspace_name": workspace_name } }}
            )
        
        # If any hits are found, the workspace already exists
        if response['hits']['total']['value'] > 0:
            return {"error": f"Workspace {workspace_name} already exists."}

        index_name = uuid.uuid4().hex
        response = self.es.indices.create(
            index=index_name,
            settings={
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            mappings={
                "properties": {
                    "file_id": {"type": "keyword"},
                    "transcript": {"type": "text"},
                    "participants": {"type": "keyword"},
                    "embeddings": {"type": "nested"}
                }
            }
        )
        if response.get("acknowledged"):
            await self.store_workspace_mapping(workspace_name, index_name)
            return {"message": f"Index {index_name} created successfully."}
        else:
            return {"error": f"Error creating index {workspace_name}."}
    
    async def store_workspace_mapping(self, workspace_name: str, workspace_id: str) -> dict:
            """
            Store the mapping between workspace_name and workspace_id (index name)
            
            Args:
                workspace_name (str): The user-provided workspace name
                workspace_id (str): The unique ID of the workspace (UUID as the index name)
            
            Returns:
                dict: Success or error message
            """
            try:
                # Ensure the 'workspace_mappings' index exists
                if not self.es.indices.exists(index="workspace_mappings"):
                    self.es.indices.create(
                        index="workspace_mappings",
                        body={
                            "mappings": {
                                "properties": {
                                    "workspace_name": {"type": "keyword"},
                                    "workspace_id": {"type": "keyword"}
                                }
                            }
                        }
                    )

                # Store the workspace mapping
                doc = {
                    "workspace_name": workspace_name,
                    "workspace_id": workspace_id
                }

                self.es.index(index="workspace_mappings", id=workspace_name, body=doc)
                return {"message": f"Workspace mapping for {workspace_name} stored successfully with ID {workspace_id}."}
            except Exception as e:
                return {"error": f"Error storing workspace mapping: {str(e)}"}
    
    async def get_workspace_mapping(self) -> list:
            """
            Retrieve all workspace mappings.

            Returns:
                list: A list of workspace mappings.
            """
            try:
                # Query to fetch all documents from the workspace_mappings index
                response = self.es.search(
                    index="workspace_mappings",
                    body={"query": {"match_all": {}}}
                )
                # Extract the source of each document
                workspaces = [hit["_source"] for hit in response["hits"]["hits"]]
                return workspaces
            except ConnectionError:
                raise HTTPException(status_code=500, detail="Unable to connect to Elasticsearch.")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error retrieving workspaces: {str(e)}")     
            
    async def store_in_elastic(self, workspace_name: str, transcript: str, participants: list, embeddings: list | None = None) -> dict:
        file_id = uuid.uuid4().hex

        doc = {
            "file_id": file_id,
            "transcript": transcript['transcript'],
            "participants": participants,
            "embeddings": embeddings if embeddings else []
        }

        try:
            self.es.index(index=workspace_name, id=file_id, body=doc)
            return file_id
        except Exception as e:
            return {"error": f"Error storing data in Elasticsearch: {str(e)}"}

    def retrieve_from_elastic(self, workspace_name: str, file_id: str) -> dict:
        
        try:
            response = self.es.get(index=workspace_name, id=file_id)
            return response["_source"]
        except Exception as e:
            return {"error": f"Error retrieving data from {workspace_name}: {str(e)}"}
