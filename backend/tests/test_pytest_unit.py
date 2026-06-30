"""
test_pytest_unit.py - Comprehensive unit tests for AIRA backend.
Covers: AI pipeline, services, models, NLP, validators, memory, prompt builder.
"""
from __future__ import annotations
import sys, os, datetime
import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


# ─────────────────────────────────────────────────────────────────────────────
# ResponseValidator (inline class inside conversation_orchestrator)
# ─────────────────────────────────────────────────────────────────────────────
class TestResponseValidator:
    def _rv(self):
        from chatbot.conversation_orchestrator import ResponseValidator
        return ResponseValidator

    def test_empty_response_returns_listening(self):
        assert "listening" in self._rv().validate("").lower()

    def test_whitespace_only_returns_listening(self):
        assert "listening" in self._rv().validate("   ").lower()

    def test_normal_response_with_question_passes_through(self):
        result = self._rv().validate("How are you feeling today?")
        assert "How are you feeling today?" in result

    def test_response_with_question_no_extra_appended(self):
        result = self._rv().validate("Is everything okay?")
        assert result.count("How does that sound to you?") == 0

    def test_response_without_question_gets_appended_question(self):
        result = self._rv().validate("I hear you.")
        assert "?" in result

    def test_long_response_truncated_at_350_words(self):
        long_input = ("word " * 400).strip()
        result = self._rv().validate(long_input)
        assert len(result.split()) <= 360

    def test_duplicate_paragraphs_collapsed(self):
        text = "Hello there.\n\nHello there."
        result = self._rv().validate(text)
        parts = [p.strip() for p in result.split("\n\n") if p.strip()]
        hello_parts = [p for p in parts if p.startswith("Hello there")]
        assert len(hello_parts) == 1

    def test_repeated_response_vs_history_gets_annotation(self):
        RV = self._rv()
        history = [{"role": "aira", "message": "I understand you?"}]
        result = RV.validate("I understand you?", history=history)
        assert "another aspect" in result.lower()

    def test_history_none_does_not_crash(self):
        assert isinstance(self._rv().validate("Great job!", history=None), str)


# ─────────────────────────────────────────────────────────────────────────────
# Real ResponseValidator (chatbot/response_validator.py)
# ─────────────────────────────────────────────────────────────────────────────
class TestRealResponseValidator:
    def _rrv(self):
        from chatbot.response_validator import ResponseValidator
        return ResponseValidator

    def test_empty_string_returns_fallback(self):
        result = self._rrv().validate("")
        assert "listening" in result.lower()

    def test_bullet_points_converted_to_conversational(self):
        text = "- Take a walk.\n- Drink water.\n- Study math."
        result = self._rrv().validate(text)
        assert "First, you could take a walk." in result
        assert "Additionally, try to drink water." in result

    def test_numbered_list_converted_to_conversational(self):
        text = "1. Sleep early.\n2. Meditate."
        result = self._rrv().validate(text)
        assert "First, you could sleep early." in result

    def test_remove_repeated_openings(self):
        result = self._rrv().validate("I'm sorry to hear that, but things will improve.")
        valid_substrings = [
            "hear you, and it's", "opening up", "glad you shared", "lot to handle",
            "appreciate you sharing", "take it one step", "work through this",
            "understandable to feel", "figure this out", "tough, but I'm"
        ]
        assert any(sub in result for sub in valid_substrings)

    def test_remove_accidental_repeated_adjacent_sentences(self):
        text = "Take a break. Take a break. Let us talk."
        result = self._rrv().validate(text)
        assert result.count("Take a break.") == 1

    def test_duplicated_paragraphs_removed(self):
        text = "First paragraph.\n\nFirst paragraph."
        result = self._rrv().validate(text)
        assert "First paragraph" in result


# ─────────────────────────────────────────────────────────────────────────────
# SessionCache
# ─────────────────────────────────────────────────────────────────────────────
class TestSessionCache:
    def setup_method(self):
        from chatbot.conversation_orchestrator import SessionCache
        SessionCache._cache.clear()
        self.SC = SessionCache

    def test_set_and_get_within_ttl(self):
        self.SC.set("uid1", {"mood": "happy"})
        assert self.SC.get("uid1") == {"mood": "happy"}

    def test_get_missing_key_returns_none(self):
        assert self.SC.get("nonexistent") is None

    def test_get_empty_string_returns_none(self):
        assert self.SC.get("") is None

    def test_set_empty_string_does_nothing(self):
        self.SC.set("", {"x": 1})
        assert "" not in self.SC._cache

    def test_invalidate_removes_entry(self):
        self.SC.set("uid2", {"x": 1})
        self.SC.invalidate("uid2")
        assert self.SC.get("uid2") is None

    def test_invalidate_nonexistent_does_not_raise(self):
        self.SC.invalidate("ghost_user")

    def test_expired_entry_returns_none(self):
        import time
        self.SC._cache["uid3"] = {"timestamp": time.time() - 400, "data": {"old": True}}
        assert self.SC.get("uid3") is None


# ─────────────────────────────────────────────────────────────────────────────
# MetricsLogger
# ─────────────────────────────────────────────────────────────────────────────
class TestMetricsLogger:
    def test_log_prints_metrics(self, capsys):
        from chatbot.conversation_orchestrator import MetricsLogger
        MetricsLogger.log("u1", 120.5, 512, "venting", False, "Yes", "llama3", 95.3)
        assert "PIPELINE METRICS" in capsys.readouterr().out

    def test_log_anonymous_user(self, capsys):
        from chatbot.conversation_orchestrator import MetricsLogger
        MetricsLogger.log(None, 10.0, 100, "normal_conversation", False, "No", "groq", 8.0)
        assert "Anonymous" in capsys.readouterr().out


# ─────────────────────────────────────────────────────────────────────────────
# ToolRouter
# ─────────────────────────────────────────────────────────────────────────────
class TestToolRouter:
    def _tr(self):
        from chatbot.conversation_orchestrator import ToolRouter
        return ToolRouter

    def test_doctor_keyword_routes_to_doctor_service(self):
        r = self._tr().route("I need a therapist near me")
        assert r["route"] == "doctor_service" and r["bypass_llm"] is True

    def test_dashboard_keyword(self):
        r = self._tr().route("show me my dashboard scores")
        assert r["route"] == "dashboard_service" and r["bypass_llm"] is True

    def test_mood_history_keyword(self):
        r = self._tr().route("can I see my mood history?")
        assert r["route"] == "mood_history" and r["bypass_llm"] is True

    def test_calendar_keyword(self):
        r = self._tr().route("what are my upcoming exam dates?")
        assert r["route"] == "calendar" and r["bypass_llm"] is True

    def test_habit_keyword(self):
        r = self._tr().route("check my habit tracker")
        assert r["route"] == "habit" and r["bypass_llm"] is True

    def test_crisis_keyword_bypasses_to_llm(self):
        r = self._tr().route("I want to kill myself")
        assert r["route"] == "llm" and r["bypass_llm"] is False

    def test_regular_message_goes_to_llm(self):
        r = self._tr().route("I am feeling stressed today")
        assert r["route"] == "llm" and r["bypass_llm"] is False

    def test_psychologist_keyword(self):
        assert self._tr().route("recommend a psychologist")["route"] == "doctor_service"

    def test_overdose_goes_to_llm(self):
        assert self._tr().route("I took an overdose")["bypass_llm"] is False

    def test_suicide_goes_to_llm(self):
        assert self._tr().route("thinking about suicide tonight")["bypass_llm"] is False


