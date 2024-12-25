from fastapi import APIRouter
# from controllers.auth_controller import AuthController
from controllers.workspace_controller import WorkspaceController
from controllers.file_controller import FileController

# Create an APIRouter to register the routes
router = APIRouter()

# auth_controller = AuthController()
workspace_controller = WorkspaceController()
file_controller = FileController()

# Authentication Routes
# router.post("auth/login-redirect")(auth_controller.login_redirect)
# router.post("auth/google-login-callback/")(auth_controller.google_login_callback)
# # router.get("auth/login/")(auth_controller.login)  
# router.get("auth/user-session-status/")(auth_controller.user_session_status)  

# Workspace Routes
router.post("/workspace/create")(workspace_controller.create_workspace)
router.post("/workspace/list")(workspace_controller.get_workspaces)

# File Routes
router.post("/file/upload")(file_controller.process_file)  

# router.get("auth/logout/")(auth_controller.logout)  
