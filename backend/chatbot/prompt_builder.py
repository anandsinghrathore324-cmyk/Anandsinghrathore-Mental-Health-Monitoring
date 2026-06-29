"""
prompt_builder.py  —  AIRA Contextual Prompt Assembly Module
=============================================================
Pure utility module with NO Flask dependency.

Responsibility:
    Receive the student's raw message, diagnostic assessment metrics,
    conversation history, and optional profile data, then assemble
    one final, richly-contextual prompt string ready to be sent
    directly to the Ollama LLM.
"""

from __future__ import annotations

from chatbot.system_prompt import SYSTEM_PROMPT

# Constants
_MAX_HISTORY_ITEMS: int = 10
_MAX_RECOMMENDATIONS: int = 3

_RECOMMENDATION_PRIORITY: list[str] = [
    "Risk-based",
    "Sleep Improvement",
    "Breathing & Mindfulness",
    "Study Management",
    "Financial Support",
    "Academic Counseling",
    "Digital Wellness",
    "Social Connection",
    "Stress Relief",
    "Healthy Lifestyle",
    "General Wellness",
]


def _humanize_score(score: int, label: str) -> str:
    """
    Convert a 0-100 numeric assessment score into a human-readable category.

    Wellness uses an inverted scale (higher score = better state), so it
    maps to a distinct set of descriptors. All other metrics (stress,
    anxiety, depression, burnout) use the standard ascending scale.

    Args:
        score:  Integer in the range 0–100.
        label:  The metric name in lowercase (e.g. "stress", "wellness").

    Returns:
        A plain-language category string.
    """
    score = max(0, min(100, int(score)))

    if label.lower() == "wellness":
        if score <= 20:
            return "Critical"
        elif score <= 40:
            return "Poor"
        elif score <= 60:
            return "Fair"
        elif score <= 79:
            return "Good"
        else:
            return "Excellent"
    else:
        if score <= 20:
            return "Very Low"
        elif score <= 40:
            return "Low"
        elif score <= 60:
            return "Moderate"
        elif score <= 79:
            return "High"
        else:
            return "Very High"


def _format_recommendations(recommendations: list[dict]) -> str:
    """
    Select the top N most relevant recommendations and format them as
    bullet points.

    Selection is driven by _RECOMMENDATION_PRIORITY.

    Args:
        recommendations: List of recommendation dicts.

    Returns:
        A formatted string block, or empty string if no valid recommendations.
    """
    if not recommendations:
        return ""

    def _priority_key(rec: dict) -> int:
        cat = rec.get("category", "")
        try:
            return _RECOMMENDATION_PRIORITY.index(cat)
        except ValueError:
            return len(_RECOMMENDATION_PRIORITY)

    sorted_recs = sorted(recommendations, key=_priority_key)
    top_recs = sorted_recs[:_MAX_RECOMMENDATIONS]

    lines: list[str] = []
    for rec in top_recs:
        title = rec.get("title", "").strip()
        description = rec.get("description", "").strip()
        if title:
            lines.append(f"• {title}: {description}")

    if not lines:
        return ""

    return "=== WELLNESS INSIGHTS AVAILABLE ===\n" + "\n".join(lines)


def _format_history(history: list[dict] | None) -> str:
    """
    Render the last N conversation turns into a dialogue block.

    Expected format of history items:
        {"role": "student" | "aira", "message": str}

    Args:
        history: List of turn dicts, or None.

    Returns:
        A formatted dialogue block string, or an empty string if history is empty.
    """
    if not history:
        return ""

    recent = history[-_MAX_HISTORY_ITEMS:]

    lines: list[str] = ["=== RECENT CONVERSATION HISTORY ==="]
    for item in recent:
        role = item.get("role", "student").strip().lower()
        message = item.get("message", "").strip()
        if not message:
            continue
        speaker = "Student" if role == "student" else "AIRA"
        lines.append(f"[{speaker}] {message}")
    lines.append("===")

    if len(lines) <= 2:
        return ""

    return "\n".join(lines)


