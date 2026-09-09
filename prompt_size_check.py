"""
Prompt Size Reduction Verification
Measures old vs new prompt length for 10 test conversations.
"""
import sys
import glob
import os

# Resolve backend path dynamically
matches = glob.glob(os.path.expanduser(r"~\OneDrive\Desktop\Social*\backend"))
if not matches:
    raise RuntimeError("Cannot locate backend directory.")
sys.path.insert(0, matches[0])

# Force UTF-8
sys.stdout.reconfigure(encoding="utf-8")

from chatbot.system_prompt import SYSTEM_PROMPT
from chatbot.prompt_builder import build_prompt, _build_wellbeing_summary, _format_recommendations, _format_history

# ---------------------------------------------------------------------------
# Simulate old prompt builder output for size comparison
# ---------------------------------------------------------------------------
def build_old_prompt(user_message, emotion, stress, anxiety, depression,
                     burnout, wellness, risk_level, prediction_reliability,
                     recommendations, history=None, student_profile=None):
    """Reconstructed old prompt for size comparison only."""

    def humanize(score, label):
        score = max(0, min(100, int(score)))
        if label == "wellness":
            if score <= 20: return "Critical"
            if score <= 40: return "Poor"
            if score <= 60: return "Fair"
            if score <= 79: return "Good"
            return "Excellent"
        else:
            if score <= 20: return "Very Low"
            if score <= 40: return "Low"
            if score <= 60: return "Moderate"
            if score <= 79: return "High"
            return "Very High"

    cleaned = user_message.strip() or "(No message provided)"
    sl = humanize(stress, "stress")
    al = humanize(anxiety, "anxiety")
    dl = humanize(depression, "depression")
    bl = humanize(burnout, "burnout")
    wl = humanize(wellness, "wellness")

    blocks = [SYSTEM_PROMPT.strip()]

    if student_profile:
        pl = ["=== STUDENT PROFILE ==="]
        if student_profile.get("name"):  pl.append(f"Name   : {student_profile['name']}")
        if student_profile.get("age"):   pl.append(f"Age    : {student_profile['age']}")
        if student_profile.get("gender"):pl.append(f"Gender : {student_profile['gender']}")
        if len(pl) > 1: blocks.append("\n".join(pl))

    blocks.append("\n".join([
        "=== STUDENT DIAGNOSTIC CONTEXT ===",
        f"Detected Emotion    : {emotion}",
        f"Stress Level        : {sl}",
        f"Anxiety Level       : {al}",
        f"Depression Level    : {dl}",
        f"Burnout Level       : {bl}",
        f"Overall Wellness    : {wl}",
        f"Risk Level          : {risk_level}",
        f"Prediction Quality  : {prediction_reliability}",
    ]))

    # Old recommendations (top 3 with full descriptions)
    if recommendations:
        rlines = ["=== WELLNESS INSIGHTS AVAILABLE ==="]
        for rec in recommendations[:3]:
            t = rec.get("title","").strip()
            d = rec.get("description","").strip()
            if t: rlines.append(f"* {t}: {d}")
        blocks.append("\n".join(rlines))

    # Old history (last 10 items)
    if history:
        hlines = ["=== RECENT CONVERSATION HISTORY ==="]
        for item in history[-10:]:
            role = item.get("role","student").lower()
            msg  = item.get("message","").strip()
            if msg:
                hlines.append(f"[{'Student' if role=='student' else 'AIRA'}] {msg}")
        hlines.append("===")
        if len(hlines) > 2: blocks.append("\n".join(hlines))

    blocks.append("\n".join([
        "=== RESPONSE INSTRUCTIONS ===",
        "- Do NOT mention any numerical scores or percentages in your response.",
        "- Describe the student's emotional and mental state using natural,",
        "  empathetic language only - never clinical jargon.",
        "- Reference at most 1 or 2 wellness insights if they are genuinely",
        "  relevant. Do not list all of them or recite them mechanically.",
        "- Acknowledge and validate the student's current emotional state first,",
        "  before offering any suggestions.",
        "- Keep your response between 150 and 250 words unless the student",
        "  explicitly requests more detail.",
        "- End with an open, supportive question to invite further conversation.",
    ]))

    blocks.append(f"Current Student Message: {cleaned}")
    blocks.append("AIRA:")
    return "\n\n".join(blocks)