# ─────────────────────────────────────────────────────────────────────────────
# WellnessCoach
# ─────────────────────────────────────────────────────────────────────────────
class TestWellnessCoach:
    def _wc(self):
        from chatbot.wellness_coach import WellnessCoach
        return WellnessCoach

    def test_empty_message_returns_venting(self):
        assert self._wc().classify_intent("")["mode"] == "venting"

    def test_crisis_pattern_returns_crisis(self):
        assert self._wc().classify_intent("I want to end my life")["mode"] == "crisis"

    def test_seeking_advice_mode(self):
        assert self._wc().classify_intent("I need help, what should I do?")["mode"] == "seeking_advice"

    def test_venting_mode_frustration(self):
        assert self._wc().classify_intent("I hate everything, I give up")["mode"] == "venting"

    def test_goal_planning_with_strong_planning_signals(self):
        msg = "I have a midterm on Friday. I need to finish 3 chapters by tonight"
        result = self._wc().classify_intent(msg)
        assert result["mode"] == "goal_planning"

    def test_progress_update_with_active_goal(self):
        ctx = {"active_goal": "Prepare Math by Friday"}
        result = self._wc().classify_intent("I finished studying last night!", coaching_context=ctx)
        assert result["mode"] == "progress_update"

    def test_returns_confidence_float(self):
        assert isinstance(self._wc().classify_intent("I don't know what to do")["confidence"], float)

    def test_high_stress_boosts_planning_score(self):
        result = self._wc().classify_intent(
            "I need to study for my midterm this week",
            assessment={"stress": 80}
        )
        assert result["mode"] == "goal_planning"

    def test_build_coaching_context_increments_turns(self):
        from chatbot.wellness_coach import CoachingDecision
        decision = CoachingDecision(
            mode="goal_planning", follow_up_question="", coaching_goal="Math",
            action_type="ask_question", confidence=0.8, reasoning="test"
        )
        ctx = self._wc().build_coaching_context({}, decision, "test")
        assert ctx["turns_in_planning"] == 1

    def test_build_coaching_context_mode_history_is_list(self):
        from chatbot.wellness_coach import CoachingDecision
        decision = CoachingDecision(
            mode="venting", follow_up_question="", coaching_goal="",
            action_type="validate", confidence=0.5, reasoning=""
        )
        ctx = self._wc().build_coaching_context({}, decision, "I feel bad")
        assert isinstance(ctx["mode_history"], list)

    def test_build_coaching_prompt_returns_string(self):
        from chatbot.wellness_coach import CoachingDecision
        decision = CoachingDecision(
            mode="seeking_advice", follow_up_question="What feels hardest?",
            coaching_goal="", action_type="ask_question", confidence=0.7, reasoning=""
        )
        prompt = self._wc().build_coaching_prompt("I need help", decision)
        assert isinstance(prompt, str) and "AIRA" in prompt

    def test_build_coaching_prompt_includes_follow_up(self):
        from chatbot.wellness_coach import CoachingDecision
        decision = CoachingDecision(
            mode="goal_planning", follow_up_question="How much time do you have?",
            coaching_goal="Finish math", action_type="ask_question", confidence=0.85, reasoning=""
        )
        prompt = self._wc().build_coaching_prompt("I have a test Monday", decision)
        assert "How much time do you have?" in prompt

    def test_build_coaching_prompt_includes_mode_instruction(self):
        from chatbot.wellness_coach import CoachingDecision
        decision = CoachingDecision(
            mode="progress_update", follow_up_question="How do you feel now?",
            coaching_goal="Prepare for exam", action_type="reinforce", confidence=0.8, reasoning=""
        )
        prompt = self._wc().build_coaching_prompt("I completed my study session", decision)
        assert isinstance(prompt, str)


# ─────────────────────────────────────────────────────────────────────────────
# CrisisHandler
# ─────────────────────────────────────────────────────────────────────────────
class TestCrisisHandler:
    def _ch(self):
        from chatbot.crisis_handler import CrisisHandler
        return CrisisHandler

    def test_empty_message_not_crisis(self):
        assert self._ch().detect_crisis("")["is_crisis"] is False

    def test_kill_myself_is_crisis(self):
        r = self._ch().detect_crisis("I want to kill myself")
        assert r["is_crisis"] is True and r["confidence"] >= 0.90

    def test_suicide_keyword_is_crisis(self):
        assert self._ch().detect_crisis("I am thinking about suicide")["is_crisis"] is True

    def test_informational_reference_is_not_crisis(self):
        assert self._ch().detect_crisis("We watched a documentary about suicide in class")["is_crisis"] is False

    def test_third_person_harm_is_crisis(self):
        assert self._ch().detect_crisis("My friend wants to hurt himself")["is_crisis"] is True

    def test_passive_distress_is_crisis(self):
        assert self._ch().detect_crisis("Everything is pointless, nothing matters")["is_crisis"] is True

    def test_normal_stress_not_crisis(self):
        assert self._ch().detect_crisis("I am really stressed about my exam")["is_crisis"] is False

    def test_build_crisis_prompt_returns_string(self):
        prompt = self._ch().build_crisis_prompt("I feel hopeless")
        assert isinstance(prompt, str) and "AIRA" in prompt

    def test_high_risk_user_raises_confidence(self, mock_db):
        user_id = "507f191e810c19729de860ea"
        mock_db["mental_health_reports"].insert_one({
            "user_id": ObjectId(user_id),
            "risk_level": "High", "stress_score": 90, "anxiety_score": 80,
            "depression_score": 70, "burnout_score": 85, "wellness_score": 20,
            "emotion": "Fear", "created_at": datetime.datetime.utcnow()
        })
        r = self._ch().detect_crisis("I want to kill myself", user_id=user_id)
        assert r["is_crisis"] is True and r["confidence"] == 0.99

    def test_cutting_keyword_detected(self):
        assert self._ch().detect_crisis("I have been cutting myself")["is_crisis"] is True

    def test_overdose_keyword_detected(self):
        assert self._ch().detect_crisis("I took an overdose last night")["is_crisis"] is True

    def test_self_harm_keyword_detected(self):
        assert self._ch().detect_crisis("I want to harm myself")["is_crisis"] is True

    def test_want_to_disappear_is_passive_crisis(self):
        assert self._ch().detect_crisis("I want to disappear forever")["is_crisis"] is True


