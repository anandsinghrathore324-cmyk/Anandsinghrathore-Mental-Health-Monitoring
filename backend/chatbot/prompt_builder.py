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

_COMPACT_SYSTEM = """You are AIRA, a warm, supportive, and intelligent AI Student Wellness Companion & Digital Bestie. Talk like an empathetic, encouraging student peer and mentor. Help with emotional wellness, stress, study habits, exam preparation, motivation, and everyday student life. Answer questions warmly, give practical tips when asked, celebrate positive moments, and never diagnose or prescribe. Keep responses natural, engaging, and supportive."""

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


def _format_recommendations(recommendations: list[dict | str] | None) -> str:
    """Return up to 2 one-line recommendation hints as compact bullets."""
    if not recommendations:
        return ""

    def _key(rec: dict | str) -> int:
        if isinstance(rec, str):
            return len(_RECOMMENDATION_PRIORITY)
        cat = rec.get("category", "")
        try:
            return _RECOMMENDATION_PRIORITY.index(cat)
        except ValueError:
            return len(_RECOMMENDATION_PRIORITY)

    top = sorted(recommendations, key=_key)[:_MAX_RECOMMENDATIONS]
    lines = []
    for r in top:
        if isinstance(r, str) and r.strip():
            lines.append(f"- {r.strip()}")
        elif isinstance(r, dict) and r.get("title"):
            lines.append(f"- {r['title'].strip()}")
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
    memories:               list[str] | None = None,
) -> str:
    """
    Assemble the final compact prompt for the Ollama LLM.

    Optimized for minimum token count while preserving personalization,
    diagnostic context, wellness hints, conversation continuity, and long-term memory.
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

    # Relevant Previous Context (memory injection)
    if memories:
        mem_lines = [f"* {m}" for m in memories[:5]]
        parts.append("Relevant Previous Context:\n" + "\n".join(mem_lines))

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
