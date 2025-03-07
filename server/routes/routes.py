from fastapi import APIRouter
from controllers import (
    AuthController,
    FileController,
    ChatController,
    WorkspaceController,
)

def get_routers(mongo_client, es_client): 
    
    # Authentication Route
    auth_router = APIRouter(prefix="/auth", tags=["User Authentication"])
    auth_controller = AuthController(mongo_client, es_client)
    auth_router.get("/google-auth")(auth_controller.google_auth)
    auth_router.get("/google-callback")(auth_controller.google_callback)
    auth_router.post("/exchange-token")(auth_controller.exchange_token)
    auth_router.get("/logout/")(auth_controller.logout)

    # Workspace Routes
    workspace_router = APIRouter(prefix="/workspace", tags=["Workspace"])
    workspace_controller = WorkspaceController(es_client)
    workspace_router.post("/create")(workspace_controller.create_workspace)
    workspace_router.get("/list")(workspace_controller.get_workspaces)

    query_router = APIRouter(tags=["User Query"])
    # File Routes
    file_controller = FileController(es_client)
    query_router.get("/file/list")(file_controller.get_files)
    query_router.post("/file/upload")(file_controller.process_file)

    # Chat Routes
    chat_controller = ChatController(mongo_client, es_client)
    query_router.post("/chat/web-search")(chat_controller.web_search)
    query_router.post("/chat/query")(chat_controller.process_query)
    query_router.post("/playground/query")(chat_controller.process_playground_query)

    # Return the routers
    return [auth_router, workspace_router, query_router]