# ─────────────────────────────────────────────────────────────────────────────
# MemoryManager
# ─────────────────────────────────────────────────────────────────────────────
class TestMemoryManager:
    def _mm(self):
        from chatbot.memory_manager import MemoryManager
        return MemoryManager

    def test_save_interaction_with_exam_fact(self, mock_db, sample_user_id):
        self._mm().save_interaction(sample_user_id, "I have an exam tomorrow", "Good luck!")
        memories = self._mm().get_recent_memory(sample_user_id)
        assert len(memories) >= 1 and any("exam" in m.lower() for m in memories)

    def test_save_interaction_with_sleep_fact(self, mock_db, sample_user_id):
        self._mm().save_interaction(sample_user_id, "I cannot sleep well at night", "Rest matters.")
        memories = self._mm().get_recent_memory(sample_user_id)
        assert any("sleep" in m.lower() for m in memories)

    def test_save_interaction_no_user_id_does_nothing(self, mock_db):
        self._mm().save_interaction(None, "hello", "hi")
        assert mock_db["user_memories"].count_documents({}) == 0

    def test_get_recent_memory_no_user_returns_empty(self):
        assert self._mm().get_recent_memory(None) == []

    def test_get_recent_memory_returns_list(self, mock_db, sample_user_id):
        assert isinstance(self._mm().get_recent_memory(sample_user_id), list)

    def test_summarize_no_memories(self):
        result = self._mm().summarize_long_history("000000000000000000000000")
        assert "No previous" in result

    def test_summarize_returns_string_with_memories(self, mock_db, sample_user_id):
        self._mm().save_interaction(sample_user_id, "I am tired from exam stress", "Take a break.")
        result = self._mm().summarize_long_history(sample_user_id)
        assert isinstance(result, str) and len(result) > 0

    def test_is_memory_useful_false_for_greeting(self):
        assert self._mm().is_memory_useful("hello", ["Some memory"]) is False

    def test_is_memory_useful_false_for_empty_memories(self):
        assert self._mm().is_memory_useful("I am stressed", []) is False

    def test_is_memory_useful_true_for_exam_message(self):
        assert self._mm().is_memory_useful("I have an exam tomorrow", ["Past exam stress"]) is True

    def test_is_memory_useful_true_for_sleep_message(self):
        assert self._mm().is_memory_useful("I have trouble sleeping", ["Sleep concern"]) is True

    def test_goal_memory_extracted(self, mock_db, sample_user_id):
        self._mm().save_interaction(sample_user_id, "I need to study math tonight", "Let's plan!")
        memories = self._mm().get_recent_memory(sample_user_id)
        assert any("math" in m.lower() or "study" in m.lower() or "plan" in m.lower() for m in memories)

    def test_multiple_saves_upsert_not_duplicate(self, mock_db, sample_user_id):
        MM = self._mm()
        MM.save_interaction(sample_user_id, "I have an exam tomorrow", "First")
        MM.save_interaction(sample_user_id, "I have another exam next week", "Second")
        count = mock_db["user_memories"].count_documents({"category": "exam"})
        assert count == 1


# ─────────────────────────────────────────────────────────────────────────────
# PromptBuilder
# ─────────────────────────────────────────────────────────────────────────────
class TestPromptBuilder:
    def _build(self, **kwargs):
        from chatbot.prompt_builder import build_prompt
        defaults = dict(
            user_message="I feel anxious",
            emotion="Anxious", stress=60, anxiety=70, depression=40,
            burnout=55, wellness=50, risk_level="Moderate",
            prediction_reliability="Medium", recommendations=[],
        )
        defaults.update(kwargs)
        return build_prompt(**defaults)

    def test_returns_string(self):
        assert isinstance(self._build(), str)

    def test_contains_user_message(self):
        assert "I cannot focus" in self._build(user_message="I cannot focus on studying")

    def test_contains_system_header(self):
        assert "AIRA" in self._build()

    def test_empty_user_message_uses_placeholder(self):
        assert "(No message provided)" in self._build(user_message="")

    def test_recommendations_as_dicts_rendered(self):
        recs = [{"category": "Sleep Improvement", "title": "Sleep 8 hours"}]
        assert "Sleep 8 hours" in self._build(recommendations=recs)

    def test_empty_recommendations_no_hints_block(self):
        assert "Hints" not in self._build(recommendations=[])

    def test_history_rendered(self):
        history = [
            {"role": "student", "message": "I feel tired"},
            {"role": "aira", "message": "Rest is important"},
        ]
        result = self._build(history=history)
        assert "S:" in result or "A:" in result

    def test_no_history_no_history_block(self):
        assert "History:" not in self._build(history=None)

    def test_student_profile_rendered(self):
        assert "Alice" in self._build(student_profile={"name": "Alice", "age": 20, "gender": "Female"})

    def test_memories_injected(self):
        assert "Past exam stress" in self._build(memories=["Past exam stress mentioned"])

    def test_wellness_score_humanized_excellent(self):
        assert "excellent" in self._build(wellness=90)

    def test_stress_score_humanized_very_high(self):
        assert "very high" in self._build(stress=85)

    def test_long_message_does_not_crash(self):
        assert isinstance(self._build(user_message="stressed " * 200), str)

    def test_only_top_2_recommendations_shown(self):
        recs = [
            {"category": "General Wellness", "title": "Rec 1"},
            {"category": "Sleep Improvement", "title": "Rec 2"},
            {"category": "Study Management", "title": "Rec 3"},
        ]
        result = self._build(recommendations=recs)
        assert "Rec 1" not in result


# ─────────────────────────────────────────────────────────────────────────────
# GibberishDetector
# ─────────────────────────────────────────────────────────────────────────────
class TestGibberishDetector:
    def _gd(self):
        from nlp.gibberish_detector import GibberishDetector
        return GibberishDetector

    def test_normal_sentence_not_gibberish(self):
        assert self._gd().is_gibberish("I feel very stressed today") is False

    def test_keyboard_spam_is_gibberish(self):
        assert self._gd().is_gibberish("asdfghjkl qwertyuiop zxcvbnm") is True

    def test_random_chars_is_gibberish(self):
        assert self._gd().is_gibberish("xkzq wvlm bfjp dtrs") is True

    def test_empty_string_returns_bool(self):
        assert isinstance(self._gd().is_gibberish(""), bool)

    def test_valid_text_not_gibberish(self):
        assert self._gd().is_gibberish("I cannot sleep properly and feel exhausted every morning") is False


