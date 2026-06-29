from chatbot.ollama_client import generate_response as ollama_generate


class ChatbotService:
    """
    Service layer for AIRA chatbot responses.

    Delegates response generation to the local Ollama LLM via
    chatbot.ollama_client. The SYSTEM_PROMPT is applied inside
    ollama_client.generate_response(), so this layer stays clean.
    """

    @staticmethod
    def generate_response(message: str, user_id: str | None = None) -> str:
        """
        Validate, route through crisis detection if needed, enrich with student diagnostic context,
        and forward to the Ollama LLM.

        Args:
            message: Raw input string from the student.
            user_id: Optional unique user ID for authenticated context.

        Returns:
            A response string from AIRA (the Ollama LLM), or a friendly
            fallback message if the LLM is unavailable.
        """
        # Guard: empty or whitespace-only messages
        cleaned = message.strip()
        if not cleaned:
            return "It looks like your message was empty. Feel free to share what's on your mind — I'm here to listen."

        # ── Crisis Detection Interceptor ──────────────────────────────────────
        from chatbot.crisis_handler import CrisisHandler
        crisis_status = CrisisHandler.detect_crisis(cleaned, user_id)
        if crisis_status["is_crisis"]:
            crisis_prompt = CrisisHandler.build_crisis_prompt(cleaned, user_id)
            return ollama_generate(crisis_prompt)

        # ── Normal Conversation Flow ──────────────────────────────────────────
        if user_id:
            from services.assessment_service import AssessmentService
            from chatbot.prompt_builder import build_prompt

            ctx = AssessmentService.get_assessment_context(user_id)
            prompt = build_prompt(
                user_message=cleaned,
                emotion=ctx["scores"]["emotion"],
                stress=ctx["scores"]["stress"],
                anxiety=ctx["scores"]["anxiety"],
                depression=ctx["scores"]["depression"],
                burnout=ctx["scores"]["burnout"],
                wellness=ctx["scores"]["wellness"],
                risk_level=ctx["scores"]["risk_level"],
                prediction_reliability=ctx["scores"]["prediction_reliability"],
                recommendations=ctx["recommendations"],
                history=ctx["history"],
                student_profile=ctx["student_profile"]
            )
            return ollama_generate(prompt)

        # Delegate to Ollama client (SYSTEM_PROMPT is applied there)
        return ollama_generate(cleaned)
