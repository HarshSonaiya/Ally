import logging
import httpx
from fastapi import HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from services import AuthService, ElasticsearchService
from utils.helper import send_response
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AuthController:
    def __init__(self, mongo_client, es_client):
        self.elastic_service = ElasticsearchService(es_client)
        self.auth_service = AuthService(mongo_client)
        self.es_client = es_client

    async def google_auth(self):
        """
        Redirects user to Google OAuth consent screen.
        """
        google_oauth_url = (
            f"{settings.AUTH_URL}"
            f"?response_type=code"
            f"&client_id={settings.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={settings.REDIRECT_URI}"
            f"&scope=openid email profile"
            f"&access_type=offline"
            f"&include_granted_scopes=true"
            f"&prompt=consent"
        )
        logger.info("Request to signup or login received.")
        return RedirectResponse(google_oauth_url)

    async def google_callback(self, request: Request):
        """
        Fetches the Authorization code sent by google on the google callback url and sends it to the frontned.
        """
        try:
            auth_code = request.query_params.get("code")
            if not auth_code:
                raise HTTPException(
                    status_code=400, detail="Authorization code is required."
                )

            logger.info(f"Authorization code received from Google.")
            return RedirectResponse(
                url=f"{settings.FRONTEND_AUTH_URL}={auth_code}", status_code=303
            )
        except Exception as e:
            logger.error(f"Error in Google auth: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def exchange_token(self, auth_code: str, response: Response):
        """
        Exchanges the authorization code for access token and refresh token and stores the user data.
        """
        try:
            if not auth_code:
                raise HTTPException(
                    status_code=400, detail="Authorization Code is required."
                )

            # Exchange auth code for tokens
            user_info = await self.auth_service.get_user_info(auth_code)
            access_token = user_info.get("access_token")
            refresh_token = user_info.get("refresh_token")
            expires_at = user_info.get("expires_at")

            if not access_token or not refresh_token or not expires_at:
                raise HTTPException(status_code=401, detail="Token Exchange failed.")

            logger.info(
                f"Access and Refresh token received from Google. {access_token} and {refresh_token}"
            )

            logger.info(f"Storing user data.")
            if await self.auth_service.store_user(user_info):
                logger.info(f"User data stored succcessfully.")
            else:
                logger.info(f"Failed to store user data.")

            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=False,
                max_age=60 * 60 * 24 * 30,
            )
            data = {"access_token": access_token, "expires_at": expires_at}
            return send_response(200, "Authentication Successfully.", data)
        except Exception as e:
            logger.error(f"Error exchagning tokens: {e}", exc_info=True)
            return HTTPException(status_code=500, detail=f"Server Error: {e}.")

    async def logout(self, request: Request, response: Response):
        """
        Logout user by invalidating refresh token and clearing cookies.
        """
        try:
            # Invalidate the access token
            async with httpx.AsyncClient() as client:
                google_response = await client.post(
                    settings.REVOKE_TOKEN_URL,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    data={"token": request.state.access_token},
                )
                if google_response.status_code != 200:
                    raise HTTPException(
                        status_code=400, detail="Error revoking access token."
                    )
            response.delete_cookie(key="refresh_token", path="/", domain="localhost")
            return send_response(200, "Logout successful.")
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