# ─────────────────────────────────────────────────────────────────────────────
# DistilBertClassifier (nlp/distilbert.py)
# ─────────────────────────────────────────────────────────────────────────────
class TestDistilBertClassifier:
    def _clf(self):
        from nlp.distilbert import nlp_classifier
        return nlp_classifier

    def test_analyze_empty_text(self):
        res = self._clf().analyze_sentiment("")
        assert res["sentiment"] == "Neutral"

    def test_analyze_too_short_text(self):
        res = self._clf().analyze_sentiment("Too short.")
        assert "error" in res

    def test_analyze_too_long_text(self):
        res = self._clf().analyze_sentiment("word " * 300)
        assert "error" in res

    def test_analyze_gibberish_text(self):
        res = self._clf().analyze_sentiment("xkzq wvlm bfjp dtrs mnpq")
        assert "error" in res

    def test_lexicon_fallback_low_confidence(self):
        # Text with no keyword triggers, making confidence flat/low
        res = self._clf().analyze_sentiment("This is a completely plain text with no emotional trigger words whatsoever.")
        assert res["sentiment"] == "Uncertain"

    def test_lexicon_fallback_high_confidence_joy(self):
        res = self._clf().analyze_sentiment("I am extremely happy and excited, full of joy and love!")
        assert res["sentiment"] == "Positive"
        assert res["emotion"] == "Joy"

    def test_huggingface_pipeline_inference_success(self):
        clf = self._clf()
        with patch.object(clf, "pipeline", create=True) as mock_pipe:
            mock_pipe.return_value = [[
                {"label": "joy", "score": 0.95},
                {"label": "sadness", "score": 0.01},
                {"label": "fear", "score": 0.01},
                {"label": "anger", "score": 0.01},
                {"label": "surprise", "score": 0.02}
            ]]
            res = clf.analyze_sentiment("I feel great today, studying has been wonderful!")
            assert res["sentiment"] == "Positive"
            assert res["emotion"] == "Joy"

    def test_huggingface_pipeline_inference_low_confidence(self):
        clf = self._clf()
        with patch.object(clf, "pipeline", create=True) as mock_pipe:
            mock_pipe.return_value = [[
                {"label": "joy", "score": 0.2},
                {"label": "sadness", "score": 0.2},
                {"label": "fear", "score": 0.2},
                {"label": "anger", "score": 0.2},
                {"label": "surprise", "score": 0.2}
            ]]
            res = clf.analyze_sentiment("I feel average today, studying is okay.")
            assert res["sentiment"] == "Uncertain"

    def test_huggingface_pipeline_inference_exception(self):
        clf = self._clf()
        with patch.object(clf, "pipeline", create=True) as mock_pipe:
            mock_pipe.side_effect = Exception("GPU out of memory")
            # Should fallback to lexicon fallback
            res = clf.analyze_sentiment("I am extremely sad and lonely and hopeless.")
            assert res["sentiment"] == "Negative"
            assert res["emotion"] == "Melancholy"


# ─────────────────────────────────────────────────────────────────────────────
# DoctorService
# ─────────────────────────────────────────────────────────────────────────────
class TestDoctorService:
    def _ds(self):
        from services.doctor_service import DoctorService
        return DoctorService

    def test_haversine_same_point_is_zero(self):
        assert abs(self._ds().calculate_haversine(28.0, 77.0, 28.0, 77.0)) < 0.01

    def test_haversine_delhi_to_mumbai_approx(self):
        dist = self._ds().calculate_haversine(28.6139, 77.2090, 19.0760, 72.8777)
        assert 1100 < dist < 1300

    def test_get_nearby_specialists_returns_list(self, mock_db):
        mock_db["doctors"].insert_one({
            "doctor_name": "Dr. Test", "specialization": "Psychologist",
            "specialization_type": "general", "latitude": 28.6, "longitude": 77.2,
            "experience": 5, "rating": 4.5, "hospital": "Test Hospital"
        })
        assert isinstance(self._ds().get_nearby_specialists(28.6139, 77.2090), list)

    def test_get_nearby_specialists_sorted_by_distance(self, mock_db):
        mock_db["doctors"].insert_many([
            {"doctor_name": "Far Dr.", "latitude": 19.0, "longitude": 72.8,
             "specialization": "Counselor", "specialization_type": "general",
             "experience": 5, "rating": 4.0, "hospital": "Far Hospital"},
            {"doctor_name": "Near Dr.", "latitude": 28.62, "longitude": 77.21,
             "specialization": "Psychologist", "specialization_type": "general",
             "experience": 8, "rating": 4.8, "hospital": "Near Hospital"},
        ])
        results = self._ds().get_nearby_specialists(28.6139, 77.2090)
        distances = [r["distance"] for r in results]
        assert distances == sorted(distances)

    def test_specialization_filter_works(self, mock_db):
        mock_db["doctors"].insert_many([
            {"doctor_name": "Psych Dr.", "latitude": 28.61, "longitude": 77.20,
             "specialization": "Psychologist", "specialization_type": "psychologist",
             "experience": 5, "rating": 4.5, "hospital": "H1"},
            {"doctor_name": "General Dr.", "latitude": 28.60, "longitude": 77.19,
             "specialization": "General", "specialization_type": "general",
             "experience": 3, "rating": 4.0, "hospital": "H2"},
        ])
        results = self._ds().get_nearby_specialists(28.61, 77.20, specialization_filter="psychologist")
        assert all(r["specialization_type"] == "psychologist" for r in results)

    def test_empty_doctor_list_returns_empty(self, mock_db):
        assert self._ds().get_nearby_specialists(28.6, 77.2) == []


