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
            if age < 13 or age > 100:
                return jsonify({"status": "error", "message": "Age must be between 13 and 100."}), 400
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
        study, err = check_bound("Study hours", data.get("study_hours"), 0.0, 16.0, is_int=False)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Sleep Hours
        sleep, err = check_bound("Sleep hours", data.get("sleep_hours"), 0.0, 14.0, is_int=False)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Screen Time
        screen, err = check_bound("Screen time", data.get("screen_time"), 0.0, 16.0, is_int=False)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Work Hours
        work, err = check_bound("Work hours", data.get("work_hours"), 0.0, 16.0, is_int=False)
        if err:
            return jsonify({"status": "error", "message": err}), 400

        # Combined workload limit
        if (study + sleep + screen + work) > 24.0:
            return jsonify({
                "status": "error",
                "message": "Combined study hours, sleep hours, screen time, and work hours cannot exceed 24 hours."
            }), 400

        # Text input validation checks (gibberish, text length, word bounds)
        diary_text = data.get("text", "").strip()
        if not diary_text:
            return jsonify({"status": "error", "message": "Journal text is required."}), 400

        words = [w for w in diary_text.split() if w]
        if len(diary_text) < 20 or len(words) < 5:
            return jsonify({"status": "error", "message": "Journal text must be at least 20 characters and contain at least 5 words."}), 400

        if len(diary_text) > 1000:
            return jsonify({"status": "error", "message": "Journal text must not exceed 1000 characters."}), 400

        from nlp.gibberish_detector import GibberishDetector
        if GibberishDetector.is_gibberish(diary_text):
            return jsonify({"status": "error", "message": "Please enter meaningful journal content."}), 400

        return f(*args, **kwargs)
    return decorated_function
