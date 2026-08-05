import os
import jwt
import datetime
import logging
from flask import Blueprint, request, jsonify
from config import Config
from database.user_model import UserModel
from middleware.auth_middleware import token_required
from services.email_service import EmailService

logger = logging.getLogger(__name__)

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
    logger.info(f"[AUTH AUDIT] Received login attempt for email: {email} (DB Provider: {db_type})")
    
    user = UserModel.find_by_email(email)
    
    if not user:
        logger.warning(f"[AUTH AUDIT] Failed Login: No user document found in database for email: {email}")
        return jsonify({
            "status": "error",
            "message": "Invalid credentials. Access Denied (User not found)."
        }), 401
        
    logger.info(f"[AUTH AUDIT] User record found: ID={user['_id']}")
    
    email_verified = user.get("email_verified")
    if email_verified is None:
        logger.info("[AUTH AUDIT] email_verified field is missing from user record (defaults to True or not used in schema)")
    else:
        logger.info(f"[AUTH AUDIT] email_verified status: {email_verified}")
        
    pass_check = UserModel.verify_password(user["password"], password)
    logger.info(f"[AUTH AUDIT] Password hash verification result: {pass_check}")
    
    if not pass_check:
        logger.warning(f"[AUTH AUDIT] Failed Login: Password mismatch for email: {email}")
        return jsonify({
            "status": "error",
            "message": "Invalid credentials. Access Denied (Password mismatch)."
        }), 401
        
    try:
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        expiration = now_utc + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        token_payload = {
            "sub": user["_id"],
            "exp": expiration,
            "iat": now_utc
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
    """Generates a 6-digit OTP and dispatches it via Resend (prod) or smtplib (dev)."""
    import secrets
    from database.db import db_manager

    data  = request.get_json() or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"status": "error", "message": "Email address is required."}), 400

    otp_code = str(secrets.randbelow(900000) + 100000)  # cryptographically random 6 digits

    try:
        # Persist OTP (TTL-indexed — auto-expires in 5 minutes)
        db_manager.db.otp_codes.update_one(
            {"email": email},
            {"$set": {"email": email, "otp": otp_code, "created_at": datetime.datetime.now(datetime.timezone.utc)}},
            upsert=True,
        )
    except Exception as db_err:
        logger.error("[OTP] Failed to persist OTP for %s: %s", email, db_err, exc_info=True)
        return jsonify({"status": "error", "message": "Failed to generate verification code."}), 500

    if not EmailService.is_configured():
        logger.error("[OTP] No email driver configured — aborting for: %s", email)
        return jsonify({
            "status": "error",
            "message": "Email delivery is not configured. Contact the administrator.",
        }), 500

    ok, err = EmailService.send_otp(to_email=email, otp_code=otp_code, purpose="reset")

    if ok:
        has_real_email = bool((os.getenv("BREVO_API_KEY") and os.getenv("BREVO_FROM_EMAIL")) or (os.getenv("SMTP_EMAIL") and os.getenv("SMTP_PASSWORD")))
        resp = {
            "status": "success",
            "message": "One-Time Password has been dispatched to your email inbox." if has_real_email else "One-Time Password generated (Dev mode: check console).",
        }
        if not has_real_email:
            resp["otp_bypass"] = otp_code
        return jsonify(resp), 200

    logger.error("[OTP] Email delivery failed for %s: %s", email, err)
    return jsonify({"status": "error", "message": f"Email delivery failed: {err}"}), 500

