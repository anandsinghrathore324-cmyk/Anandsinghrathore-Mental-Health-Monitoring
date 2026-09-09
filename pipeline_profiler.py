"""
Chatbot Pipeline Performance Profiler
======================================
Instruments each stage of the chatbot execution pipeline with precise
timing measurements. Does NOT modify any existing business logic.

Stages measured:
  1. JWT Token Generation (auth overhead proxy)
  2. AssessmentService (MongoDB profile + report + history queries)
  3. CrisisHandler Detection
  4. PromptBuilder Assembly
  5. MongoDB Queries (isolated sub-timing inside AssessmentService)
  6. Ollama HTTP Request + LLM Generation (total roundtrip)
  7. Response Serialization
"""

import sys
import time
import json
import jwt
import datetime
import requests

# Force UTF-8 output on Windows terminals to avoid cp1252 UnicodeEncodeError
sys.stdout.reconfigure(encoding="utf-8")

import os as _os
# Resolve the backend directory via glob to avoid the curly-quote character in the path
import glob as _glob
_matches = _glob.glob(_os.path.expanduser(r"~\OneDrive\Desktop\Social*\backend"))
if not _matches:
    raise RuntimeError("Cannot locate backend directory. Ensure the project is on the Desktop.")
sys.path.append(_matches[0])



from config import Config
from database.db import db_manager
from database.user_model import UserModel
from database.report_model import ReportModel
from database.chatbot_model import ChatbotModel
from chatbot.crisis_handler import CrisisHandler
from chatbot.prompt_builder import build_prompt
from chatbot.ollama_client import OLLAMA_URL, OLLAMA_MODEL

# ── Config ────────────────────────────────────────────────────────────────────
STUDENT_EMAIL = "student@aira.edu"
OLLAMA_PAYLOAD_OPTIONS = {"num_predict": 200, "temperature": 0.7}

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

# ── Helpers ───────────────────────────────────────────────────────────────────
def ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


def print_separator():
    print("-" * 68)


# ── Connect to DB ─────────────────────────────────────────────────────────────
db_manager.connect()

# Fetch user
user = db_manager.db.users.find_one({"email": STUDENT_EMAIL})
if not user:
    print(f"[ERROR] User {STUDENT_EMAIL} not found. Run the app and register first.")
    sys.exit(1)
user_id = str(user["_id"])

# ── Results store ─────────────────────────────────────────────────────────────
all_runs = []

print("=" * 68)
print("    AIRA CHATBOT PIPELINE PERFORMANCE PROFILER")
print(f"    Student: {STUDENT_EMAIL}  |  User ID: {user_id}")
print(f"    Messages: {len(TEST_MESSAGES)}")
print("=" * 68)

# Pre-warm the NLP/DistilBERT model before timed runs to eliminate cold-start bias
print("\n[WARMUP] Pre-loading NLP model to eliminate first-run bias...", end="", flush=True)
try:
    from chatbot.crisis_handler import CrisisHandler as _CH
    _CH.detect_crisis("warmup message", user_id=None)
    print(" done.")
except Exception as _e:
    print(f" skipped ({_e}).")