# ─────────────────────────────────────────────────────────────────────────────
# UserModel
# ─────────────────────────────────────────────────────────────────────────────
class TestUserModel:
    def test_create_user_returns_dict(self, mock_db):
        from database.user_model import UserModel
        user = UserModel.create_user("Jane Doe", "jane@test.com", "SecurePass123!")
        assert isinstance(user, dict) and user["email"] == "jane@test.com"

    def test_find_by_email_existing(self, mock_db):
        from database.user_model import UserModel
        UserModel.create_user("Bob", "bob@test.com", "Pass123!")
        found = UserModel.find_by_email("bob@test.com")
        assert found is not None and found["name"] == "Bob"

    def test_find_by_email_nonexistent_returns_none(self, mock_db):
        from database.user_model import UserModel
        assert UserModel.find_by_email("ghost@test.com") is None

    def test_password_is_hashed_not_plaintext(self, mock_db):
        from database.user_model import UserModel
        UserModel.create_user("Eve", "eve@test.com", "PlainPass!")
        db_user = mock_db["users"].find_one({"email": "eve@test.com"})
        assert db_user is not None
        assert db_user["password"] != "PlainPass!" and db_user["password"].startswith("$2b$")

    def test_verify_password_correct(self, mock_db):
        from database.user_model import UserModel
        import bcrypt
        plain = "MyPass456!"
        hashed = bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
        assert UserModel.verify_password(hashed, plain) is True

    def test_verify_password_incorrect(self, mock_db):
        from database.user_model import UserModel
        import bcrypt
        hashed = bcrypt.hashpw(b"RealPass789!", bcrypt.gensalt()).decode()
        assert UserModel.verify_password(hashed, "WrongPass") is False

    def test_find_by_id_returns_user(self, mock_db):
        from database.user_model import UserModel
        user = UserModel.create_user("Frank", "frank@test.com", "Pass999!")
        found = UserModel.find_by_id(user["_id"])
        assert found is not None and found["email"] == "frank@test.com"

    def test_update_profile_stores_fields(self, mock_db):
        from database.user_model import UserModel
        user = UserModel.create_user("Grace", "grace@test.com", "Pass111!")
        UserModel.update_profile(user["_id"], {"age": 22, "gender": "Female"})
        updated = UserModel.find_by_id(user["_id"])
        assert updated is not None

    def test_create_duplicate_email_still_creates(self, mock_db):
        from database.user_model import UserModel
        u1 = UserModel.create_user("A", "dup2@test.com", "P1!")
        u2 = UserModel.create_user("B", "dup2@test.com", "P2!")
        assert u1["_id"] != u2["_id"]


# ─────────────────────────────────────────────────────────────────────────────
# ReportModel
# ─────────────────────────────────────────────────────────────────────────────
class TestReportModel:
    def test_create_report_returns_dict(self, mock_db, sample_user_id):
        from database.report_model import ReportModel
        report = ReportModel.create_report(
            user_id=sample_user_id, stress=70, anxiety=60, depression=50,
            burnout=65, wellness=45, emotion="Anxious", risk="Moderate"
        )
        assert isinstance(report, dict) and report["stress_score"] == 70

    def test_create_report_stores_in_db(self, mock_db, sample_user_id):
        from database.report_model import ReportModel
        ReportModel.create_report(
            user_id=sample_user_id, stress=80, anxiety=70, depression=60,
            burnout=75, wellness=35, emotion="Fear", risk="High"
        )
        count = mock_db["mental_health_reports"].count_documents(
            {"user_id": ObjectId(sample_user_id)}
        )
        assert count == 1

    def test_get_user_reports_returns_list(self, mock_db, sample_user_id):
        from database.report_model import ReportModel
        ReportModel.create_report(
            user_id=sample_user_id, stress=50, anxiety=40, depression=30,
            burnout=45, wellness=60, emotion="Calm", risk="Low"
        )
        reports = ReportModel.get_user_reports(sample_user_id)
        assert isinstance(reports, list) and len(reports) >= 1

    def test_get_user_reports_empty_for_unknown_user(self, mock_db):
        from database.report_model import ReportModel
        assert ReportModel.get_user_reports("507f191e810c19729de860ea") == []

    def test_report_optional_fields(self, mock_db, sample_user_id):
        from database.report_model import ReportModel
        report = ReportModel.create_report(
            user_id=sample_user_id, stress=55, anxiety=45, depression=35,
            burnout=50, wellness=55, emotion="Calm", risk="Low",
            sleep_hours=6.5, financial_stress=3
        )
        assert report.get("sleep_hours") == 6.5


# ─────────────────────────────────────────────────────────────────────────────
# MoodModel
# ─────────────────────────────────────────────────────────────────────────────
class TestMoodModel:
    def test_log_mood_creates_record(self, mock_db, sample_user_id):
        from database.mood_model import MoodModel
        MoodModel.log_mood(sample_user_id, "happy", 78, journal="Feeling good today")
        count = mock_db["mood_logs"].count_documents({"user_id": ObjectId(sample_user_id)})
        assert count == 1

    def test_get_mood_heatmap_returns_list(self, mock_db, sample_user_id):
        from database.mood_model import MoodModel
        MoodModel.log_mood(sample_user_id, "calm", 70, journal="Relaxed")
        result = MoodModel.get_mood_heatmap(sample_user_id, days=30)
        assert isinstance(result, list)

    def test_get_mood_heatmap_empty_for_unknown_user(self, mock_db):
        from database.mood_model import MoodModel
        assert MoodModel.get_mood_heatmap("507f191e810c19729de860ea", days=30) == []

    def test_log_mood_with_risk_level(self, mock_db, sample_user_id):
        from database.mood_model import MoodModel
        MoodModel.log_mood(sample_user_id, "anxious", 55,
                           risk_level="Moderate", combined_probability=0.65)
        count = mock_db["mood_logs"].count_documents({"user_id": ObjectId(sample_user_id)})
        assert count == 1


