from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
from routes.routes import auth_router, workspace_router, query_router
import logging
from config import settings

app = FastAPI()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
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
    # Exclude specific routes from validation
    excluded_paths = [
        "/auth/google-auth",
        "/",
        "/docs",
        "/favicon.ico",
        "/openapi.json",
        "/auth/google-callback",
        "/refresh-token",
    ]

    if request.url.path in excluded_paths or request.method == "OPTIONS":
        return await call_next(request)

    authorization: str = request.headers.get("Authorization")
    if authorization and authorization.startswith("Bearer "):
        access_token = authorization.split(" ")[1]
        access_token = access_token.strip()
        logger.info(f"Access token received: {access_token}")
        try:
            response = requests.post(settings.TOKEN_INFO_URL, params={"access_token": access_token})
            logger.info(f"Token info response: {response.json()}")
            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid or expired access token")
            logger.info(f"Token info received: {response.json()}")
            token_info = response.json()
            request.state.user_id = token_info.get("user_id")
            request.state.access_token = access_token
        except HTTPException as e:
            return Response(content=e.detail, status_code=e.status_code)
    else:
        return Response(content="Access token missing", status_code=401)

    return await call_next(request)

# Register the routers
app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(query_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Navio!!!"}
