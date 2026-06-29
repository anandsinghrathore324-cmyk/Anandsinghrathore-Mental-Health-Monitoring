import re
from chatbot.crisis_prompt import CRISIS_SYSTEM_PROMPT
from database.report_model import ReportModel

class CrisisHandler:
    """Utility service to perform multi-signal crisis detection and build emergency prompts."""

    @staticmethod
    def detect_crisis(message: str, user_id: str | None = None) -> dict:
        """
        Evaluates multiple signals to detect self-harm or acute psychological crisis.

        Signals evaluated:
        1. Explicit crisis keywords & regex patterns.
        2. DistilBERT emotion / sentiment analysis from NLP service (if available).
        3. Latest assessment report risk level from database (if available).

        Args:
            message: Raw chat message input from the student.
            user_id: Optional student user ID to pull historical risk levels.

        Returns:
            A dictionary containing:
                "is_crisis" (bool): Whether a crisis was detected.
                "confidence" (float): Confidence score between 0.0 and 1.0.
                "reason" (str): Rationale for the classification.
        """
        msg_clean = message.strip().lower()
        if not msg_clean:
            return {
                "is_crisis": False,
                "confidence": 0.0,
                "reason": "Empty message input."
            }

        # ── 1. Define Regex Patterns ──────────────────────────────────────────
        # Explicit active self-harm or suicidal ideation
        active_ideation_pattern = re.compile(
            r"\b(kill\s+myself|end\s+my\s+life|want\s+to\s+die|hurt\s+myself|harm\s+myself|don't\s+want\s+to\s+live|no\s+reason\s+to\s+live|suicide|self-harm|cutting|overdose)\b"
        )
        # Third-person active threats or concerns
        third_person_pattern = re.compile(
            r"\b(wants\s+to\s+die|wants\s+to\s+kill|harm\s+himself|harm\s+herself|harm\s+themselves|hurt\s+himself|hurt\s+herself)\b"
        )
        # Passive distress / hopelessness indicators
        passive_distress_pattern = re.compile(
            r"\b(pointless|hopeless|can't\s+take\s+this|give\s+up|nothing\s+matters|why\s+bother|want\s+to\s+disappear|better\s+off\s+dead)\b"
        )
        # Informational/speculative bypass cues
        informational_pattern = re.compile(
            r"\b(documentary|movie|book|class|article|news|history|heard\s+about|talking\s+about|researching)\b"
        )

        # ── 2. Gather External Signals ────────────────────────────────────────
        latest_risk = "Low"
        if user_id:
            try:
                reports = ReportModel.get_user_reports(user_id, limit=1)
                if reports:
                    latest_risk = reports[0].get("risk_level", "Low")
            except Exception:
                pass

        nlp_emotion = "Neutral"
        nlp_sentiment = "Neutral"
        try:
            from services.nlp_service import NlpService
            nlp_res = NlpService.analyze_diary_entry(message)
            nlp_emotion = nlp_res.get("emotion", "Neutral")
            nlp_sentiment = nlp_res.get("sentiment", "Neutral")
        except Exception:
            pass

        # ── 3. Run Evaluation Logic ───────────────────────────────────────────
        
        # Check active ideation first
        if active_ideation_pattern.search(msg_clean):
            # Check if this is an informational / documentary reference
            if informational_pattern.search(msg_clean):
                return {
                    "is_crisis": False,
                    "confidence": 0.30,
                    "reason": "Crisis terms detected, but contextual cues suggest informational/non-active reference."
                }
            
            # Active personal crisis
            confidence = 0.95
            if latest_risk in ["High", "Critical"]:
                confidence = 0.99
            return {
                "is_crisis": True,
                "confidence": confidence,
                "reason": "Active self-harm or suicidal ideation indicators identified in the message."
            }

        # Check third-person concern (e.g. friend)
        if third_person_pattern.search(msg_clean):
            if informational_pattern.search(msg_clean):
                return {
                    "is_crisis": False,
                    "confidence": 0.25,
                    "reason": "Third-person crisis terms detected in an informational reference context."
                }
            return {
                "is_crisis": True,
                "confidence": 0.85,
                "reason": "Student is reporting third-person active crisis or self-harm risk."
            }

        # Check passive distress patterns
        if passive_distress_pattern.search(msg_clean):
            # Elevate confidence if user has a history of high/critical risk
            if latest_risk in ["High", "Critical"] or nlp_emotion in ["Sadness", "Fear"] or nlp_sentiment == "Negative":
                return {
                    "is_crisis": True,
                    "confidence": 0.80,
                    "reason": "Passive distress / hopelessness markers detected alongside elevated risk history or negative emotion."
                }
            return {
                "is_crisis": True,
                "confidence": 0.65,
                "reason": "Passive distress or hopelessness indicators detected in message."
            }

        # Catch-all for extreme NLP negative sentiment without keywords
        if nlp_sentiment == "Negative" and nlp_emotion in ["Sadness", "Fear"] and latest_risk in ["High", "Critical"]:
            return {
                "is_crisis": True,
                "confidence": 0.55,
                "reason": "No explicit keywords, but message has highly distressed sentiment combined with high-risk clinical history."
            }

        # Standard non-crisis path
        return {
            "is_crisis": False,
            "confidence": 0.10,
            "reason": "No crisis indicators detected."
        }

    @staticmethod
    def build_crisis_prompt(message: str, user_id: str | None = None) -> str:
        """
        Assembles a dedicated crisis prompt, integrating the raw message
        with CRISIS_SYSTEM_PROMPT.

        Args:
            message: Raw chat message input from the student.
            user_id: Optional student user ID.

        Returns:
            A fully assembled prompt string ready to pass directly to the LLM.
        """
        prompt_blocks = [
            CRISIS_SYSTEM_PROMPT.strip(),
            "=== CURRENT CRISIS INPUT ===",
            f"Student Distress Message: {message.strip()}",
            "============================",
            "AIRA:"
        ]
        return "\n\n".join(prompt_blocks)
