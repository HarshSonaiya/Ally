from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.middleware.cors import CORSMiddleware
import requests
from contextlib import asynccontextmanager
from routes.routes import get_routers
import logging
import json
from config import settings, db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("main")


# Common security headers
SECURITY_HEADERS = {
    "Access-Control-Allow-Origin": "http://localhost:5173",
    "Access-Control-Allow-Credentials": "true",
    "X-Content-Type-Options": "nosniff",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
}

mongo_client = None
es_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mongo_client, es_client

    try:
        # Initialize database connections
        db_manager.connect()

        mongo_client = db_manager.get_mongo_client()
        es_client = db_manager.get_es_client()

        # Ensure DBs are connected
        if not mongo_client or not es_client or not es_client.ping():
            raise RuntimeError("Database connections failed. Exiting...")

        logger.info("MongoDB and Elasticsearch connected successfully.")

        ## Initialize routers with dependencies
        routers = get_routers(mongo_client, es_client)
        for router in routers:
            app.include_router(router)
            
        yield  # Run the app

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise RuntimeError("Failed to start application.") from e

    finally:
        if mongo_client:
            mongo_client.close()
            logger.info("MongoDB connection closed.")
        if es_client:
            es_client.close()
            logger.info("Elasticsearch connection closed.")


app = FastAPI(lifespan=lifespan)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def validate_access_token(request: Request, call_next):
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

    # Check DB availability
    if not mongo_client or not es_client or not es_client.ping():
        return JSONResponse(
            content={"error": "Service unavailable. Please try again later."},
            status_code=503,
            headers=SECURITY_HEADERS,
        )

    if request.url.path in excluded_paths or request.method == "OPTIONS":
        response = await call_next(request)
        response.headers.update(SECURITY_HEADERS)
        return response

    authorization: str = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Unauthorized request: Access token missing")
        # Return JSON response (Redirect not needed since this comes from the frontend)
        return JSONResponse(
            content=json.dumps({"error": "Unauthorized request"}),
            status_code=401,
            headers=SECURITY_HEADERS,
        )

    access_token = authorization.split(" ")[1].strip()
    logger.info(f"Validating Access Token.")

    try:
        response = requests.post(
            settings.TOKEN_INFO_URL, params={"access_token": access_token}
        )
        if response.status_code != 200:
            logger.warning("Invalid or expired access token")

            if request.url.path == "/auth/google-callback":
                redirect_response = RedirectResponse(
                    url=settings.FRONTEND_ERROR_URL
                )
                redirect_response.delete_cookie("refresh_token")
                redirect_response.headers.update(SECURITY_HEADERS)
                logger.warning("Invalid access token")
                return redirect_response

            response = Response(
                content=json.dumps({"error": "Expired access token"}),
                status_code=401,
                headers=SECURITY_HEADERS,
            )
            response.delete_cookie("refresh_token")
            logger.warning("Expired access token")
            return response

        token_info = response.json()
        request.state.user_id = token_info.get("user_id")
        request.state.access_token = access_token

    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        return JSONResponse(
            content=json.dumps({"error": f"Authentication failed: {str(e)}"}),
            status_code=500,
            headers=SECURITY_HEADERS,
        )

    response = await call_next(request)
    response.headers.update(SECURITY_HEADERS)
    return response


@app.get("/")
def read_root():
    return {"message": "Welcome to Ally!!!"}
