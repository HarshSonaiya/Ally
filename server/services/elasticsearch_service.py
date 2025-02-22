import uuid
import tqdm
from config import get_es_client
from fastapi import HTTPException, Request
import logging
from langchain.docstore.document import Document
from typing import List
from elasticsearch.helpers import bulk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ElasticsearchService:
    def __init__(self):
        self.es = get_es_client()

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
        if self.es.indices.exists(index="workspace_mappings"):
            response = self.es.search(
                    index="workspace_mappings",
                    body={
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {"workspace_name": { "value":workspace_name}}},
                                {"term": {"user_id": { "value":user_id}}}
                            ]
                        }
                    }
                }
            )
            logger.info(response)
            # If any hits are found, the workspace already exists
            if response['hits']['total']['value'] > 0:
                return {"message": f"Workspace {workspace_name} already exists."}

        index_name = uuid.uuid4().hex
        response = self.es.indices.create(
            index=index_name,
            settings={
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            mappings= {
                "properties": {
                    "file_id": { "type": "keyword" },
                    "filename": { "type": "keyword" },
                    "content_type": { "type": "keyword" },
                    "transcript": { "type": "text" },
                    "transcript_embeddings": {
                        "type": "nested",
                        "properties": {
                        "start": { "type": "float" },
                        "end": { "type": "float" },
                        "text": { "type": "text" },
                        "embedding": {
                            "type": "dense_vector",
                            "dims": 768
                        }
                        }
                    },
                    "pdf_text": { "type": "text" },
                    "pdf_embeddings": {
                        "type": "nested",
                        "properties": {
                        "text": { "type": "text" },
                        "embedding": { "type": "dense_vector", "dims": 768 }
                        }
                    }
                }   
            }
        )

        if response.get("acknowledged"):
            await self.store_workspace_mapping(user_id, workspace_name, index_name)
            return {"message": f"Index {workspace_name} created successfully."}
        else:
            return {"message": f"Error creating index {workspace_name}."}
    
    async def store_workspace_mapping(self, user_id: str, workspace_name: str, workspace_id: str) -> dict:
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
                if not self.es.indices.exists(index="workspace_mappings"):
                    self.es.indices.create(
                        index="workspace_mappings",
                        mappings= {
                            "properties": {
                                "workspace_name": {"type": "keyword"},
                                "workspace_id": {"type": "keyword"},
                                "user_id": {"type": "keyword"}
                            }
                        }
                    )

                # Store the workspace mapping
                doc = {
                    "workspace_name": workspace_name,
                    "workspace_id": workspace_id,
                    "user_id": user_id
                }

                self.es.index(index="workspace_mappings", id=workspace_name, body=doc)
                return {"message": f"Workspace mapping for {workspace_name} stored successfully with ID {workspace_id}."}
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
                response = self.es.search(
                    index="workspace_mappings",
                    body={
                        "query": {
                            "bool": {
                                "must": [
                                    {"term": {"user_id": user_id}}  
                                ]
                            }
                        },
                        "_source": ["workspace_name"]  
                    }
                )
                # Extract the source of each document
                workspaces = [hit["_source"]["workspace_name"] for hit in response["hits"]["hits"]]
                return workspaces

            except ConnectionError:
                raise HTTPException(status_code=500, detail="Unable to connect to Elasticsearch.")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error retrieving workspaces: {str(e)}")     
            
    async def store_in_elastic(self, workspace_name: str, filename: str, content_type: str, transcript: str, summary: str, embeddings: list)  -> str:   
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
        doc = {
            "file_id": file_id,
            "filename": filename,
            "content_type": content_type
        }

        if content_type == "transcript":
            doc["transcript"] = transcript
            doc["summary"] = summary
            doc["transcript_embeddings"] = [
                {
                    "start": segment.get("start", 0.0),
                    "end": segment.get("end", 0.0),
                    "text": segment["chunk"],
                    "embedding": segment["embedding"]
                }
                for segment in embeddings
            ]
        try:
            # Index document into Elasticsearch
            self.es.index(index=workspace_name, id=file_id, body=doc)
            logger.info(f"Successfully indexed document with file_id {file_id}")
            
        except Exception as e:
            logger.error(f"Error storing data in Elasticsearch for file {filename}: {str(e)}")
            raise HTTPException(
                status_code=500, 
                detail=f"Error storing data in Elasticsearch: {str(e)}"
            )

    async def index_hybrid_collection(self, chunks: List[Document], brain_id: str, batch_size: int = 64):
        """
        Index the given list of Document chunks into Elasticsearch.
        """
        logger.info(f"Indexing {len(chunks)} documents into Elasticsearch Hybrid Collection.")

        try:
            invalid_chunks = 0
            batched_chunks = [
                chunks[i : i + batch_size] for i in range(0, len(chunks), batch_size)
            ]

            for batch_idx, batch in enumerate(tqdm(batched_chunks, desc="Processing batches")):
                actions = []
                for i, doc in enumerate(batch):
                    try:
                        dense_embedding = self.create_dense_vector(doc.page_content)
                    except Exception as e:
                        logger.exception(f"Error creating dense vector for document {i}: {e}")
                        dense_embedding = None

                    try:
                        sparse_embedding = self.create_sparse_vector(doc.page_content)
                    except Exception as e:
                        logger.exception(f"Error creating sparse vector for document {i}: {e}")
                        sparse_embedding = None

                    if dense_embedding is not None and sparse_embedding is not None:
                        doc_id = str(uuid.uuid4())
                        # Determine content type (transcript or PDF)
                        content_type = "transcript" if "transcript" in doc.metadata else "pdf"

                        actions.append({
                            "_index": self.index_name,
                            "_id": doc_id,
                            "_source": {
                                "brain_id": brain_id,
                                "doc_id": doc_id,
                                "content_type": content_type,
                                "content": doc.page_content,
                                "metadata": doc.metadata,
                                "dense_embedding": dense_embedding,
                                "sparse_embedding": sparse_embedding,
                            },
                        })
                    else:
                        logger.warning(f"Skipping indexing for document {i} due to failed embeddings.")
                        invalid_chunks += 1
                  # Bulk insert into Elasticsearch
                if actions:
                    bulk(self.es_client, actions)
                    logger.info(f"Indexed {len(actions)} documents into Elasticsearch.")

            return invalid_chunks == 0
        except Exception as e:
            logger.exception(f"Error occurred during batch indexing: {e}")
            return False
  
    def retrieve_from_elastic(self, workspace_name: str, file_id: str) -> dict:
        
        try:
            response = self.es.get(index=workspace_name, id=file_id)
            return response["_source"]
        except Exception as e:
            return {"error": f"Error retrieving data from {workspace_name}: {str(e)}"}
