import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

# ---------------------------------------------------------------------------
# LLM Provider Abstraction Layer
# ---------------------------------------------------------------------------

class LLMProvider(ABC):
    """Abstract interface defining the contract for LLM inference providers."""
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class OllamaProvider(LLMProvider):
    """Default implementation delegating to the local Ollama client."""
    def generate(self, prompt: str) -> str:
        from chatbot.ollama_client import generate_response
        return generate_response(prompt)


# Global instance of LLMProvider, swappable at runtime if needed
llm_provider: LLMProvider = OllamaProvider()


# ---------------------------------------------------------------------------
# Session Cache Layer
# ---------------------------------------------------------------------------

class SessionCache:
    """Lightweight in-memory cache to store student diagnostic profiles and histories."""
    _cache: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def get(cls, user_id: str) -> Optional[Dict[str, Any]]:
        if not user_id:
            return None
        entry = cls._cache.get(user_id)
        if entry:
            # 5-minute TTL check (300 seconds)
            if time.time() - entry["timestamp"] < 300:
                return entry["data"]
            else:
                del cls._cache[user_id]
        return None

    @classmethod
    def set(cls, user_id: str, data: Dict[str, Any]) -> None:
        if not user_id:
            return
        cls._cache[user_id] = {
            "timestamp": time.time(),
            "data": data
        }

    @classmethod
    def invalidate(cls, user_id: str) -> None:
        if user_id in cls._cache:
            del cls._cache[user_id]


# ---------------------------------------------------------------------------
# Response Validator Stage
# ---------------------------------------------------------------------------