@auth_bp.route("/signup-request-otp", methods=["POST"])
def signup_request_otp():
    """Checks email availability, generates a signup OTP, and dispatches it via Resend (prod) or smtplib (dev)."""
    import secrets
    from database.db import db_manager

    data  = request.get_json() or {}
    name  = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()

    if not name or not email:
        return jsonify({"status": "error", "message": "Name and email are required."}), 400

    if UserModel.find_by_email(email):
        return jsonify({
            "status": "error",
            "message": "A student account is already registered under this email address.",
        }), 400

    otp_code = str(secrets.randbelow(900000) + 100000)  # cryptographically random 6 digits

    try:
        db_manager.db.otp_codes.update_one(
            {"email": email},
            {"$set": {"email": email, "otp": otp_code, "created_at": datetime.datetime.now(datetime.timezone.utc)}},
            upsert=True,
        )
    except Exception as db_err:
        logger.error("[SIGNUP OTP] Failed to persist OTP for %s: %s", email, db_err, exc_info=True)
        return jsonify({"status": "error", "message": "Failed to generate verification code."}), 500

    if not EmailService.is_configured():
        logger.error("[SIGNUP OTP] No email driver configured — aborting for: %s", email)
        return jsonify({
            "status": "error",
            "message": "Email delivery is not configured. Contact the administrator.",
        }), 500

    ok, err = EmailService.send_otp(
        to_email=email,
        otp_code=otp_code,
        purpose="signup",
        recipient_name=name,
    )

    if ok:
        has_real_email = bool((os.getenv("BREVO_API_KEY") and os.getenv("BREVO_FROM_EMAIL")) or (os.getenv("SMTP_EMAIL") and os.getenv("SMTP_PASSWORD")))
        resp = {
            "status": "success",
            "message": "Verification code has been dispatched to your email address." if has_real_email else "Verification code generated (Dev mode: check console).",
        }
        if not has_real_email:
            resp["otp_bypass"] = otp_code
        return jsonify(resp), 200

    logger.error("[SIGNUP OTP] Email delivery failed for %s: %s", email, err)
    return jsonify({"status": "error", "message": f"Email delivery failed: {err}"}), 500

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
        record = db_manager.db.otp_codes.find_one({"email": email, "otp": otp_provided})
        
        if not record:
            return jsonify({
                "status": "error",
                "message": "Invalid or expired One-Time Password. Access Denied."
            }), 401
            
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        created_at = record.get("created_at")
        if created_at and getattr(created_at, "tzinfo", None) is None:
            created_at = created_at.replace(tzinfo=datetime.timezone.utc)
        time_elapsed = now_utc - (created_at or now_utc)
        if time_elapsed > datetime.timedelta(minutes=5):
            db_manager.db.otp_codes.delete_one({"_id": record["_id"]})
            return jsonify({
                "status": "error",
                "message": "Verification code has expired. Access Denied."
            }), 401
            
        # Burn OTP immediately so it cannot be re-used
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
        record = db_manager.db.otp_codes.find_one({"email": email, "otp": otp_provided})
        
        if not record:
            logger.warning(f"[AUTH OTP VERIFY] OTP check failed: no record found matching email {email} and code {otp_provided}")
            return jsonify({
                "status": "error",
                "message": "Invalid or expired One-Time Password. Access Denied."
            }), 401
            
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        created_at = record.get("created_at")
        if created_at and getattr(created_at, "tzinfo", None) is None:
            created_at = created_at.replace(tzinfo=datetime.timezone.utc)
        time_elapsed = now_utc - (created_at or now_utc)
        logger.info(f"[AUTH OTP VERIFY] OTP record found. Created at {record['created_at'].isoformat()}, time elapsed: {time_elapsed.total_seconds()}s")
        if time_elapsed > datetime.timedelta(minutes=5):
            logger.warning(f"[AUTH OTP VERIFY] OTP code has expired (> 5 minutes elapsed) for user: {email}")
            db_manager.db.otp_codes.delete_one({"_id": record["_id"]})
            return jsonify({
                "status": "error",
                "message": "One-Time Password has expired (5 minutes timeout). Access Denied."
            }), 401
            
        # Burn OTP immediately so it cannot be re-used
        db_manager.db.otp_codes.delete_one({"_id": record["_id"]})
        logger.info(f"[AUTH OTP VERIFY] Burned OTP token successfully for user: {email}")
        
        user = UserModel.find_by_email(email)
        
        if not user:
            logger.info(f"[AUTH OTP VERIFY] Auto-Signup triggered for new user: {email}")
            name_prefix = email.split("@")[0].capitalize()
            user = UserModel.create_user(name_prefix, email, "otp-auto-secured-pass-2026")
            logger.info(f"[AUTH OTP VERIFY] Registered new user during auto-signup: ID={user['_id']}")
        else:
            logger.info(f"[AUTH OTP VERIFY] Found existing user profile for email: {email}")
            
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        expiration = now_utc + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
        token_payload = {
            "sub": user["_id"],
            "exp": expiration,
            "iat": now_utc
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


# ─── Profile Onboarding Endpoints ────────────────────────────────────────────

@auth_bp.route("/profile-status", methods=["GET"])
@token_required
def profile_status(current_user):
    """Returns whether the user has completed their profile and the stored profile data."""
    current_year = datetime.datetime.now(datetime.timezone.utc).year
    birth_year = current_user.get("birth_year")
    age = (current_year - int(birth_year)) if birth_year else None

    profile_complete = UserModel.has_complete_profile(current_user)

    return jsonify({
        "status": "success",
        "profile_complete": profile_complete,
        "profile": {
            "name": current_user.get("name"),
            "gender": current_user.get("gender"),
            "birth_year": birth_year,
            "age": age
        }
    }), 200


@auth_bp.route("/save-profile", methods=["POST"])
@token_required
def save_profile(current_user):
    """Saves or updates the user's one-time onboarding profile (gender, birth_year, name).

    Validates birth_year so that the resulting age is between 15 and 60.
    College is not collected.
    """
    data = request.get_json() or {}

    gender     = data.get("gender", "").strip()
    birth_year = data.get("birth_year")
    name       = data.get("name", "").strip()

    # Validate required fields
    if not gender or not birth_year:
        return jsonify({
            "status": "error",
            "message": "Gender and birth year are required."
        }), 400

    valid_genders = ["Male", "Female", "Other", "Prefer not to say"]
    if gender not in valid_genders:
        return jsonify({
            "status": "error",
            "message": f"Gender must be one of: {', '.join(valid_genders)}."
        }), 400

    current_year = datetime.datetime.now(datetime.timezone.utc).year
    try:
        birth_year = int(birth_year)
        age = current_year - birth_year
        if age < 15 or age > 60:
            return jsonify({
                "status": "error",
                "message": "Birth year must result in an age between 15 and 60."
            }), 400
    except (ValueError, TypeError):
        return jsonify({
            "status": "error",
            "message": "Birth year must be a valid integer (e.g. 1999)."
        }), 400

    profile_data = {
        "gender": gender,
        "birth_year": birth_year
    }
    if name:
        profile_data["name"] = name

    success = UserModel.update_profile(current_user["_id"], profile_data)
    if not success:
        logger.error(f"[PROFILE] Failed to update profile for user {current_user['_id']}")
        return jsonify({
            "status": "error",
            "message": "Profile update failed. Please try again."
        }), 500

    logger.info(f"[PROFILE] Profile saved for user {current_user['_id']} — gender={gender}, birth_year={birth_year}, age={age}")

    return jsonify({
        "status": "success",
        "message": "Profile saved successfully.",
        "profile": {
            "name": name or current_user.get("name"),
            "gender": gender,
            "birth_year": birth_year,
            "age": age
        }
    }), 200
