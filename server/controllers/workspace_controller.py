from fastapi import HTTPException, Request
from models.pydantic_models import WorkspaceRequest
from services import ElasticsearchService
import logging
from utils.helper import send_response


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkspaceController:

    def __init__(self):
        self.elastic_service = ElasticsearchService()
        
    async def create_workspace(self, request: Request, workspace: WorkspaceRequest) -> dict:
        """
        Create a new workspace and store its mapping to a unique workspace ID.

        Args:
            workspace_name (str): The name of the workspace.

        Returns:
            dict: Success or error message.
        """
        try:
            logger.info(f"Creating workspace: {workspace.workspace_name} and user id: {request.state.user_id}")
            response = await self.elastic_service.create_workspace_index(request.state.user_id, workspace.workspace_name)
            return send_response(200, response.get('message'), data="None")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating workspace: {e}")
    
    async def get_workspaces(self, request: Request):
        """
        Retrieve the workspace ID for a given workspace name.

        Returns:
            list: List of workspace names
        """
        try:
            workspaces = await self.elastic_service.get_workspace_mapping(request.state.user_id)
            return workspaces
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error getting workspaces: {e}")
        