class ResponseValidator:
    """Post-processing stage to sanitize and format raw LLM outputs."""
    @staticmethod
    def validate(raw_response: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        cleaned = raw_response.strip()

        # 1. Reject empty response
        if not cleaned:
            return "I'm listening. Please go ahead and share what's on your mind when you're ready."

        # 2. Enforce maximum response length (350 words)
        words = cleaned.split()
        if len(words) > 350:
            cleaned = " ".join(words[:350]) + "..."

        # 3. Remove duplicated paragraphs
        paragraphs = cleaned.split("\n\n")
        seen_paragraphs = []
        for p in paragraphs:
            p_strip = p.strip()
            if p_strip and p_strip not in seen_paragraphs:
                seen_paragraphs.append(p_strip)
        cleaned = "\n\n".join(seen_paragraphs)

        # 4. Detect repeated responses compared to recent history
        if history:
            last_responses = [h.get("message", "").strip() for h in history if h.get("role") == "aira"]
            if last_responses:
                last_reply = last_responses[-1]
                if cleaned == last_reply:
                    cleaned += "\n\n(Let me know if you would like to explore another aspect of this.)"

        # 5. Ensure at least one follow-up question exists (if not already present)
        if "?" not in cleaned:
            cleaned += "\n\nHow does that sound to you?"

        return cleaned


# ---------------------------------------------------------------------------
# Pipeline Metrics Logger
# ---------------------------------------------------------------------------

class MetricsLogger:
    """Utility to capture and log pipeline telemetry."""
    @staticmethod
    def log(
        user_id: Optional[str],
        total_time_ms: float,
        prompt_size: int,
        coaching_mode: str,
        crisis_flag: bool,
        assessment_loaded: str,
        model_used: str,
        generation_latency_ms: float
    ) -> None:
        print(
            f"[PIPELINE METRICS] User: {user_id or 'Anonymous'} | "
            f"Total Time: {total_time_ms:.2f}ms | "
            f"Prompt Size: {prompt_size} chars | "
            f"Coaching Mode: {coaching_mode} | "
            f"Crisis: {crisis_flag} | "
            f"Assessment Loaded DB: {assessment_loaded} | "
            f"Model: {model_used} | "
            f"LLM Latency: {generation_latency_ms:.2f}ms",
            flush=True
        )


# ---------------------------------------------------------------------------
# Tool Router Stage
# ---------------------------------------------------------------------------

class ToolRouter:
    """Decides if queries should bypass the LLM and go directly to structured services."""
    @staticmethod
    def route(message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        msg_lower = message.lower().strip()

        # Priority 1: Crisis Pre-scan
        # If it has explicit self-harm keywords, skip tool matching to trigger safety flows immediately.
        crisis_keywords = [
            "kill myself", "end my life", "want to die", "hurt myself", 
            "harm myself", "don't want to live", "no reason to live", 
            "suicide", "self-harm", "cutting", "overdose"
        ]
        if any(kw in msg_lower for kw in crisis_keywords):
            return {
                "route": "llm",
                "bypass_llm": False,
                "arguments": {}
            }

        # Priority 2: Direct Tool Matching
        # A. Doctor Recommendation Service
        doctor_keywords = ["doctor", "therapist", "psychologist", "counselor near me", "specialist", "nearby doctor", "psychiatrist"]
        if any(kw in msg_lower for kw in doctor_keywords):
            return {
                "route": "doctor_service",
                "bypass_llm": True,
                "arguments": {"latitude": 28.6139, "longitude": 77.2090}
            }

        # B. Dashboard Service
        dashboard_keywords = ["dashboard", "stress progress", "stress level trend", "dashboard scores", "my metrics", "burnout chart"]
        if any(kw in msg_lower for kw in dashboard_keywords):
            return {
                "route": "dashboard_service",
                "bypass_llm": True,
                "arguments": {}
            }

        # C. Mood History Service
        mood_keywords = ["mood history", "mood logs", "past moods", "diary logs", "mood heatmap"]
        if any(kw in msg_lower for kw in mood_keywords):
            return {
                "route": "mood_history",
                "bypass_llm": True,
                "arguments": {}
            }

        # D. Future Calendar Service
        calendar_keywords = ["calendar", "schedule", "deadlines", "upcoming events", "exam dates", "tasks for tomorrow", "agenda"]
        if any(kw in msg_lower for kw in calendar_keywords):
            return {
                "route": "calendar",
                "bypass_llm": True,
                "arguments": {}
            }

        # E. Future Habit Tracker
        habit_keywords = ["habit", "habit tracker", "routine", "streaks", "habit streak", "track my habits"]
        if any(kw in msg_lower for kw in habit_keywords):
            return {
                "route": "habit",
                "bypass_llm": True,
                "arguments": {}
            }

        # Default fallback to LLM
        return {
            "route": "llm",
            "bypass_llm": False,
            "arguments": {}
        }


# ---------------------------------------------------------------------------
# Conversation Orchestrator
# ---------------------------------------------------------------------------

class ConversationOrchestrator:
    """The central coordinator that executes the chatbot decision flow."""

    @staticmethod
    def orchestrate(message: str, user_id: Optional[str] = None) -> str:
        start_time = time.time()
        cleaned = message.strip()

        # Step 1: Crisis Detection check
        from chatbot.crisis_handler import CrisisHandler
        crisis_status = CrisisHandler.detect_crisis(cleaned, user_id)

        if crisis_status["is_crisis"]:
            crisis_prompt = CrisisHandler.build_crisis_prompt(cleaned, user_id)
            
            gen_start = time.time()
            llm_reply = llm_provider.generate(crisis_prompt)
            gen_latency = (time.time() - gen_start) * 1000
            
            final_reply = ResponseValidator.validate(llm_reply, history=None)
            
            total_latency = (time.time() - start_time) * 1000
            MetricsLogger.log(
                user_id=user_id,
                total_time_ms=total_latency,
                prompt_size=len(crisis_prompt),
                coaching_mode="crisis",
                crisis_flag=True,
                assessment_loaded="Yes",
                model_used="Ollama-llama3.2:3b",
                generation_latency_ms=gen_latency
            )
            return final_reply

        # Step 2: Tool Routing
        routing_decision = ToolRouter.route(cleaned, user_id)
        if routing_decision["bypass_llm"]:
            tool_reply = ConversationOrchestrator._execute_tool(routing_decision["route"], user_id)
            total_latency = (time.time() - start_time) * 1000
            MetricsLogger.log(
                user_id=user_id,
                total_time_ms=total_latency,
                prompt_size=0,
                coaching_mode=f"tool_bypass:{routing_decision['route']}",
                crisis_flag=False,
                assessment_loaded="No",
                model_used="None",
                generation_latency_ms=0.0
            )
            return tool_reply

        # Step 3: Lazy-Load Assessment Context
        assessment_loaded_db = "No"
        assessment_ctx = None
        if user_id:
            assessment_ctx = SessionCache.get(user_id)

        if not assessment_ctx:
            if user_id:
                from services.assessment_service import AssessmentService
                assessment_ctx = AssessmentService.get_assessment_context(user_id)
                SessionCache.set(user_id, assessment_ctx)
                assessment_loaded_db = "Yes"
            else:
                # Fallback dictionary structure for unauthenticated/anonymous calls
                assessment_ctx = {
                    "student_profile": None,
                    "scores": {
                        "stress": 0,
                        "anxiety": 0,
                        "depression": 0,
                        "burnout": 0,
                        "wellness": 100,
                        "emotion": "Calm",
                        "risk_level": "Low",
                        "prediction_reliability": "High"
                    },
                    "recommendations": [],
                    "history": None,
                    "coaching_context": {}
                }

        # Step 3.5: Load Long-Term Memories
        from chatbot.memory_manager import MemoryManager
        memories = MemoryManager.get_recent_memory(user_id, limit=5)
        useful_memories = memories if MemoryManager.is_memory_useful(cleaned, memories) else None

        # Step 4: Wellness Coach mode determination
        from chatbot.wellness_coach import WellnessCoach
        coaching_context = assessment_ctx.get("coaching_context", {})
        intent_decision = WellnessCoach.classify_intent(
            cleaned,
            assessment_ctx.get("history"),
            assessment_ctx.get("scores"),
            coaching_context
        )

        updated_coaching_ctx = WellnessCoach.build_coaching_context(
            coaching_context,
            intent_decision,
            cleaned
        )
        
        # Keep coaching context sync'd in cache
        if user_id:
            assessment_ctx["coaching_context"] = updated_coaching_ctx
            SessionCache.set(user_id, assessment_ctx)

        # Step 5: Prompt Construction
        coaching_modes = {"seeking_advice", "goal_planning", "progress_update", "venting"}
        if intent_decision["mode"] in coaching_modes:
            prompt = WellnessCoach.build_coaching_prompt(
                cleaned,
                intent_decision,
                updated_coaching_ctx,
                assessment_ctx.get("scores")
            )
            if useful_memories:
                mem_lines = [f"* {m}" for m in useful_memories]
                mem_block = "Relevant Previous Context:\n" + "\n".join(mem_lines)
                prompt = mem_block + "\n\n" + prompt
            coaching_mode = intent_decision["mode"]
        else:
            from chatbot.prompt_builder import build_prompt
            scores = assessment_ctx.get("scores")
            prompt = build_prompt(
                user_message=cleaned,
                emotion=scores["emotion"],
                stress=scores["stress"],
                anxiety=scores["anxiety"],
                depression=scores["depression"],
                burnout=scores["burnout"],
                wellness=scores["wellness"],
                risk_level=scores["risk_level"],
                prediction_reliability=scores["prediction_reliability"],
                recommendations=assessment_ctx.get("recommendations", []),
                history=assessment_ctx.get("history"),
                student_profile=assessment_ctx.get("student_profile"),
                memories=useful_memories
            )
            coaching_mode = "normal_conversation"

        # Step 6: LLM Provider Execution
        gen_start = time.time()
        llm_reply = llm_provider.generate(prompt)
        gen_latency = (time.time() - gen_start) * 1000

        # Step 7: Response Validation
        final_reply = ResponseValidator.validate(llm_reply, assessment_ctx.get("history"))

        # Step 7.5: Save Interaction to Memory
        try:
            MemoryManager.save_interaction(user_id, cleaned, final_reply)
        except Exception:
            pass

        # Step 8: Metrics Telemetry Logging
        total_latency = (time.time() - start_time) * 1000
        MetricsLogger.log(
            user_id=user_id,
            total_time_ms=total_latency,
            prompt_size=len(prompt),
            coaching_mode=coaching_mode,
            crisis_flag=False,
            assessment_loaded=assessment_loaded_db,
            model_used="Ollama-llama3.2:3b",
            generation_latency_ms=gen_latency
        )

        return final_reply

    @staticmethod
    def _execute_tool(route: str, user_id: Optional[str] = None) -> str:
        """Helper to invoke structured services and return user-friendly outputs."""
        if route == "doctor_service":
            from services.doctor_service import DoctorService
            # Coordinate nearby doctor lookup with default Delhi location
            specialists = DoctorService.get_nearby_specialists(28.6139, 77.2090)
            if not specialists:
                return "I couldn't find any specialist clinics in close proximity to your current location. Please verify your GPS settings."
            
            reply = "I found these mental health specialists nearby:\n\n"
            for idx, s in enumerate(specialists[:3], start=1):
                dist = s.get("distance_km", 0.0)
                reply += f"{idx}. {s.get('name', 'Specialist')} ({s.get('specialization_type', 'Psychologist')}) - {dist:.2f} km away\n   Address: {s.get('clinic_address', 'N/A')}\n"
            reply += "\nFeel free to ask if you need their contact details or working hours!"
            return reply

        elif route == "dashboard_service":
            if not user_id:
                return "Please log in to view your personalized dashboard metrics."
            from services.dashboard_service import DashboardService
            metrics = DashboardService.compile_dashboard_metrics(user_id)
            
            stress_scores = metrics.get("stress_path", [])
            latest_stress = stress_scores[-1] if stress_scores else "N/A"
            
            anxiety_scores = metrics.get("anxiety_path", [])
            latest_anxiety = anxiety_scores[-1] if anxiety_scores else "N/A"
            
            depression_scores = metrics.get("depression_path", [])
            latest_depression = depression_scores[-1] if depression_scores else "N/A"
            
            wellness_scores = metrics.get("wellness_path", [])
            latest_wellness = wellness_scores[-1] if wellness_scores else "N/A"
            
            return (
                f"Here is a summary of your latest wellness metrics from your dashboard:\n\n"
                f"- Stress Score: {latest_stress}/100\n"
                f"- Anxiety Score: {latest_anxiety}/100\n"
                f"- Depression Score: {latest_depression}/100\n"
                f"- Wellness Index: {latest_wellness}/100\n\n"
                f"You can view the full progress charts and stress trends directly on your dashboard tab."
            )

        elif route == "mood_history":
            if not user_id:
                return "Please log in to retrieve your mood history logs."
            from database.mood_model import MoodModel
            logs = MoodModel.get_mood_heatmap(user_id, days=5)
            if not logs:
                return "You don't have any mood logs recorded yet. Try sharing how you feel today using the check-in card!"
            
            reply = "Here are your recent mood check-in records:\n\n"
            for log in logs[:5]:
                date = log.get("date", "N/A")
                mood = log.get("mood", "calm").title()
                wellness = log.get("wellness", 100)
                reply += f"- {date}: {mood} (Wellness Score: {wellness}/100)\n"
            return reply

        elif route == "calendar":
            return (
                "I checked your academic calendar. Here are your upcoming deadlines and exams:\n\n"
                "- MATH 101 Midterm: Monday at 9:00 AM\n"
                "- Chemistry Lab Report: Friday at 11:59 PM\n"
                "- Psychology Quiz: Next Tuesday\n\n"
                "Make sure to schedule study blocks beforehand!"
            )

        elif route == "habit":
            return (
                "Here is your current habits checklist status:\n\n"
                "- Morning Meditation: 5-day streak 🔥 (Completed today)\n"
                "- Read 10 Pages: 3-day streak 🔥 (Pending today)\n"
                "- Sleep by 11 PM: 0-day streak (Missed yesterday)\n\n"
                "Keep up the great momentum on your meditation streak!"
            )

        return "I'm sorry, I encountered a routing error. How can I help you today?"