for run_idx, message in enumerate(TEST_MESSAGES, 1):
    print(f"\n[Run #{run_idx}] Message: \"{message}\"")
    print_separator()
    run = {}

    # ── Stage 1: JWT Token Generation ─────────────────────────────────────────
    t0 = time.perf_counter()
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRATION_HOURS)
    token_payload = {
        "sub": user_id,
        "exp": expiration,
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(token_payload, Config.JWT_SECRET_KEY, algorithm="HS256")
    run["jwt_ms"] = ms(t0)
    print(f"  JWT Token Generation    : {run['jwt_ms']} ms")

    # ── Stage 2: CrisisHandler Detection ─────────────────────────────────────
    t0 = time.perf_counter()
    crisis_result = CrisisHandler.detect_crisis(message, user_id)
    run["crisis_ms"] = ms(t0)
    print(f"  CrisisHandler Detection : {run['crisis_ms']} ms  "
          f"[is_crisis={crisis_result['is_crisis']}, confidence={crisis_result['confidence']}]")

    # ── Stage 3: AssessmentService (with sub-timings per MongoDB query) ────────
    t_assess = time.perf_counter()

    # 3a. User profile query
    t0 = time.perf_counter()
    profile_doc = db_manager.db.users.find_one({"_id": user["_id"]}) or {}
    run["mongo_user_ms"] = ms(t0)

    # 3b. Report query
    t0 = time.perf_counter()
    reports = ReportModel.get_user_reports(user_id, limit=1)
    run["mongo_report_ms"] = ms(t0)
    latest_report = reports[0] if reports else None

    # 3c. Chat history query
    t0 = time.perf_counter()
    chats = ChatbotModel.get_chat_history(user_id, limit=5)
    run["mongo_history_ms"] = ms(t0)

    # Assemble context dict
    scores = {
        "stress": latest_report.get("stress_score", 0) if latest_report else 0,
        "anxiety": latest_report.get("anxiety_score", 0) if latest_report else 0,
        "depression": latest_report.get("depression_score", 0) if latest_report else 0,
        "burnout": latest_report.get("burnout_score", 0) if latest_report else 0,
        "wellness": latest_report.get("wellness_score", 100) if latest_report else 100,
        "emotion": latest_report.get("emotion", "Calm") if latest_report else "Calm",
        "risk_level": latest_report.get("risk_level", "Low") if latest_report else "Low",
        "prediction_reliability": (
            latest_report.get("explainability", {}).get("prediction_reliability", "High")
            if latest_report else "High"
        )
    }
    recommendations = latest_report.get("recommendations", []) if latest_report else []
    history = []
    for chat in chats:
        if chat.get("message"):
            history.append({"role": "student", "message": chat["message"]})
        if chat.get("response"):
            history.append({"role": "aira", "message": chat["response"]})

    run["assess_ms"] = ms(t_assess)
    print(f"  AssessmentService Total : {run['assess_ms']} ms")
    print(f"    -> MongoDB User Query  : {run['mongo_user_ms']} ms")
    print(f"    -> MongoDB Report Query: {run['mongo_report_ms']} ms")
    print(f"    -> MongoDB Hist. Query : {run['mongo_history_ms']} ms")

    # ── Stage 4: PromptBuilder ────────────────────────────────────────────────
    t0 = time.perf_counter()
    if crisis_result["is_crisis"]:
        prompt = CrisisHandler.build_crisis_prompt(message, user_id)
    else:
        profile = {}
        if profile_doc.get("name"):
            profile["name"] = profile_doc["name"]
        if profile_doc.get("gender"):
            profile["gender"] = profile_doc["gender"]
        prompt = build_prompt(
            user_message=message,
            emotion=scores["emotion"],
            stress=scores["stress"],
            anxiety=scores["anxiety"],
            depression=scores["depression"],
            burnout=scores["burnout"],
            wellness=scores["wellness"],
            risk_level=scores["risk_level"],
            prediction_reliability=scores["prediction_reliability"],
            recommendations=recommendations,
            history=history if history else None,
            student_profile=profile if profile else None
        )
    run["prompt_ms"] = ms(t0)
    prompt_branch = "CrisisHandler.build_crisis_prompt" if crisis_result["is_crisis"] else "PromptBuilder.build_prompt"
    print(f"  PromptBuilder Assembly  : {run['prompt_ms']} ms  [{prompt_branch}]")
    run["prompt_chars"] = len(prompt)
    print(f"    -> Prompt length       : {run['prompt_chars']} characters")

    # ── Stage 5: Ollama HTTP Request + LLM Generation ─────────────────────────
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": OLLAMA_PAYLOAD_OPTIONS
    }
    t0 = time.perf_counter()
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
        resp.raise_for_status()
        ollama_data = resp.json()
        run["ollama_total_ms"] = ms(t0)
        # Ollama returns its own timings in nanoseconds
        run["ollama_prompt_eval_ms"] = round(ollama_data.get("prompt_eval_duration", 0) / 1_000_000, 2)
        run["ollama_gen_ms"] = round(ollama_data.get("eval_duration", 0) / 1_000_000, 2)
        run["ollama_load_ms"] = round(ollama_data.get("load_duration", 0) / 1_000_000, 2)
        run["ollama_tokens"] = ollama_data.get("eval_count", 0)
        llm_response = ollama_data.get("response", "")
    except Exception as e:
        run["ollama_total_ms"] = ms(t0)
        run["ollama_prompt_eval_ms"] = 0
        run["ollama_gen_ms"] = 0
        run["ollama_load_ms"] = 0
        run["ollama_tokens"] = 0
        llm_response = f"[ERROR: {e}]"

    print(f"  Ollama Total Roundtrip  : {run['ollama_total_ms']} ms")
    print(f"    -> Model Load/Cache    : {run['ollama_load_ms']} ms")
    print(f"    -> Prompt Evaluation   : {run['ollama_prompt_eval_ms']} ms")
    print(f"    -> LLM Token Gen.      : {run['ollama_gen_ms']} ms  [{run['ollama_tokens']} tokens]")

    # ── Stage 6: Response Serialization ───────────────────────────────────────
    t0 = time.perf_counter()
    serialized = json.dumps({
        "status": "success",
        "message": "AI reply compiled successfully.",
        "response": llm_response
    })
    run["serialize_ms"] = ms(t0)
    print(f"  Response Serialization  : {run['serialize_ms']} ms")

    # ── Pipeline Total ────────────────────────────────────────────────────────
    run["total_ms"] = round(
        run["jwt_ms"] + run["crisis_ms"] + run["assess_ms"] +
        run["prompt_ms"] + run["ollama_total_ms"] + run["serialize_ms"],
        2
    )
    print(f"  {'─' * 44}")
    print(f"  PIPELINE TOTAL          : {run['total_ms']} ms")

    all_runs.append(run)

