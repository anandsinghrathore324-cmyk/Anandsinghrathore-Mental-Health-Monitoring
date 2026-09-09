"""
prompt_builder.py  --  AIRA Contextual Prompt Assembly Module (Optimized)
=========================================================================
Pure utility module with NO Flask dependency.

Optimization goals (Phase 1):
    - Reduce prompt size by >=50% vs. the verbose version.
    - Compress assessment into a single natural-language sentence.
    - Limit history to last 2 conversation turns only.
    - Include at most 2 one-line recommendation hints.
    - Remove section headers that duplicate SYSTEM_PROMPT instructions.
    - Never expose raw numerical scores.

Prompt structure (compact):
    [SYSTEM_PROMPT]
    [Student name/context line — only if profile provided]
    [Wellbeing summary — one natural-language sentence]
    [Top 2 wellness hints — one bullet each]
    [Last 2 history turns — only if available]
    [Student message]
    AIRA:
"""

from __future__ import annotations
from chatbot.system_prompt import SYSTEM_PROMPT

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

    Example output:
        "The student is feeling Anxious with high stress, moderate anxiety,
        low depression, high burnout, and poor overall wellbeing (risk: Moderate)."
    """
    s  = _humanize_score(stress,     "stress")
    a  = _humanize_score(anxiety,    "anxiety")
    d  = _humanize_score(depression, "depression")
    b  = _humanize_score(burnout,    "burnout")
    w  = _humanize_score(wellness,   "wellness")

    return (
        f"The student is feeling {emotion} with {s} stress, {a} anxiety, "
        f"{d} depression, {b} burnout, and {w} overall wellbeing (risk: {risk_level})."
    )


def _format_recommendations(recommendations: list[dict]) -> str:
    """
    Return up to 2 one-line recommendation hints as compact bullets.
    No category headers. No long descriptions.
    """
    if not recommendations:
        return ""

    def _key(rec: dict) -> int:
        cat = rec.get("category", "")
        try:
            return _RECOMMENDATION_PRIORITY.index(cat)
        except ValueError:
            return len(_RECOMMENDATION_PRIORITY)

    sorted_recs = sorted(recommendations, key=_key)
    top = sorted_recs[:_MAX_RECOMMENDATIONS]

    lines = []
    for rec in top:
        title = rec.get("title", "").strip()
        if title:
            lines.append(f"• {title}")

    return "\n".join(lines) if lines else ""


def _format_history(history: list[dict] | None) -> str:
    """
    Render only the last 2 conversation turns as a compact dialogue.
    No section headers. No separator markers.
    """
    if not history:
        return ""

    recent = history[-_MAX_HISTORY_TURNS:]
    lines = []
    for item in recent:
        role    = item.get("role", "student").strip().lower()
        message = item.get("message", "").strip()
        if not message:
            continue
        speaker = "Student" if role == "student" else "AIRA"
        lines.append(f"{speaker}: {message}")

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

    Optimized for minimum token count while preserving full personalization,
    diagnostic context, wellness hints, and conversation continuity.

    Returns:
        A single string — the complete assembled prompt.
    """
    cleaned = user_message.strip() if user_message else "(No message provided)"

    # ── System prompt ────────────────────────────────────────────────────────
    parts: list[str] = [SYSTEM_PROMPT.strip()]

    # ── Student context line (if profile available) ───────────────────────────
    if student_profile:
        ctx_parts = []
        if student_profile.get("name"):
            ctx_parts.append(f"Name: {str(student_profile['name']).strip()}")
        if student_profile.get("age"):
            ctx_parts.append(f"Age: {str(student_profile['age']).strip()}")
        if student_profile.get("gender"):
            ctx_parts.append(f"Gender: {str(student_profile['gender']).strip()}")
        if ctx_parts:
            parts.append("Student: " + " | ".join(ctx_parts))

    # ── Wellbeing summary (compressed natural prose) ─────────────────────────
    parts.append(_build_wellbeing_summary(
        emotion, stress, anxiety, depression, burnout, wellness, risk_level
    ))

    # ── Top 2 wellness hints (one line each) ─────────────────────────────────
    hints = _format_recommendations(recommendations)
    if hints:
        parts.append("Wellness hints:\n" + hints)

    # ── Last 2 conversation turns ─────────────────────────────────────────────
    hist = _format_history(history)
    if hist:
        parts.append("Recent chat:\n" + hist)

    # ── Current message + trigger ─────────────────────────────────────────────
    parts.append(f"Student: {cleaned}")
    parts.append("AIRA:")

    return "\n\n".join(parts)
