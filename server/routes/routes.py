from fastapi import APIRouter
from controllers import auth_controller, file_controller, workspace_controller, chat_controller

# Create an APIRouter to register the routes
router = APIRouter()

# Authentication Route
router.get("/auth/google-auth")(auth_controller.google_auth)  
router.get("/google-callback")(auth_controller.google_callback)

# Workspace Routes
router.post("/workspace/create")(workspace_controller.create_workspace)
router.get("/workspace/list")(workspace_controller.get_workspaces)

# File Routes
router.get("/file/list")(file_controller.get_files)
router.post("/file/upload/{workspace_id}")(file_controller.process_file)  

# Chat Routes
router.post("/chat/web-search")(chat_controller.web_search)
# Log Out route
router.get("/auth/logout/")(auth_controller.logout)  