# ── Aggregate Report ──────────────────────────────────────────────────────────
def stats(key):
    vals = [r[key] for r in all_runs]
    return min(vals), max(vals), round(sum(vals) / len(vals), 2)

print("\n\n" + "=" * 68)
print("    AGGREGATE PERFORMANCE REPORT")
print(f"    Total Runs: {len(all_runs)}")
print("=" * 68)

stages = [
    ("JWT Token Generation",    "jwt_ms"),
    ("CrisisHandler Detection", "crisis_ms"),
    ("AssessmentService Total", "assess_ms"),
    ("  MongoDB User Query",    "mongo_user_ms"),
    ("  MongoDB Report Query",  "mongo_report_ms"),
    ("  MongoDB Hist. Query",   "mongo_history_ms"),
    ("PromptBuilder Assembly",  "prompt_ms"),
    ("Ollama Total Roundtrip",  "ollama_total_ms"),
    ("  Model Load/Cache",      "ollama_load_ms"),
    ("  Prompt Evaluation",     "ollama_prompt_eval_ms"),
    ("  LLM Token Generation",  "ollama_gen_ms"),
    ("Response Serialization",  "serialize_ms"),
    ("PIPELINE TOTAL",          "total_ms"),
]

print(f"\n{'Stage':<30}  {'Min':>10}  {'Max':>10}  {'Avg':>10}")
print("-" * 68)
for label, key in stages:
    lo, hi, avg = stats(key)
    sep = "  " if not label.startswith("PIPELINE") else "  "
    print(f"{label:<30}  {lo:>8.1f}ms  {hi:>8.1f}ms  {avg:>8.1f}ms")

print("=" * 68)
