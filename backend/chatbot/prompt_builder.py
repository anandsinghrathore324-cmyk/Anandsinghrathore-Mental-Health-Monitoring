"""
prompt_builder.py  --  AIRA Contextual Prompt Assembly Module (Optimized v2)
============================================================================
Pure utility module with NO Flask dependency.

Phase 1 Optimization:
    - Uses a compact inline system header instead of the verbose SYSTEM_PROMPT.
    - Compresses assessment into a single natural-language sentence.
    - Limits history to last 2 conversation turns (4 items).
    - Includes at most 2 one-line recommendation hints.
    - Removes all verbose section headers and repeated instructions.
    - Achieves >=50% total prompt size reduction.
    - Never exposes raw numerical scores.

Prompt structure:
    [Compact system header]
    [Student context line - only if profile provided]
    [Wellbeing summary - one natural-language sentence]
    [Top 2 wellness hints - one bullet each]
    [Last 2 history turns - only if available]
    [Student message]
    AIRA:
"""

from __future__ import annotations

# Compact system header -- covers all essential SYSTEM_PROMPT instructions
# in ~30% of the character count. Used instead of the full SYSTEM_PROMPT
# to reduce token overhead while preserving behavioral fidelity.
_COMPACT_SYSTEM = """You are AIRA, an AI Student Wellness Assistant. Support students on mental health, stress, anxiety, depression, burnout, sleep, study habits, and wellbeing only. Decline unrelated topics politely. Never diagnose or prescribe. Be warm, empathetic, concise (150-250 words), and end responses with an open supportive question."""

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MAX_HISTORY_TURNS: int = 4   # 2 full turns = 4 items (student + aira x2)
_MAX_RECOMMENDATIONS: int = 2

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

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _humanize_score(score: int, label: str) -> str:
    """Convert a 0-100 numeric score to a human-readable category label."""
    score = max(0, min(100, int(score)))
    if label.lower() == "wellness":
        if score <= 20: return "critical"
        if score <= 40: return "poor"
        if score <= 60: return "fair"
        if score <= 79: return "good"
        return "excellent"
    else:
        if score <= 20: return "very low"
        if score <= 40: return "low"
        if score <= 60: return "moderate"
        if score <= 79: return "high"
        return "very high"


def _build_wellbeing_summary(
    emotion: str,
    stress: int,
    anxiety: int,
    depression: int,
    burnout: int,
    wellness: int,
    risk_level: str,
) -> str:
    """
    Compress all diagnostic scores into one natural-language sentence.

    Example:
        "Student is feeling Anxious; high stress, moderate anxiety,
        low depression, high burnout, poor wellbeing (risk: Moderate)."
    """
    s = _humanize_score(stress,     "stress")
    a = _humanize_score(anxiety,    "anxiety")
    d = _humanize_score(depression, "depression")
    b = _humanize_score(burnout,    "burnout")
    w = _humanize_score(wellness,   "wellness")
    return (
        f"Student: feeling {emotion}; {s} stress, {a} anxiety, "
        f"{d} depression, {b} burnout, {w} wellbeing (risk: {risk_level})."
    )


def _format_recommendations(recommendations: list[dict]) -> str:
    """Return up to 2 one-line recommendation hints as compact bullets."""
    if not recommendations:
        return ""

    def _key(rec: dict) -> int:
        cat = rec.get("category", "")
        try:
            return _RECOMMENDATION_PRIORITY.index(cat)
        except ValueError:
            return len(_RECOMMENDATION_PRIORITY)

    top = sorted(recommendations, key=_key)[:_MAX_RECOMMENDATIONS]
    lines = [f"- {r['title'].strip()}" for r in top if r.get("title")]
    return "\n".join(lines) if lines else ""


def _format_history(history: list[dict] | None) -> str:
    """Render only the last 2 conversation turns as compact inline dialogue."""
    if not history:
        return ""
    lines = []
    for item in history[-_MAX_HISTORY_TURNS:]:
        role    = item.get("role", "student").lower()
        message = item.get("message", "").strip()
        if message:
            lines.append(f"{'S' if role == 'student' else 'A'}: {message}")
    return "\n".join(lines) if lines else ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_prompt(
    user_message:           str,
    emotion:                str,
    stress:                 int,
    anxiety:                int,
    depression:             int,
    burnout:                int,
    wellness:               int,
    risk_level:             str,
    prediction_reliability: str,
    recommendations:        list[dict],
    history:                list[dict] | None = None,
    student_profile:        dict | None = None,
) -> str:
    """
    Assemble the final compact prompt for the Ollama LLM.

    Optimized for minimum token count while preserving personalization,
    diagnostic context, wellness hints, and conversation continuity.

    Args:
        user_message:           Raw student input.
        emotion:                Detected dominant emotion string.
        stress:                 Stress score 0-100.
        anxiety:                Anxiety score 0-100.
        depression:             Depression score 0-100.
        burnout:                Burnout score 0-100.
        wellness:               Wellness score 0-100 (inverted scale).
        risk_level:             Risk classification string.
        prediction_reliability: Model confidence label (unused in prompt,
                                retained for API compatibility).
        recommendations:        List of recommendation dicts.
        history:                Optional previous chat turns (oldest-first).
        student_profile:        Optional dict with name/age/gender keys.

    Returns:
        A single string ready to pass to ollama_client.generate_response().
    """
    cleaned = user_message.strip() if user_message else "(No message provided)"

    parts: list[str] = [_COMPACT_SYSTEM.strip()]

    # Student profile (one compact line)
    if student_profile:
        ctx = []
        if student_profile.get("name"):   ctx.append(student_profile["name"].strip())
        if student_profile.get("age"):    ctx.append(f"age {str(student_profile['age']).strip()}")
        if student_profile.get("gender"): ctx.append(student_profile["gender"].strip())
        if ctx:
            parts.append("Student profile: " + ", ".join(ctx))

    # Wellbeing summary (one sentence)
    parts.append(_build_wellbeing_summary(
        emotion, stress, anxiety, depression, burnout, wellness, risk_level
    ))

    # Top 2 wellness hints (one line each)
    hints = _format_recommendations(recommendations)
    if hints:
        parts.append("Hints:\n" + hints)

    # Last 2 conversation turns (compact S:/A: format)
    hist = _format_history(history)
    if hist:
        parts.append("History:\n" + hist)

    # Current message + trigger
    parts.append(f"Student: {cleaned}")
    parts.append("AIRA:")

    return "\n\n".join(parts)