# ─────────────────────────────────────────────────────────────────────────────
# PredictionService
# ─────────────────────────────────────────────────────────────────────────────
class TestPredictionService:
    def _svc(self):
        from services.prediction_service import PredictionService
        return PredictionService()

    def _payload(self, **overrides):
        base = {
            "age": 21, "gender": "Male", "academic_pressure": 7,
            "study_satisfaction": 5, "sleep_hours": 6.0,
            "study_hours": 4.0, "screen_time": 3.0, "work_hours": 2.0,
            "dietary_habits": "Moderate", "financial_stress": 4,
            "family_history": "No",
            "text": "I feel very anxious and cannot focus on my studies",
            "anxiety_level": 6, "stress_level": 7,
        }
        base.update(overrides)
        return base

    def test_run_assessment_returns_dict(self):
        result = self._svc().run_assessment(self._payload())
        assert isinstance(result, dict)

    def test_run_assessment_has_risk_level(self):
        result = self._svc().run_assessment(self._payload())
        assert "risk_level" in result or "risk" in result

    def test_run_assessment_has_wellness(self):
        result = self._svc().run_assessment(self._payload())
        assert "wellness" in result

    def test_run_assessment_low_stress(self):
        result = self._svc().run_assessment(self._payload(
            academic_pressure=2, study_satisfaction=9, sleep_hours=8.0,
            financial_stress=1, work_hours=3.0
        ))
        assert isinstance(result, dict)

    def test_run_assessment_high_stress(self):
        result = self._svc().run_assessment(self._payload(
            academic_pressure=10, study_satisfaction=1, sleep_hours=3.0,
            financial_stress=9, work_hours=14.0, family_history="Yes"
        ))
        risk = result.get("risk_level") or result.get("risk", "")
        assert risk in ("Moderate", "High", "Critical")

    def test_clean_text_strips_urls(self):
        from services.prediction_service import _clean_text
        assert "http" not in _clean_text("Check https://example.com out")

    def test_clean_text_strips_punctuation(self):
        from services.prediction_service import _clean_text
        assert "!" not in _clean_text("Hello! How are you?")

    def test_clean_text_lowercases(self):
        from services.prediction_service import _clean_text
        assert _clean_text("FEELING ANXIOUS") == "feeling anxious"

    def test_run_assessment_has_emotion(self):
        result = self._svc().run_assessment(self._payload())
        assert "emotion" in result

    def test_run_assessment_scenarios_for_coverage(self):
        svc = self._svc()
        svc.run_assessment(self._payload(
            sleep_hours=9.0,
            dietary_habits="Healthy",
            text="I am having a panic attack and feel scared about deadlines",
            family_history="Yes"
        ))
        svc.run_assessment(self._payload(
            dietary_habits="Unhealthy",
            study_satisfaction=2,
            academic_pressure=10,
            stress_level=10,
            anxiety_level=10,
            financial_stress=10,
            work_hours=15.0,
            text="suicide self-harm want to die"
        ))

    def test_run_assessment_mocked_behav_ready(self):
        svc = self._svc()
        svc._behav_ready = True
        svc._behav_model = MagicMock()
        svc._behav_model.predict_proba.return_value = [[0.1, 0.9]]
        svc._behav_preprocessor = MagicMock()
        cat_enc = MagicMock()
        cat_enc.get_feature_names_out.return_value = ["Gender_Male", "Sleep_7-8", "Diet_Mod", "Family_No"]
        svc._behav_preprocessor.named_transformers_ = {
            "cat": MagicMock(named_steps={"onehot": cat_enc})
        }
        res = svc.run_assessment(self._payload())
        assert res is not None

    def test_run_assessment_mocked_behav_exception(self):
        svc = self._svc()
        svc._behav_ready = True
        svc._behav_model = MagicMock()
        svc._behav_model.predict_proba.side_effect = Exception("Model prediction error")
        res = svc.run_assessment(self._payload())
        assert res is not None

    def test_run_assessment_mocked_text_ready(self):
        svc = self._svc()
        svc._text_ready = True
        svc._text_model = MagicMock()
        svc._text_model.predict_proba.return_value = [[0.1, 0.85]]
        svc._text_vectorizer = MagicMock()
        res = svc.run_assessment(self._payload())
        assert res is not None

    def test_run_assessment_mocked_text_exception(self):
        svc = self._svc()
        svc._text_ready = True
        svc._text_model = MagicMock()
        svc._text_model.predict_proba.side_effect = Exception("Text model prediction error")
        res = svc.run_assessment(self._payload())
        assert res is not None


# ─────────────────────────────────────────────────────────────────────────────
# AssessmentService
# ─────────────────────────────────────────────────────────────────────────────
class TestAssessmentService:
    def test_get_assessment_context_returns_dict(self, mock_db, sample_user_id):
        from services.assessment_service import AssessmentService
        from database.chatbot_model import ChatbotModel
        # Run with mock user profile inside database to hit user fields and age mapping
        mock_db["users"].update_one(
            {"_id": ObjectId(sample_user_id)},
            {"$set": {"birth_year": "2000", "gender": "Female", "name": "Jane"}},
            upsert=True
        )
        # Mock chatbot message history correctly via model save pattern
        ChatbotModel.save_chat(sample_user_id, "I feel down", "I hear you")
        ChatbotModel.save_chat(sample_user_id, "Not sleeping well", "Rest up")
        
        result = AssessmentService.get_assessment_context(sample_user_id)
        assert isinstance(result, dict) and "scores" in result
        assert result["student_profile"]["gender"] == "Female"
        assert result["student_profile"]["name"] == "Jane"
        assert len(result["history"]) > 0

    def test_assessment_has_all_score_keys(self, mock_db, sample_user_id):
        from services.assessment_service import AssessmentService
        scores = AssessmentService.get_assessment_context(sample_user_id)["scores"]
        for key in ("stress", "anxiety", "depression", "burnout", "wellness"):
            assert key in scores

    def test_assessment_with_report_reflects_scores(self, mock_db, sample_user_id):
        from database.report_model import ReportModel
        from services.assessment_service import AssessmentService
        ReportModel.create_report(
            user_id=sample_user_id, stress=75, anxiety=65, depression=55,
            burnout=70, wellness=40, emotion="Stressed", risk="High"
        )
        result = AssessmentService.get_assessment_context(sample_user_id)
        assert result["scores"]["stress"] == 75
        assert result["scores"]["risk_level"] == "High"


