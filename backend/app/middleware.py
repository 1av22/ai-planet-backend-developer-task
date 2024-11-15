from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


class TokenAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_routes = ["/auth/login", "/auth/register", "/auth"]
        if any(request.url.path.startswith(route) for route in public_routes):
            return await call_next(request)

        token = request.cookies.get("access_token")
        if not token:
            logger.warning("Authorization token is missing.")
            raise HTTPException(
                status_code=401, detail="Authorization token is missing")

        if not self.validate_token(token):
            logger.warning("Invalid or expired token.")
            raise HTTPException(
                status_code=401, detail="Invalid or expired token")

        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            raise e

    def validate_token(self, token: str) -> bool:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return True
        except JWTError as e:
            logger.error(f"JWT error: {e}")
            return False
