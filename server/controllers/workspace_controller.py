from fastapi import HTTPException
from models.pydantic_models import WorkspaceRequest
from services import elastic_service
import logging
from utils.helper import send_response


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkspaceController:

    def __init__(self):
        self.elastic_service = elastic_service
        
    async def create_workspace(self, workspace: WorkspaceRequest) -> dict:
        """
        Create a new workspace and store its mapping to a unique workspace ID.

        Args:
            workspace_name (str): The name of the workspace.

        Returns:
            dict: Success or error message.
        """
        try:
            logger.info(f"Creating workspace: {workspace.workspace_name}")
            await self.elastic_service.create_workspace_index(workspace.workspace_name)
            return send_response(200, f"Workspace '{workspace.workspace_name}' created successfully", data=workspace.workspace_name)
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
        
workspace_controller = WorkspaceController()
