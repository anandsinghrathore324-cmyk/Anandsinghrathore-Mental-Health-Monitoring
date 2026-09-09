"""
Wellness Coach — Verification Suite
Tests all 5 intent modes and multi-turn coaching sequences.
"""
import sys, glob, os
sys.stdout.reconfigure(encoding="utf-8")
matches = glob.glob(os.path.expanduser(r"~\OneDrive\Desktop\Social*\backend"))
if not matches:
    raise RuntimeError("Backend not found.")
sys.path.insert(0, matches[0])

from chatbot.wellness_coach import WellnessCoach

assessment = {
    "emotion": "Anxious", "stress": 72, "anxiety": 65,
    "depression": 48, "burnout": 61, "wellness": 38, "risk_level": "Moderate"
}

def test(label, message, history=None, coaching_context=None, assessment=assessment):
    d = WellnessCoach.classify_intent(message, history, assessment, coaching_context)
    c = WellnessCoach.build_coaching_context(coaching_context, d, message)
    print(f"\n  [{label}]")
    print(f"  Message  : \"{message}\"")
    print(f"  Mode     : {d['mode']}")
    print(f"  Action   : {d['action_type']}")
    print(f"  Confidence: {d['confidence']}")
    print(f"  Follow-up: {d['follow_up_question'] or '(none)'}")
    print(f"  Goal set : {d['coaching_goal'] or '(none)'}")
    print(f"  Reasoning: {d['reasoning']}")
    return d, c

print("=" * 65)
print("  WELLNESS COACH VERIFICATION SUITE")
print("=" * 65)

print("\n--- SINGLE-TURN INTENT CLASSIFICATION ---")
test("Pure Venting",          "I'm so fed up with everything, I just want to scream.")
test("Seeking Advice",        "I don't know what to do anymore. Can you help me?")
test("Goal Planning",         "I have a Physics exam on Monday and 4 chapters left.")
test("Crisis intercept",      "I don't want to live anymore.")
test("Off-topic (no signals)","The weather is really nice today.")
test("Burnout venting",       "I don't want to study anymore. I'm so tired.")
test("Advice with ?",         "How do I deal with exam pressure?")
test("Planning with subject", "I need to study Calculus for my final on Friday.")

print("\n--- MULTI-TURN COACHING SEQUENCE (Exam Stress) ---")
# Turn 1: venting
d1, ctx1 = test("Turn 1 - Venting", "I'm overwhelmed by my exams.")

# Turn 2: goal planning emerges
d2, ctx2 = test("Turn 2 - Planning", "I have Physics on Monday.", coaching_context=ctx1)

# Turn 3: progress update
d3, ctx3 = test("Turn 3 - Progress", "I finished 2 chapters last night.", coaching_context=ctx2)

print("\n--- COACHING PROMPT SAMPLE ---")
d_adv, ctx_adv = WellnessCoach.classify_intent(
    "I don't know how to start studying for my exam.",
    assessment=assessment
), {}
if isinstance(d_adv, tuple): d_adv = d_adv[0]
d_adv = WellnessCoach.classify_intent("I don't know how to start studying for my exam.", assessment=assessment)
prompt = WellnessCoach.build_coaching_prompt(
    "I don't know how to start studying for my exam.", d_adv,
    coaching_context=None, assessment=assessment
)
print(f"\n  Generated coaching prompt ({len(prompt)} chars):")
print("  " + "\n  ".join(prompt.split("\n\n")))

print("\n" + "=" * 65)
print("  VERIFICATION COMPLETE")
print("=" * 65)