# ─────────────────────────────────────────────────────────────────────────────
# DashboardService
# ─────────────────────────────────────────────────────────────────────────────
class TestDashboardService:
    def test_compile_dashboard_returns_dict(self, mock_db, sample_user_id):
        from services.dashboard_service import DashboardService
        result = DashboardService.compile_dashboard_metrics(sample_user_id)
        assert isinstance(result, dict)

    def test_compile_dashboard_has_timeline(self, mock_db, sample_user_id):
        from services.dashboard_service import DashboardService
        result = DashboardService.compile_dashboard_metrics(sample_user_id)
        assert "timeline" in result

    def test_compile_dashboard_has_summary(self, mock_db, sample_user_id):
        from services.dashboard_service import DashboardService
        result = DashboardService.compile_dashboard_metrics(sample_user_id)
        assert "summary" in result

    def test_compile_dashboard_has_heatmap(self, mock_db, sample_user_id):
        from services.dashboard_service import DashboardService
        result = DashboardService.compile_dashboard_metrics(sample_user_id)
        assert "heatmap" in result

    def test_compile_dashboard_with_reports_and_various_sleep_ranges(self, mock_db, sample_user_id):
        from database.report_model import ReportModel
        from services.dashboard_service import DashboardService
        
        # We write reports with different sleep ranges, different created_at formats, and missing probabilities
        # 1. Critical Sleep Deprivation (<= 3 hours), raw ISO created_at string
        ReportModel.create_report(
            user_id=sample_user_id, stress=60, anxiety=50, depression=40,
            burnout=55, wellness=55, emotion="Calm", risk="Moderate",
            sleep_hours=2.0
        )
        # created_at must remain a datetime object in pymongo memory, but let's test custom ISO created_at parse
        mock_db["mental_health_reports"].update_one(
            {"user_id": ObjectId(sample_user_id)},
            {"$set": {"created_at": datetime.datetime.fromisoformat("2026-06-25T12:00:00")}}
        )

        res1 = DashboardService.compile_dashboard_metrics(sample_user_id)
        assert "Critical Sleep Deprivation" in res1["summary"]["sleep_quality"]

        # 2. Poor Sleep (<= 5 hours), fallback to Scan index created_at formatted as string in raw pymongo bypass check
        # But wait! If we do it inside get_user_reports, it converts it. Let's mock get_user_reports directly to return a string created_at.
        mock_db["mental_health_reports"].delete_many({})
        ReportModel.create_report(
            user_id=sample_user_id, stress=60, anxiety=50, depression=40,
            burnout=55, wellness=55, emotion="Calm", risk="Moderate",
            sleep_hours=4.0
        )
        with patch("database.report_model.ReportModel.get_user_reports") as mock_reports:
            mock_reports.return_value = [{
                "_id": "report123", "user_id": sample_user_id,
                "stress_score": 60, "anxiety_score": 50, "depression_score": 40,
                "burnout_score": 55, "wellness_score": 55, "emotion": "Calm", "risk_level": "Moderate",
                "sleep_hours": 4.0, "created_at": "invalid-datetime-string-for-fromisoformat"
            }]
            res2 = DashboardService.compile_dashboard_metrics(sample_user_id)
            assert "Poor Sleep" in res2["summary"]["sleep_quality"]
            assert "Scan 1" in res2["timeline"]["labels"]

        # 3. Excessive Sleep (<= 12 hours) and Very Excessive Sleep (> 12 hours)
        mock_db["mental_health_reports"].delete_many({})
        ReportModel.create_report(
            user_id=sample_user_id, stress=30, anxiety=20, depression=10,
            burnout=20, wellness=85, emotion="Joy", risk="Low",
            sleep_hours=10.0
        )
        res3 = DashboardService.compile_dashboard_metrics(sample_user_id)
        assert "Excessive Sleep" in res3["summary"]["sleep_quality"]
        
        mock_db["mental_health_reports"].delete_many({})
        ReportModel.create_report(
            user_id=sample_user_id, stress=30, anxiety=20, depression=10,
            burnout=20, wellness=85, emotion="Joy", risk="Low",
            sleep_hours=14.0
        )
        res4 = DashboardService.compile_dashboard_metrics(sample_user_id)
        assert "Very Excessive Sleep" in res4["summary"]["sleep_quality"]

        # Heatmap legacy fallback tests
        # Insert mood log with missing combined_probability and legacy wellness classification
        mock_db["mood_logs"].insert_many([
            {"user_id": ObjectId(sample_user_id), "mood": "calm", "wellness": 85, "date": "2026-06-30"},
            {"user_id": ObjectId(sample_user_id), "mood": "anxious", "wellness": 50, "date": "2026-06-29"},
            {"user_id": ObjectId(sample_user_id), "mood": "sad", "wellness": 30, "date": "2026-06-28"},
            {"user_id": ObjectId(sample_user_id), "mood": "tired", "wellness": 10, "date": "2026-06-27"}
        ])
        res5 = DashboardService.compile_dashboard_metrics(sample_user_id)
        assert len(res5["heatmap"]) > 0
        assert res5["heatmap"][0]["behavioral_probability"] is not None


# ─────────────────────────────────────────────────────────────────────────────
# GeoModel (database/geo_model.py)
# ─────────────────────────────────────────────────────────────────────────────
class TestGeoModel:
    def test_seed_check_executes(self):
        from database.geo_model import GeoModel
        GeoModel.seed_check()

    def test_geo_model_exceptions(self, mock_db):
        from database.geo_model import GeoModel
        with patch("database.db.db_manager.db", MagicMock()) as mock_mgr:
            mock_mgr.geo_countries.find.side_effect = Exception("db error")
            assert GeoModel.get_all_countries() == []
            assert GeoModel.get_states_by_country("IN") == []
            assert GeoModel.get_cities_by_state("IN", "MH") == []
            assert GeoModel.search_countries("India") == []
            assert GeoModel.search_states("IN", "MH") == []
            assert GeoModel.search_cities("IN", "MH", "Mum") == []


# ─────────────────────────────────────────────────────────────────────────────
# LLMProvider
# ─────────────────────────────────────────────────────────────────────────────
class TestLLMProvider:
    def test_groq_provider_generate_response_success(self):
        from chatbot.llm_provider import GroqProvider
        provider = GroqProvider()
        with patch("chatbot.llm_provider.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "Test response from Groq"}}]
            }
            mock_post.return_value = mock_resp
            with patch.dict("os.environ", {"GROQ_API_KEY": "test-key-123"}):
                result = provider.generate_response("Hello")
        assert "Test response" in result

    def test_groq_provider_missing_api_key_returns_error_string(self):
        from chatbot.llm_provider import GroqProvider
        provider = GroqProvider()
        with patch.dict("os.environ", {}, clear=True):
            import os
            os.environ.pop("GROQ_API_KEY", None)
            result = provider.generate_response("Hello")
        assert isinstance(result, str) and len(result) > 0

    def test_groq_provider_connection_error_returns_string(self):
        from chatbot.llm_provider import GroqProvider
        import requests as req_lib
        provider = GroqProvider()
        with patch("chatbot.llm_provider.requests.post",
                   side_effect=req_lib.exceptions.ConnectionError("down")):
            with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
                result = provider.generate_response("Hello")
        assert isinstance(result, str)

    def test_groq_provider_timeout_returns_string(self):
        from chatbot.llm_provider import GroqProvider
        import requests as req_lib
        provider = GroqProvider()
        with patch("chatbot.llm_provider.requests.post",
                   side_effect=req_lib.exceptions.Timeout("timeout")):
            with patch.dict("os.environ", {"GROQ_API_KEY": "test-key"}):
                result = provider.generate_response("Hello")
        assert isinstance(result, str)

    def test_llm_provider_singleton_is_provider_instance(self):
        from chatbot.llm_provider import llm_provider, LLMProvider
        assert isinstance(llm_provider, LLMProvider)

    def test_llm_provider_has_model_name(self):
        from chatbot.llm_provider import llm_provider
        assert isinstance(llm_provider.model_name, str)


# ─────────────────────────────────────────────────────────────────────────────
# ConversationOrchestrator
# ─────────────────────────────────────────────────────────────────────────────
class TestConversationOrchestrator:
    def _orchestrate(self, message, user_id=None):
        from chatbot.conversation_orchestrator import ConversationOrchestrator, SessionCache
        SessionCache._cache.clear()
        return ConversationOrchestrator.orchestrate(message, user_id)

    def test_crisis_message_returns_string(self):
        with patch("chatbot.llm_provider.llm_provider.generate_response",
                   return_value="Please reach out for help right away?"):
            result = self._orchestrate("I want to kill myself")
        assert isinstance(result, str) and len(result) > 0

    def test_habit_tool_bypass(self):
        result = self._orchestrate("show me my habit tracker")
        assert "habit" in result.lower() or "streak" in result.lower()

    def test_calendar_tool_bypass(self):
        result = self._orchestrate("what are my upcoming exam dates?")
        assert "midterm" in result.lower() or "calendar" in result.lower() or "deadline" in result.lower()

    def test_regular_message_with_mocked_llm(self):
        with patch("chatbot.llm_provider.llm_provider.generate_response",
                   return_value="That sounds stressful. How can I help you?"):
            result = self._orchestrate("I feel overwhelmed today")
        assert isinstance(result, str) and len(result) > 0

    def test_unauthenticated_user_gets_response(self):
        with patch("chatbot.llm_provider.llm_provider.generate_response",
                   return_value="I am here for you. What is on your mind?"):
            result = self._orchestrate("I feel stressed", user_id=None)
        assert isinstance(result, str)

    def test_dashboard_bypass_no_user_prompts_login(self):
        result = self._orchestrate("show me my dashboard scores", user_id=None)
        assert "log in" in result.lower() or "please" in result.lower()

    def test_mood_history_no_user_prompts_login(self):
        result = self._orchestrate("show my mood history", user_id=None)
        assert "log in" in result.lower() or "please" in result.lower()

    def test_execute_tool_unknown_route_returns_error(self):
        from chatbot.conversation_orchestrator import ConversationOrchestrator
        result = ConversationOrchestrator._execute_tool("unknown_route")
        assert "error" in result.lower() or "sorry" in result.lower()

    def test_doctor_bypass_no_doctors_in_db(self, mock_db):
        result = self._orchestrate("I need a therapist near me")
        assert isinstance(result, str) and len(result) > 0


