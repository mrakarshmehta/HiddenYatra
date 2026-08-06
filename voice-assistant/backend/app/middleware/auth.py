import jwt
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifies JWT token for Socket.IO connection authentication."""
    if not token:
        return None
    try:
        # Strip Bearer prefix if present
        if token.startswith("Bearer "):
            token = token[7:]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT authentication failed: Token expired")
        return None
    except jwt.PyJWTError as e:
        logger.warning(f"JWT authentication failed: {e}")
        return None