# ---------------------------------------------------------------------------
# Test cases (representative real messages)
# ---------------------------------------------------------------------------
SAMPLE_PROFILE = {"name": "Anand", "age": "21", "gender": "Male"}
SAMPLE_SCORES  = dict(emotion="Anxious", stress=72, anxiety=65, depression=48,
                      burnout=61, wellness=38, risk_level="Moderate",
                      prediction_reliability="High")
SAMPLE_RECOMMENDATIONS = [
    {"title": "Proactive Stress Management", "description": "Setting boundaries and dedicated self-care time may significantly reduce current strain.", "category": "Stress Relief"},
    {"title": "Sleep Hygiene", "description": "Consistent, quality rest could improve both focus and emotional resilience.", "category": "Sleep Improvement"},
    {"title": "Mindfulness & Breathing", "description": "Guided breathing exercises are available on the platform and take only a few minutes.", "category": "Breathing & Mindfulness"},
]
SAMPLE_HISTORY = [
    {"role": "student", "message": "I've been struggling to focus on anything lately."},
    {"role": "aira",    "message": "That sounds really exhausting. When did this start?"},
    {"role": "student", "message": "About two weeks ago, right when exam season began."},
    {"role": "aira",    "message": "Exam pressure can really pile up. What subjects are weighing on you most?"},
]

TEST_MESSAGES = [
    "I feel really overwhelmed with my assignments.",
    "I can't sleep properly and it's affecting my studies.",
    "I'm stressed because of exams.",
    "How can I manage my time better?",
    "I feel like nobody understands me.",
    "I'm having trouble concentrating.",
    "I feel burnt out from all the pressure.",
    "My anxiety is getting worse every day.",
    "I don't have enough energy to do anything.",
    "I feel disconnected from everything around me.",
]

print("=" * 65)
print("  PROMPT SIZE REDUCTION VERIFICATION — Phase 1")
print("=" * 65)

old_sizes = []
new_sizes = []

for i, msg in enumerate(TEST_MESSAGES, 1):
    old_p = build_old_prompt(
        user_message=msg,
        history=SAMPLE_HISTORY,
        student_profile=SAMPLE_PROFILE,
        recommendations=SAMPLE_RECOMMENDATIONS,
        **SAMPLE_SCORES
    )
    new_p = build_prompt(
        user_message=msg,
        history=SAMPLE_HISTORY,
        student_profile=SAMPLE_PROFILE,
        recommendations=SAMPLE_RECOMMENDATIONS,
        **SAMPLE_SCORES
    )

    old_len = len(old_p)
    new_len = len(new_p)
    reduction = round((1 - new_len / old_len) * 100, 1)

    old_sizes.append(old_len)
    new_sizes.append(new_len)

    print(f"\nTest #{i}: \"{msg[:45]}{'...' if len(msg)>45 else ''}\"")
    print(f"  Old prompt length : {old_len:,} chars")
    print(f"  New prompt length : {new_len:,} chars")
    print(f"  Reduction         : {reduction}%")

avg_old = round(sum(old_sizes) / len(old_sizes))
avg_new = round(sum(new_sizes) / len(new_sizes))
avg_red = round((1 - avg_new / avg_old) * 100, 1)
min_new = min(new_sizes)
max_new = max(new_sizes)

print("\n" + "=" * 65)
print("  AGGREGATE RESULTS")
print("=" * 65)
print(f"  Average old prompt : {avg_old:,} chars")
print(f"  Average new prompt : {avg_new:,} chars")
print(f"  Average reduction  : {avg_red}%")
print(f"  Fastest (min new)  : {min_new:,} chars")
print(f"  Slowest (max new)  : {max_new:,} chars")
print(f"  Target met (>=50%) : {'YES' if avg_red >= 50 else 'NO - NEEDS MORE WORK'}")
print("=" * 65)
