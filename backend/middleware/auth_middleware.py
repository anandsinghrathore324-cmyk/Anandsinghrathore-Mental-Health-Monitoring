import jwt
import logging
from flask import request, jsonify
from functools import wraps
from config import Config
from database.user_model import UserModel

logger = logging.getLogger(__name__)

def token_required(f):
    """Production JWT validation wrapper middleware securing clinical endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        logger.info(f"[AUTH MIDDLEWARE] Intercepting request to: {request.method} {request.path} from IP: {request.remote_addr}")
        
        # Pull JWT Bearer tokens from request Headers
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                logger.info(f"[AUTH MIDDLEWARE] Found Authorization header. Token extracted (length={len(token)}).")
            else:
                logger.warning("[AUTH MIDDLEWARE] Authorization header present but does not start with 'Bearer '")
        else:
            logger.warning("[AUTH MIDDLEWARE] Authorization header missing from request headers.")
        
        if not token:
            logger.warning(f"[AUTH MIDDLEWARE] Access Denied: Missing auth token for request to {request.path}")
            return jsonify({
                "status": "error",
                "message": "Authorization credentials key is missing. Access Denied."
            }), 401
            
        try:
            # Decrypt signature payload using algorithm check
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            logger.info(f"[AUTH MIDDLEWARE] Token decrypted successfully: sub={payload.get('sub')}, iat={payload.get('iat')}, exp={payload.get('exp')}")
            
            current_user = UserModel.find_by_id(payload["sub"])
            
            if not current_user:
                logger.warning(f"[AUTH MIDDLEWARE] Access Denied: User ID {payload.get('sub')} decoded from token does not exist in database.")
                return jsonify({
                    "status": "error",
                    "message": "Secure authentication node has expired or user does not exist."
                }), 401
            
            logger.info(f"[AUTH MIDDLEWARE] Token validated successfully. Authenticated user ID={current_user['_id']}, email={current_user.get('email')}")
                
        except jwt.ExpiredSignatureError:
            logger.warning(f"[AUTH MIDDLEWARE] Access Denied: Token signature has expired (ExpiredSignatureError).")
            return jsonify({
                "status": "error",
                "message": "Security token has expired. Please authenticate again."
            }), 401
        except jwt.InvalidTokenError:
            logger.warning(f"[AUTH MIDDLEWARE] Access Denied: Token signature is invalid (InvalidTokenError).")
            return jsonify({
                "status": "error",
                "message": "Invalid decrypt signatures. Access Denied."
            }), 401
            
        return f(current_user, *args, **kwargs)
        
    return decorated

