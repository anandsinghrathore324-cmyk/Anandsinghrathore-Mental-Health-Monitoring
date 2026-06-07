import jwt
from flask import request, jsonify
from functools import wraps
from config import Config
from database.user_model import UserModel

def token_required(f):
    """Production JWT validation wrapper middleware securing clinical endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Pull JWT Bearer tokens from request Headers
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({
                "status": "error",
                "message": "Authorization credentials key is missing. Access Denied."
            }), 401
            
        try:
            # Decrypt signature payload using algorithm check
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=["HS256"])
            current_user = UserModel.find_by_id(payload["sub"])
            
            if not current_user:
                return jsonify({
                    "status": "error",
                    "message": "Secure authentication node has expired or user does not exist."
                }), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({
                "status": "error",
                "message": "Security token has expired. Please authenticate again."
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                "status": "error",
                "message": "Invalid decrypt signatures. Access Denied."
            }), 401
            
        return f(current_user, *args, **kwargs)
        
    return decorated
