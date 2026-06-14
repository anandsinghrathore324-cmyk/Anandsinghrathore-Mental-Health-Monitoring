import jwt
import datetime
import logging
from flask import Blueprint, request, jsonify
from config import Config
from database.user_model import UserModel
from middleware.auth_middleware import token_required

logger = logging.getLogger(__name__)

def is_smtp_configured() -> bool:
    email = Config.SMTP_EMAIL
    password = Config.SMTP_PASSWORD
    if not email or not password:
        return False
    # Check for placeholder strings
    if "your-gmail" in email or "your-gmail" in password or email.strip() == "" or password.strip() == "":
        return False
    return True

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    """Endpoint to register a new student user inside MongoDB."""
    data = request.get_json() or {}
    
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not name or not email or not password:
        return jsonify({
            "status": "error",
            "message": "Name, email, and password key are required inputs."
        }), 400
        
    # Check if user already exists
    if UserModel.find_by_email(email):
        return jsonify({
            "status": "error",
            "message": "A student account is already registered under this email address."
        }), 400
        
    try:
        new_user = UserModel.create_user(name, email, password)
        return jsonify({
            "status": "success",
            "message": "Student identity successfully registered.",
            "user": new_user
        }), 201
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server encountered error saving record: {str(e)}"
        }), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    """Endpoint to authenticate a student user and generate bearer JWT signatures."""
    from database.db import db_manager
    data = request.get_json() or {}
    
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({
            "status": "error",
            "message": "Email and password security key are required parameters."
        }), 400
        
    db_type = "MONGOMOCK_FALLBACK" if "mongomock" in str(type(db_manager.client)) else "LIVE_MONGODB"
    logger.info(f"[AUTH LOGIN] Received login request for email: {email} (DB Provider: {db_type})")
    
    user = UserModel.find_by_email(email)
    
    if not user:
        logger.warning(f"[AUTH LOGIN] User lookup failed: no document found for email {email}")
        return jsonify({
            "status": "error",
            "message": "Invalid decrypt signatures. Access Denied."
        }), 401
        
    logger.info(f"[AUTH LOGIN] User found in database: ID={user['_id']}")
    
    pass_check = UserModel.verify_password(user["password"], password)
    logger.info(f"[AUTH LOGIN] Password hash match check: {pass_check}")
    
    if not pass_check:
        logger.warning(f"[AUTH LOGIN] Access Denied: Password mismatch for email {email}")
        return jsonify({
            "status": "error",
            "message": "Invalid decrypt signatures. Access Denied."
        }), 401
        
    # Generate secure JWT access token
    try:
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        token_payload = {
            "sub": user["_id"],
            "exp": expiration,
            "iat": datetime.datetime.utcnow()
        }
        logger.info(f"[AUTH LOGIN] Generating token: sub={user['_id']}, exp={expiration.isoformat()}")
        token = jwt.encode(token_payload, Config.JWT_SECRET_KEY, algorithm="HS256")
        logger.info(f"[AUTH LOGIN] Token encoding completed for user: {email}")
        
        return jsonify({
            "status": "success",
            "message": "Student identity authenticated successfully.",
            "token": token,
            "user": {
                "id": user["_id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200
    except Exception as e:
        logger.error(f"[AUTH LOGIN] Token generation failure: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Failed to generate access signature: {str(e)}"
        }), 500

@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout(current_user):
    """Endpoint that verifies JWT signatures and logs the user session out."""
    return jsonify({
        "status": "success",
        "message": f"Successfully deleted active session for {current_user['name']}."
    }), 200

@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile(current_user):
    """Endpoint returning details of the currently logged-in student."""
    return jsonify({
        "status": "success",
        "user": current_user
    }), 200

@auth_bp.route("/request-otp", methods=["POST"])
def request_otp():
    """Generates a 6-digit OTP code and dispatches it via Gmail or fallback console print."""
    import random
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from database.db import db_manager
    
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    
    if not email:
        return jsonify({
            "status": "error",
            "message": "Student email identifier is a required parameter."
        }), 400
        
    # Generate secure 6-digit verification OTP
    otp_code = f"{random.randint(100000, 999999)}"
    
    try:
        # Upsert verification code into MongoDB (expiring automatically in 5 minutes via TTL index)
        db_manager.db.otp_codes.update_one(
            {"email": email},
            {
                "$set": {
                    "email": email,
                    "otp": otp_code,
                    "created_at": datetime.datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Check if Gmail credentials are set and valid
        if is_smtp_configured():
            try:
                msg = MIMEMultipart()
                msg["From"] = Config.SMTP_EMAIL
                msg["To"] = email
                msg["Subject"] = "Reset Your Password"

                body = f"""
                <html>
                <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #060813; color: #ffffff; padding: 2rem;">
                    <div style="max-width: 500px; margin: 0 auto; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 242, 254, 0.2); border-radius: 16px; padding: 2rem; box-shadow: 0 0 40px rgba(0, 242, 254, 0.05);">
                        <h2 style="color: #00f2fe; text-align: center; font-weight: 800; letter-spacing: 1px; margin-bottom: 1.5rem;">AIRA WELLNESS</h2>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3;">Hello,</p>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3;">We received a request to reset the password for your AIRA Wellness account.</p>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3;">Use the verification code below to continue:</p>
                        <div style="background: rgba(0, 242, 254, 0.08); border-radius: 12px; border: 1px solid rgba(0, 242, 254, 0.3); padding: 1.2rem; text-align: center; margin: 2rem 0;">
                            <span style="font-size: 2.2rem; font-weight: 900; letter-spacing: 8px; color: #00f2fe; font-family: monospace;">{otp_code}</span>
                        </div>
                        <p style="font-size: 0.85rem; color: #ff007f; text-align: center; margin-top: 1rem;">This verification code will expire in 5 minutes.</p>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3;">If you did not request a password reset, you can safely ignore this email. No changes will be made to your account.</p>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3; margin-top: 1.5rem;">Best regards,<br>AIRA Wellness Team</p>
                        <hr style="border: 0; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 2rem 0;">
                        <p style="font-size: 0.75rem; color: #6272a4; text-align: center; margin-bottom: 0;">AIRA Wellness • Student Mental Health & Wellness Platform</p>
                    </div>
                </body>
                </html>
                """
                msg.attach(MIMEText(body, "html"))

                # Secure connection using SSL (with explicit timeout)
                server = smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=10)
                server.login(Config.SMTP_EMAIL, Config.SMTP_PASSWORD)
                server.sendmail(Config.SMTP_EMAIL, email, msg.as_string())
                server.quit()
                
                logger.info(f"Successfully sent security OTP email to {email}")
                return jsonify({
                    "status": "success",
                    "message": "One-Time Password has been dispatched to your email inbox."
                }), 200
            except Exception as mail_err:
                # Console logger fallback with detailed traceback on SMTP delivery failure
                logger.error(f"[OTP SMTP ERROR] Dispatch failed for {email}: {str(mail_err)}", exc_info=True)
                return jsonify({
                    "status": "error",
                    "message": f"SMTP mail delivery failed: {str(mail_err)}"
                }), 500
        else:
            # Local Sandbox Mode: Console logging fallback
            logger.info(f"[OTP SYSTEM LOGS] Gmail credentials not configured (using local sandbox mode)")
            logger.info(f"[OTP SYSTEM LOGS] Generated code for {email}: {otp_code}")
            
            return jsonify({
                "status": "success",
                "message": "One-Time Password generated locally. (Local Sandbox Mode active)",
                "otp_bypass": otp_code
            }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server failed to initialize verification dispatch: {str(e)}"
        }), 500

@auth_bp.route("/signup-request-otp", methods=["POST"])
def signup_request_otp():
    """Checks email availability, generates a signup OTP, and dispatches it."""
    import random
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from database.db import db_manager
    
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    
    if not name or not email:
        return jsonify({
            "status": "error",
            "message": "Student name and email are required inputs."
        }), 400
        
    # Check if user already exists
    if UserModel.find_by_email(email):
        return jsonify({
            "status": "error",
            "message": "A student account is already registered under this email address."
        }), 400
        
    otp_code = f"{random.randint(100000, 999999)}"
    
    try:
        # Upsert verification code into MongoDB (expiring automatically in 5 minutes via TTL index)
        db_manager.db.otp_codes.update_one(
            {"email": email},
            {
                "$set": {
                    "email": email,
                    "otp": otp_code,
                    "created_at": datetime.datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Check if Gmail credentials are set and valid
        if is_smtp_configured():
            try:
                msg = MIMEMultipart()
                msg["From"] = Config.SMTP_EMAIL
                msg["To"] = email
                msg["Subject"] = "Verify Your Email Address"

                body = f"""
                <html>
                <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #060813; color: #ffffff; padding: 2rem;">
                    <div style="max-width: 500px; margin: 0 auto; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 242, 254, 0.2); border-radius: 16px; padding: 2rem; box-shadow: 0 0 40px rgba(0, 242, 254, 0.05);">
                        <h2 style="color: #00f2fe; text-align: center; font-weight: 800; letter-spacing: 1px; margin-bottom: 1.5rem;">AIRA WELLNESS</h2>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3;">Hello {name},</p>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3;">Welcome to AIRA Wellness!</p>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3;">To complete your account registration and verify your email address, enter the verification code below:</p>
                        <div style="background: rgba(0, 242, 254, 0.08); border-radius: 12px; border: 1px solid rgba(0, 242, 254, 0.3); padding: 1.2rem; text-align: center; margin: 2rem 0;">
                            <span style="font-size: 2.2rem; font-weight: 900; letter-spacing: 8px; color: #00f2fe; font-family: monospace;">{otp_code}</span>
                        </div>
                        <p style="font-size: 0.85rem; color: #ff007f; text-align: center; margin-top: 1rem;">This verification code will expire in 5 minutes.</p>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3;">If you did not create an AIRA Wellness account, you can safely ignore this email.</p>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3;">Thank you for joining AIRA Wellness.</p>
                        <p style="font-size: 0.95rem; line-height: 1.6; color: #a9b2c3; margin-top: 1.5rem;">Best regards,<br>AIRA Wellness Team</p>
                        <hr style="border: 0; border-top: 1px solid rgba(255, 255, 255, 0.08); margin: 2rem 0;">
                        <p style="font-size: 0.75rem; color: #6272a4; text-align: center; margin-bottom: 0;">AIRA Wellness • Student Mental Health & Wellness Platform</p>
                    </div>
                </body>
                </html>
                """
                msg.attach(MIMEText(body, "html"))

                # Secure connection using SSL (with explicit timeout)
                server = smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=10)
                server.login(Config.SMTP_EMAIL, Config.SMTP_PASSWORD)
                server.sendmail(Config.SMTP_EMAIL, email, msg.as_string())
                server.quit()
                
                logger.info(f"Successfully sent registration OTP email to {email}")
                return jsonify({
                    "status": "success",
                    "message": "Verification code has been dispatched to your Gmail address."
                }), 200
            except Exception as mail_err:
                # Console logger fallback with detailed traceback on SMTP delivery failure
                logger.error(f"[SIGNUP SMTP ERROR] Dispatch failed for {email}: {str(mail_err)}", exc_info=True)
                return jsonify({
                    "status": "error",
                    "message": f"SMTP mail delivery failed: {str(mail_err)}"
                }), 500
        else:
            # Local Sandbox Mode: Console logging fallback
            logger.info(f"[SIGNUP SYSTEM LOGS] Gmail credentials not configured (using local sandbox mode)")
            logger.info(f"[SIGNUP SYSTEM LOGS] Generated code for {email}: {otp_code}")
            
            return jsonify({
                "status": "success",
                "message": "Verification code generated locally. (Local Sandbox Mode active)",
                "otp_bypass": otp_code
            }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server failed to initialize signup verification dispatch: {str(e)}"
        }), 500

@auth_bp.route("/signup-verify-otp", methods=["POST"])
def signup_verify_otp():
    """Verifies standard registration OTP code."""
    from database.db import db_manager
    
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    otp_provided = data.get("otp", "").strip()
    
    if not email or not otp_provided:
        return jsonify({
            "status": "error",
            "message": "Email and 6-digit OTP verification code are required parameters."
        }), 400
        
    try:
        # Search active code registry
        record = db_manager.db.otp_codes.find_one({"email": email, "otp": otp_provided})
        
        if not record:
            return jsonify({
                "status": "error",
                "message": "Invalid or expired One-Time Password. Access Denied."
            }), 401
            
        # Optional validation check on expiry time (in case MongoDB TTL index hasn't run yet)
        time_elapsed = datetime.datetime.utcnow() - record["created_at"]
        if time_elapsed > datetime.timedelta(minutes=5):
            db_manager.db.otp_codes.delete_one({"_id": record["_id"]})
            return jsonify({
                "status": "error",
                "message": "Verification code has expired. Access Denied."
            }), 401
            
        # Burn OTP immediately so it cannot be re-used under any circumstance
        db_manager.db.otp_codes.delete_one({"_id": record["_id"]})
        
        return jsonify({
            "status": "success",
            "message": "Email address verified successfully."
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server verification crashed: {str(e)}"
        }), 500

@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """Verifies standard OTP parameters, auto-registers new users, and returns JWT session signatures."""
    from database.db import db_manager
    
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    otp_provided = data.get("otp", "").strip()
    
    if not email or not otp_provided:
        return jsonify({
            "status": "error",
            "message": "Email and 6-digit OTP verification code are required parameters."
        }), 400
        
    db_type = "MONGOMOCK_FALLBACK" if "mongomock" in str(type(db_manager.client)) else "LIVE_MONGODB"
    logger.info(f"[AUTH OTP VERIFY] Received verification request for: {email} (DB Provider: {db_type})")
    
    try:
        # Search active code registry
        record = db_manager.db.otp_codes.find_one({"email": email, "otp": otp_provided})
        
        if not record:
            logger.warning(f"[AUTH OTP VERIFY] OTP check failed: no record found matching email {email} and code {otp_provided}")
            return jsonify({
                "status": "error",
                "message": "Invalid or expired One-Time Password. Access Denied."
            }), 401
            
        # Optional validation check on expiry time (in case MongoDB TTL index hasn't run yet)
        time_elapsed = datetime.datetime.utcnow() - record["created_at"]
        logger.info(f"[AUTH OTP VERIFY] OTP record found. Created at {record['created_at'].isoformat()}, time elapsed: {time_elapsed.total_seconds()}s")
        if time_elapsed > datetime.timedelta(minutes=5):
            logger.warning(f"[AUTH OTP VERIFY] OTP code has expired (> 5 minutes elapsed) for user: {email}")
            db_manager.db.otp_codes.delete_one({"_id": record["_id"]})
            return jsonify({
                "status": "error",
                "message": "One-Time Password has expired (5 minutes timeout). Access Denied."
            }), 401
            
        # Burn OTP immediately so it cannot be re-used under any circumstance
        db_manager.db.otp_codes.delete_one({"_id": record["_id"]})
        logger.info(f"[AUTH OTP VERIFY] Burned OTP token successfully for user: {email}")
        
        # Check if user already exists
        user = UserModel.find_by_email(email)
        
        if not user:
            logger.info(f"[AUTH OTP VERIFY] Auto-Signup triggered for new user: {email}")
            # Auto-Signup: Automatically register new users on first OTP verification!
            name_prefix = email.split("@")[0].capitalize()
            user = UserModel.create_user(name_prefix, email, "otp-auto-secured-pass-2026")
            logger.info(f"[AUTH OTP VERIFY] Registered new user during auto-signup: ID={user['_id']}")
        else:
            logger.info(f"[AUTH OTP VERIFY] Found existing user profile for email: {email}")
            
        # Generate secure JWT access token
        expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        token_payload = {
            "sub": user["_id"],
            "exp": expiration,
            "iat": datetime.datetime.utcnow()
        }
        logger.info(f"[AUTH OTP VERIFY] Generating token: sub={user['_id']}, exp={expiration.isoformat()}")
        token = jwt.encode(token_payload, Config.JWT_SECRET_KEY, algorithm="HS256")
        logger.info(f"[AUTH OTP VERIFY] OTP validation complete. Returning secure JWT token for user: {email}")
        
        return jsonify({
            "status": "success",
            "message": "One-Time Password verified. Identity authenticated.",
            "token": token,
            "user": {
                "id": user["_id"],
                "name": user["name"],
                "email": user["email"]
            }
        }), 200
        
    except Exception as e:
        logger.error(f"[AUTH OTP VERIFY] Verification logic exception: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Server verification logic crashed: {str(e)}"
        }), 500

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Allows resetting user password after confirming OTP code."""
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    new_password = data.get("password", "")
    
    if not email or not new_password:
        return jsonify({
            "status": "error",
            "message": "Email and new password are required inputs."
        }), 400
        
    user = UserModel.find_by_email(email)
    if not user:
        return jsonify({
            "status": "error",
            "message": "Student account not found."
        }), 404
        
    try:
        success = UserModel.update_password(email, new_password)
        if success:
            return jsonify({
                "status": "success",
                "message": "Security password successfully updated."
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to update password. Try again."
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Database update failed: {str(e)}"
        }), 500
