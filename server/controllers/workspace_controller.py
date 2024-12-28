from fastapi import HTTPException
from models.pydantic_models import WorkspaceRequest
from services.elasticsearch_service import ElasticsearchService
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkspaceController:

    def __init__(self):
        self.elastic_service = ElasticsearchService()
        
    async def create_workspace(self, workspace: WorkspaceRequest) -> dict:
        """
        Create a new workspace and store its mapping to a unique workspace ID.

        Args:
            workspace_name (str): The name of the workspace.

        Returns:
            dict: Success or error message.
        """
        try:
            await self.elastic_service.create_workspace_index(workspace.workspace_name)
            return {"message": "Workspace created successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating workspace: {e}")
    
    async def get_workspaces(self):
        """
        Retrieve the workspace ID for a given workspace name.

        Returns:
            list: List of workspace names
        """
        try:
            workspaces = await self.elastic_service.get_workspace_mapping()
            return workspaces
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting workspaces: {e}")
        