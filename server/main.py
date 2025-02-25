from fastapi import FastAPI, Request
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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def validate_access_token(request: Request, call_next):
<<<<<<< Updated upstream
    try: 
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
=======
    excluded_paths = [
        "/auth/google-auth",
        "/auth/google-callback",
        "/auth/exchange-token",
        "/",
        "/docs",
        "/favicon.ico",
        "/openapi.json",
        "/refresh-token",
    ]
>>>>>>> Stashed changes

        if request.url.path in excluded_paths or request.method == "OPTIONS":
            return await call_next(request)

    authorization: str = request.headers.get("Authorization")

    if authorization and authorization.startswith("Bearer "):
        access_token = authorization.split(" ")[1].strip()
        logger.info(f"Access token received: {access_token}")
        
        try:
            response = requests.post(settings.TOKEN_INFO_URL, params={"access_token": access_token})
            if response.status_code != 200:
                logger.warning("Invalid or expired access token")
                return JSONResponse(content={"error": "Invalid or expired access token"}, status_code=401)

            token_info = response.json()
            request.state.user_id = token_info.get("user_id")
            request.state.access_token = access_token
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            return JSONResponse(content={"error": "Authentication failed", "detail": str(e)}, status_code=500)
    else:
        logger.warning("Unauthorized request: Access token missing")
        return JSONResponse(content={"error": "Unauthorized request"}, status_code=401)

<<<<<<< Updated upstream
        return await call_next(request)
    except Exception as e:
        logger.info(f"exception: {e}")
        raise HTTPException(status_code=401, detail=e)
=======
    response =  await call_next(request)
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
    return response
>>>>>>> Stashed changes

# Register the routers
app.include_router(auth_router)
app.include_router(workspace_router)
app.include_router(query_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Navio!!!"}
