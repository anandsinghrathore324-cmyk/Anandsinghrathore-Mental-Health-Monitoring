from functools import wraps
from flask import request, jsonify, g
import re
import datetime as _dt
from nlp.gibberish_detector import GibberishDetector

def validate_prediction_input(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json() or {}

        # Resolve current_user from args[0] (injected by @token_required which runs first)
        current_user = args[0] if args else None

        # ── 1. Text input validation (Primary ML/DL Feature) ────────────────────
        diary_text = data.get("text", "").strip()
        if not diary_text:
            return jsonify({"status": "error", "message": "Journal text is required."}), 400

        words = [w for w in diary_text.split() if w]
        
        # Minimum 20 characters & 5 words
        if len(diary_text) < 20:
            return jsonify({"status": "error", "message": "Journal text must be at least 20 characters."}), 400
            
        if len(words) < 5:
            return jsonify({"status": "error", "message": "Journal text must contain at least 5 words."}), 400

        if len(diary_text) > 1000:
            return jsonify({"status": "error", "message": "Journal text must not exceed 1000 characters."}), 400

        # Reject only numbers
        letters_only = re.sub(r'[^a-zA-Z]', '', diary_text)
        digits_only = re.sub(r'[^0-9]', '', diary_text)
        if len(digits_only) > 0 and len(letters_only) == 0:
            return jsonify({"status": "error", "message": "Journal text cannot consist of only numbers."}), 400

        # Reject only symbols
        alphanumeric_only = re.sub(r'[^a-zA-Z0-9]', '', diary_text)
        if len(alphanumeric_only) == 0:
            return jsonify({"status": "error", "message": "Journal text cannot consist of only symbols."}), 400

        # Reject keyboard spam (character repetition of 4+ same characters consecutively)
        if re.search(r'(.)\1{3,}', diary_text):
            return jsonify({"status": "error", "message": "Please enter meaningful journal content (keyboard spam detected)."}), 400

        # Reject repeated nonsense tokens (consecutive identical words repeated 3+ times)
        if re.search(r'\b(\w+)\b\s+\1\s+\1', diary_text, re.IGNORECASE):
            return jsonify({"status": "error", "message": "Please enter meaningful journal content (repeated nonsense tokens detected)."}), 400

        # Reject repeated nonsense tokens (low unique word ratio < 0.35)
        if len(words) >= 5:
            unique_words = set(w.lower() for w in words)
            if (len(unique_words) / len(words)) < 0.35:
                return jsonify({"status": "error", "message": "Please enter meaningful journal content (low unique word ratio)."}), 400

        if GibberishDetector.is_gibberish(diary_text):
            return jsonify({"status": "error", "message": "Please enter meaningful journal content."}), 400

        # ── 2. Demographic resolution (Optional / Profile fallback) ─────────────
        age_raw = data.get("age")
        if age_raw is None and current_user and current_user.get("birth_year"):
            age_raw = _dt.datetime.now(_dt.timezone.utc).year - int(current_user["birth_year"])
        
        if age_raw is not None:
            try:
                age = int(age_raw)
                data["age"] = max(15, min(60, age))
            except (ValueError, TypeError):
                data["age"] = 21
        else:
            data["age"] = 21  # Youth default

        gender = data.get("gender")
        if not gender and current_user and current_user.get("gender"):
            gender = current_user["gender"]
        valid_genders = ["Male", "Female", "Other", "Prefer not to say"]
        if gender not in valid_genders:
            gender = "Prefer not to say"
        data["gender"] = gender

        # ── 3. Optional contextual parameters (clean sanitization) ──────────────
        g.warnings = []
        
        # Optional sleep
        if "sleep_hours" in data:
            try:
                data["sleep_hours"] = float(data["sleep_hours"])
            except (ValueError, TypeError):
                data["sleep_hours"] = 7.0
        else:
            data["sleep_hours"] = 7.0

        return f(*args, **kwargs)
    return decorated_function