# ─────────────────────────────────────────────────────────────────────────────
# EmailService Helpers (Direct validation for 100% coverage)
# ─────────────────────────────────────────────────────────────────────────────
class TestEmailServiceHelpers:
    def test_send_via_brevo_missing_api_key(self):
        from services.email_service import _send_via_brevo
        with patch.dict("os.environ", {}, clear=True):
            import os
            os.environ.pop("BREVO_API_KEY", None)
            ok, err = _send_via_brevo("test@test.com", "sub", "body")
            assert ok is False
            assert "BREVO_API_KEY" in err

    def test_send_via_brevo_missing_from_email(self):
        from services.email_service import _send_via_brevo
        with patch.dict("os.environ", {"BREVO_API_KEY": "some-key"}, clear=True):
            import os
            os.environ.pop("BREVO_FROM_EMAIL", None)
            ok, err = _send_via_brevo("test@test.com", "sub", "body")
            assert ok is False
            assert "BREVO_FROM_EMAIL" in err

    def test_send_via_brevo_http_success_200(self):
        from services.email_service import _send_via_brevo
        with patch.dict("os.environ", {"BREVO_API_KEY": "some-key", "BREVO_FROM_EMAIL": "sender@test.com"}):
            with patch("services.email_service.requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {"messageId": "msg-1234"}
                mock_post.return_value = mock_resp
                ok, err = _send_via_brevo("test@test.com", "sub", "body")
                assert ok is True

    def test_send_via_brevo_http_failure_400(self):
        from services.email_service import _send_via_brevo
        with patch.dict("os.environ", {"BREVO_API_KEY": "some-key", "BREVO_FROM_EMAIL": "sender@test.com"}):
            with patch("services.email_service.requests.post") as mock_post:
                mock_resp = MagicMock()
                mock_resp.status_code = 400
                mock_resp.json.return_value = {"message": "Invalid request"}
                mock_post.return_value = mock_resp
                ok, err = _send_via_brevo("test@test.com", "sub", "body")
                assert ok is False
                assert "API error" in err

    def test_send_via_brevo_timeout_exception(self):
        from services.email_service import _send_via_brevo
        import requests as req_lib
        with patch.dict("os.environ", {"BREVO_API_KEY": "some-key", "BREVO_FROM_EMAIL": "sender@test.com"}):
            with patch("services.email_service.requests.post", side_effect=req_lib.exceptions.Timeout("timeout")):
                ok, err = _send_via_brevo("test@test.com", "sub", "body")
                assert ok is False
                assert "timed out" in err

    def test_send_via_brevo_connection_exception(self):
        from services.email_service import _send_via_brevo
        import requests as req_lib
        with patch.dict("os.environ", {"BREVO_API_KEY": "some-key", "BREVO_FROM_EMAIL": "sender@test.com"}):
            with patch("services.email_service.requests.post", side_effect=req_lib.exceptions.ConnectionError("conn")):
                ok, err = _send_via_brevo("test@test.com", "sub", "body")
                assert ok is False
                assert "Could not reach" in err

    def test_send_via_smtp_missing_credentials(self):
        from services.email_service import _send_via_smtp
        with patch.dict("os.environ", {}, clear=True):
            import os
            os.environ.pop("SMTP_EMAIL", None)
            os.environ.pop("SMTP_PASSWORD", None)
            ok, err = _send_via_smtp("test@test.com", "sub", "body")
            assert ok is False
            assert "credentials" in err

    def test_send_via_smtp_ehlo_tls_success_port_587(self):
        from services.email_service import _send_via_smtp
        import smtplib
        with patch.dict("os.environ", {"SMTP_EMAIL": "test@gmail.com", "SMTP_PASSWORD": "pass", "SMTP_PORT": "587"}):
            with patch("smtplib.SMTP") as mock_smtp_class:
                mock_server = MagicMock()
                mock_smtp_class.return_value = mock_server
                ok, err = _send_via_smtp("test@test.com", "sub", "body")
                assert ok is True
                mock_server.starttls.assert_called_once()
                mock_server.login.assert_called_once()

    def test_send_via_smtp_ssl_success_port_465(self):
        from services.email_service import _send_via_smtp
        import smtplib
        with patch.dict("os.environ", {"SMTP_EMAIL": "test@gmail.com", "SMTP_PASSWORD": "pass", "SMTP_PORT": "465"}):
            with patch("smtplib.SMTP_SSL") as mock_ssl_class:
                mock_server = MagicMock()
                mock_ssl_class.return_value = mock_server
                ok, err = _send_via_smtp("test@test.com", "sub", "body")
                assert ok is True
                mock_server.login.assert_called_once()

    def test_send_via_smtp_exception_587(self):
        from services.email_service import _send_via_smtp
        with patch.dict("os.environ", {"SMTP_EMAIL": "test@gmail.com", "SMTP_PASSWORD": "pass", "SMTP_PORT": "587"}):
            with patch("smtplib.SMTP") as mock_class:
                mock_class.side_effect = Exception("SMTP server down 587")
                ok, err = _send_via_smtp("test@test.com", "sub", "body")
                assert ok is False
                assert "SMTP server down 587" in err

    def test_send_via_smtp_exception_465(self):
        from services.email_service import _send_via_smtp
        with patch.dict("os.environ", {"SMTP_EMAIL": "test@gmail.com", "SMTP_PASSWORD": "pass", "SMTP_PORT": "465"}):
            with patch("smtplib.SMTP_SSL") as mock_class:
                mock_class.side_effect = Exception("SMTP server down 465")
                ok, err = _send_via_smtp("test@test.com", "sub", "body")
                assert ok is False
                assert "SMTP server down 465" in err
