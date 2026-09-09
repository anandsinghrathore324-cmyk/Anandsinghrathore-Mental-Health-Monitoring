"""
Chatbot Pipeline Performance Profiler — Phase 2
================================================
Compares Phase 1 baseline (num_predict=200) vs Phase 2 optimized settings.
Reports: total latency, prompt eval time, token gen time, token count, % improvement.
"""
import sys, time, json, jwt, datetime, requests, glob, os

sys.stdout.reconfigure(encoding="utf-8")

matches = glob.glob(os.path.expanduser(r"~\OneDrive\Desktop\Social*\backend"))
if not matches:
    raise RuntimeError("Backend not found.")
sys.path.insert(0, matches[0])

from config import Config
from database.db import db_manager
from database.report_model import ReportModel
from database.chatbot_model import ChatbotModel
from chatbot.prompt_builder import build_prompt

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"
STUDENT_EMAIL = "student@aira.edu"

# Phase 1 baseline options
PHASE1_OPTIONS = {
    "num_predict": 200,
    "temperature": 0.7,
}

# Phase 2 optimized options
PHASE2_OPTIONS = {
    "num_predict":    160,
    "stop":           ["\nStudent:", "\nS:", "\n\nStudent", "\n\nS:"],
    "temperature":    0.7,
    "top_p":          0.9,
    "top_k":          40,
    "repeat_penalty": 1.15,
}

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

def ms(ns: int) -> float:
    return round(ns / 1_000_000, 2)

db_manager.connect()
user = db_manager.db.users.find_one({"email": STUDENT_EMAIL})
if not user:
    raise RuntimeError(f"{STUDENT_EMAIL} not found.")
user_id = str(user["_id"])

# Generate JWT
expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
token = jwt.encode({"sub": user_id, "exp": expiration}, Config.JWT_SECRET_KEY, algorithm="HS256")

# Build a representative prompt using the optimized prompt_builder
reports = ReportModel.get_user_reports(user_id, limit=1)
latest  = reports[0] if reports else {}
chats   = ChatbotModel.get_chat_history(user_id, limit=5)
history = []
for c in chats:
    if c.get("message"): history.append({"role": "student", "message": c["message"]})
    if c.get("response"): history.append({"role": "aira",    "message": c["response"]})

profile_doc = db_manager.db.users.find_one({"_id": user["_id"]}) or {}
profile = {}
if profile_doc.get("name"):   profile["name"]   = profile_doc["name"]
if profile_doc.get("gender"): profile["gender"] = profile_doc["gender"]

scores = {
    "emotion":                latest.get("emotion", "Calm"),
    "stress":                 latest.get("stress_score", 0),
    "anxiety":                latest.get("anxiety_score", 0),
    "depression":             latest.get("depression_score", 0),
    "burnout":                latest.get("burnout_score", 0),
    "wellness":               latest.get("wellness_score", 100),
    "risk_level":             latest.get("risk_level", "Low"),
    "prediction_reliability": latest.get("explainability", {}).get("prediction_reliability", "High"),
}
recommendations = latest.get("recommendations", [])

print("=" * 70)
print("  PHASE 2 — OLLAMA GENERATION OPTIMIZATION BENCHMARK")
print(f"  Model: {OLLAMA_MODEL}  |  User: {STUDENT_EMAIL}")
print("=" * 70)

# Warmup
print("\n[WARMUP] Sending warmup request to load model...", end="", flush=True)
try:
    requests.post(OLLAMA_URL, json={"model": OLLAMA_MODEL, "prompt": "Hi", "stream": False, "options": PHASE2_OPTIONS}, timeout=120)
    print(" done.")
except:
    print(" failed (continuing).")

p1_results = []
p2_results = []

for idx, msg in enumerate(TEST_MESSAGES, 1):
    prompt = build_prompt(
        user_message=msg,
        recommendations=recommendations,
        history=history if history else None,
        student_profile=profile if profile else None,
        **scores
    )
    prompt_chars = len(prompt)

    print(f"\n[Run #{idx}] \"{msg[:50]}\"")
    print(f"  Prompt: {prompt_chars} chars")

    def call_ollama(options, label):
        payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": options}
        t0 = time.perf_counter()
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        wall_ms = round((time.perf_counter() - t0) * 1000, 2)
        d = resp.json()
        return {
            "wall_ms":      wall_ms,
            "eval_ms":      ms(d.get("eval_duration", 0)),
            "prompt_ms":    ms(d.get("prompt_eval_duration", 0)),
            "load_ms":      ms(d.get("load_duration", 0)),
            "tokens":       d.get("eval_count", 0),
            "response":     d.get("response", ""),
        }

    r1 = call_ollama(PHASE1_OPTIONS, "Phase1")
    r2 = call_ollama(PHASE2_OPTIONS, "Phase2")

    p1_results.append(r1)
    p2_results.append(r2)

    improvement = round((1 - r2["wall_ms"] / r1["wall_ms"]) * 100, 1)
    tok_diff    = r1["tokens"] - r2["tokens"]

    print(f"  {'Phase 1':30s}  {'Phase 2':30s}")
    print(f"  {'Wall time: ' + str(r1['wall_ms']) + ' ms':30s}  {'Wall time: ' + str(r2['wall_ms']) + ' ms':30s}")
    print(f"  {'Prompt eval: ' + str(r1['prompt_ms']) + ' ms':30s}  {'Prompt eval: ' + str(r2['prompt_ms']) + ' ms':30s}")
    print(f"  {'Token gen: ' + str(r1['eval_ms']) + ' ms':30s}  {'Token gen: ' + str(r2['eval_ms']) + ' ms':30s}")
    print(f"  {'Tokens: ' + str(r1['tokens']):30s}  {'Tokens: ' + str(r2['tokens']):30s}")
    print(f"  Improvement: {improvement}%  |  Tokens saved: {tok_diff}")

# Aggregate
def avg(lst, key):
    return round(sum(r[key] for r in lst) / len(lst), 2)

print("\n\n" + "=" * 70)
print("  AGGREGATE — PHASE 1 vs PHASE 2")
print("=" * 70)
metrics = [
    ("Wall time (ms)",     "wall_ms"),
    ("Prompt eval (ms)",   "prompt_ms"),
    ("Token gen (ms)",     "eval_ms"),
    ("Tokens generated",   "tokens"),
]

print(f"\n{'Metric':<25}  {'Phase 1':>12}  {'Phase 2':>12}  {'Improvement':>12}")
print("-" * 70)
for label, key in metrics:
    a1 = avg(p1_results, key)
    a2 = avg(p2_results, key)
    pct = round((1 - a2/a1)*100, 1) if a1 else 0
    unit = "ms" if "ms" in label else ""
    print(f"{label:<25}  {str(a1)+unit:>12}  {str(a2)+unit:>12}  {str(pct)+'%':>12}")

print("=" * 70)
