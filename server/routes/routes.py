from fastapi import APIRouter
from controllers.authcontroller import AuthController

# Create an APIRouter to register the routes
router = APIRouter()

# Create an instance of the AuthController
auth = AuthController()

# Register the routes with the router
router.post("/auth/google-auth")(auth.login)