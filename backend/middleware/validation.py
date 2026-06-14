from functools import wraps
from flask import request, jsonify

def validate_prediction_input(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json() or {}
        
        # Age validation
        age_raw = data.get("age")
        if age_raw is None:
            return jsonify({"status": "error", "message": "Age is required."}), 400
        try:
            age = int(age_raw)
            if age < 15 or age > 60:
                return jsonify({"status": "error", "message": "Age must be between 15 and 60."}), 400
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Age must be a valid integer."}), 400

        # Gender validation
        gender = data.get("gender")
        if gender is None:
            return jsonify({"status": "error", "message": "Gender is required."}), 400
        valid_genders = ["Male", "Female", "Other", "Prefer not to say"]
        if gender not in valid_genders:
            return jsonify({"status": "error", "message": f"Gender must be one of {valid_genders}."}), 400

        # Numeric bounds checking helper
        def check_bound(name, val, min_val, max_val, is_int=True):
            if val is None:
                return None, f"{name} is required."
            try:
                num_val = int(val) if is_int else float(val)
                if num_val < min_val or num_val > max_val:
                    return None, f"{name} must be between {min_val} and {max_val}."
                return num_val, None
            except (ValueError, TypeError):
                return None, f"{name} must be a valid number."

        # Academic Pressure
        acad, err = check_bound("Academic pressure", data.get("academic_pressure"), 1, 10, is_int=True)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Study Satisfaction
        satisfaction, err = check_bound("Study satisfaction", data.get("study_satisfaction"), 1, 10, is_int=True)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Dietary Habits
        diet = data.get("dietary_habits")
        if diet is None:
            return jsonify({"status": "error", "message": "Dietary habits is required."}), 400
        valid_diets = ["Healthy", "Moderate", "Unhealthy"]
        if diet not in valid_diets:
            return jsonify({"status": "error", "message": f"Dietary habits must be one of {valid_diets}."}), 400

        # Anxiety Level
        anx, err = check_bound("Anxiety level", data.get("anxiety_level"), 1, 10, is_int=True)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Stress Level
        str_lvl, err = check_bound("Stress level", data.get("stress_level"), 1, 10, is_int=True)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Financial Stress
        fin_stress, err = check_bound("Financial stress", data.get("financial_stress"), 1, 10, is_int=True)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Family History of Mental Illness
        fam_history = data.get("family_history")
        if fam_history is None:
            return jsonify({"status": "error", "message": "Family history of mental illness is required."}), 400
        valid_history = ["Yes", "No"]
        if fam_history not in valid_history:
            return jsonify({"status": "error", "message": f"Family history of mental illness must be one of {valid_history}."}), 400

        # Study Hours
        study, err = check_bound("Study hours", data.get("study_hours"), 0.0, 24.0, is_int=False)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Sleep Hours
        sleep, err = check_bound("Sleep hours", data.get("sleep_hours"), 0.0, 24.0, is_int=False)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Screen Time
        screen, err = check_bound("Screen time", data.get("screen_time"), 0.0, 24.0, is_int=False)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Work Hours
        work, err = check_bound("Work hours", data.get("work_hours"), 0.0, 24.0, is_int=False)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Implement soft warnings instead of hard rejections for combined hours
        from flask import g
        g.warnings = []
        if (sleep + study + work) > 24.0:
            g.warnings.append("Combined sleep, study, and work hours exceed 24 hours in a single day.")

        # Soft warnings for individual high values
        if sleep > 16.0:
            g.warnings.append("Sleep duration is unusually high (over 16 hours).")
        if study > 16.0:
            g.warnings.append("Study duration is unusually high (over 16 hours).")
        if work > 16.0:
            g.warnings.append("Work duration is unusually high (over 16 hours).")
        if screen > 18.0:
            g.warnings.append("Screen time is unusually high (over 18 hours).")

        # Text input validation checks (gibberish, text length, word bounds)
        diary_text = data.get("text", "").strip()
        if not diary_text:
            return jsonify({"status": "error", "message": "Journal text is required."}), 400

        words = [w for w in diary_text.split() if w]
        
        # Minimum 30 characters
        if len(diary_text) < 30:
            return jsonify({"status": "error", "message": "Journal text must be at least 30 characters."}), 400
            
        # Minimum 5 words
        if len(words) < 5:
            return jsonify({"status": "error", "message": "Journal text must contain at least 5 words."}), 400

        if len(diary_text) > 1000:
            return jsonify({"status": "error", "message": "Journal text must not exceed 1000 characters."}), 400

        # Reject only numbers
        import re
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

        from nlp.gibberish_detector import GibberishDetector
        if GibberishDetector.is_gibberish(diary_text):
            return jsonify({"status": "error", "message": "Please enter meaningful journal content."}), 400

        return f(*args, **kwargs)
    return decorated_function
