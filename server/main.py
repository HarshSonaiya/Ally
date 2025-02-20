from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from google.auth.transport import requests
from routes.routes import router
from services import auth_service
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("main")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://accounts.google.com/signin"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response


@app.middleware("http")
async def validate_access_token(request: Request, call_next):

    # Exclude authentication and refresh token routes from validation
    logger.info(request.url.path)
    if request.method == "OPTIONS":
        return Response(status_code=200)  # Allow OPTIONS requests

    if request.url.path in ["/auth/google-auth", "/", "/docs", "/favicon.ico", "/openapi.json", "/google-callback", "/refresh-token"]:
        return await call_next(request)

    access_token = request.headers.get("Authorization")
    if access_token and access_token.startswith("Bearer "):
        access_token = access_token.split(" ")[1]
        try:
            user = requests.verify_token(access_token)
            request.state.user = user
        except Exception:
            raise HTTPException(
                status_code=401, detail="Invalid or expired access token"
            )
    else:
        raise HTTPException(status_code=401, detail="Access token missing")

    return await call_next(request)


# Include the PDF processing routes from the controller
app.include_router(router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Navio!!!"}