def build_prompt(
    user_message: str,
    emotion: str,
    stress: int,
    anxiety: int,
    depression: int,
    burnout: int,
    wellness: int,
    risk_level: str,
    prediction_reliability: str,
    recommendations: list[dict],
    history: list[dict] | None = None,
    student_profile: dict | None = None,
) -> str:
    """
    Assemble the final prompt string to send to the Ollama LLM.

    All numeric scores are humanized before injection. Raw numbers
    never appear in the returned string.

    Args:
        user_message:           The raw text typed by the student.
        emotion:                Detected dominant emotion.
        stress:                 Stress score 0-100.
        anxiety:                Anxiety score 0-100.
        depression:             Depression score 0-100.
        burnout:                Burnout score 0-100.
        wellness:               Wellness score 0-100.
        risk_level:             Risk classification string.
        prediction_reliability: Model confidence label.
        recommendations:        List of recommendation dicts.
        history:                Optional list of previous chat turns.
        student_profile:        Optional dict with profile fields (e.g. name, age, gender).

    Returns:
        A single string ready to pass directly to the LLM client.
    """
    cleaned_message = user_message.strip() if user_message else ""
    if not cleaned_message:
        cleaned_message = "(No message provided)"

    stress_label = _humanize_score(stress, "stress")
    anxiety_label = _humanize_score(anxiety, "anxiety")
    depression_label = _humanize_score(depression, "depression")
    burnout_label = _humanize_score(burnout, "burnout")
    wellness_label = _humanize_score(wellness, "wellness")

    # A. SYSTEM PROMPT
    block_system = SYSTEM_PROMPT.strip()

    # B. STUDENT PROFILE (optional)
    block_profile = ""
    if student_profile:
        profile_lines: list[str] = ["=== STUDENT PROFILE ==="]
        if student_profile.get("name"):
            profile_lines.append(f"Name   : {str(student_profile['name']).strip()}")
        if student_profile.get("age"):
            profile_lines.append(f"Age    : {str(student_profile['age']).strip()}")
        if student_profile.get("gender"):
            profile_lines.append(f"Gender : {str(student_profile['gender']).strip()}")
        if len(profile_lines) > 1:
            block_profile = "\n".join(profile_lines)

    # C. STUDENT DIAGNOSTIC CONTEXT
    block_context = "\n".join([
        "=== STUDENT DIAGNOSTIC CONTEXT ===",
        f"Detected Emotion    : {emotion}",
        f"Stress Level        : {stress_label}",
        f"Anxiety Level       : {anxiety_label}",
        f"Depression Level    : {depression_label}",
        f"Burnout Level       : {burnout_label}",
        f"Overall Wellness    : {wellness_label}",
        f"Risk Level          : {risk_level}",
        f"Prediction Quality  : {prediction_reliability}",
    ])

    # D. WELLNESS INSIGHTS
    block_insights = _format_recommendations(recommendations)

    # E. RECENT CONVERSATION HISTORY (omitted if empty)
    block_history = _format_history(history)

    # F. RESPONSE INSTRUCTIONS
    block_instructions = "\n".join([
        "=== RESPONSE INSTRUCTIONS ===",
        "- Do NOT mention any numerical scores or percentages in your response.",
        "- Describe the student's emotional and mental state using natural,",
        "  empathetic language only — never clinical jargon.",
        "- Reference at most 1 or 2 wellness insights if they are genuinely",
        "  relevant. Do not list all of them or recite them mechanically.",
        "- Acknowledge and validate the student's current emotional state first,",
        "  before offering any suggestions.",
        "- Keep your response between 150 and 250 words unless the student",
        "  explicitly requests more detail.",
        "- End with an open, supportive question to invite further conversation.",
    ])

    # G. CURRENT STUDENT MESSAGE
    block_message = f"Current Student Message: {cleaned_message}"

    # H. AIRA:
    block_trigger = "AIRA:"

    # Assemble sections
    all_blocks: list[str] = [block_system]

    if block_profile:
        all_blocks.append(block_profile)

    all_blocks.append(block_context)

    if block_insights:
        all_blocks.append(block_insights)

    if block_history:
        all_blocks.append(block_history)

    all_blocks.append(block_instructions)
    all_blocks.append(block_message)
    all_blocks.append(block_trigger)

    return "\n\n".join(all_blocks)
