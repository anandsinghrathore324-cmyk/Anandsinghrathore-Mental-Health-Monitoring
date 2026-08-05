"""
response_validator.py -- Sanitization and quality validation for chatbot outputs.
=================================================================================
Validates, deduplicates, bounds length, and formats raw LLM responses before
delivering them to the user.
"""

import re
from typing import List, Dict, Optional

TRANSITION_WORDS = [
    "First, you could ",
    "Additionally, try to ",
    "Also, consider ",
    "Finally, remember to "
]

REPEATED_OPENINGS = [
    "i'm sorry to hear that",
    "i am sorry to hear that",
    "sorry to hear that",
]

OPENING_ALTERNATIVES = [
    "I hear you, and it's understandable to feel this way.",
    "Thank you for opening up to me.",
    "I'm glad you shared that with me.",
    "That sounds like a lot to handle.",
    "I appreciate you sharing this.",
]


class ResponseValidator:
    """Post-processing stage to sanitize and format raw LLM outputs."""

    last_corrections: List[str] = []

    @classmethod
    def validate(cls, raw_response: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Sanitize and validate an AIRA chatbot response.
        """
        cls.last_corrections = []
        if not raw_response or not raw_response.strip():
            cls.last_corrections.append("empty_fallback")
            return "I'm listening. Please go ahead and share what's on your mind when you're ready."

        cleaned = raw_response.strip()

        # 1. Enforce maximum response length (350 words)
        words = cleaned.split()
        if len(words) > 350:
            cls.last_corrections.append("response_truncated")
            cleaned = " ".join(words[:350]) + "..."

        # 2. Replace robotic repetitive openings
        for opening in REPEATED_OPENINGS:
            if cleaned.lower().startswith(opening):
                alt = OPENING_ALTERNATIVES[0]
                rest = cleaned[len(opening):].lstrip(",. ")
                if rest:
                    rest = rest[0].upper() + rest[1:] if len(rest) > 1 else rest.upper()
                    cleaned = f"{alt} {rest}"
                else:
                    cleaned = alt
                cls.last_corrections.append("opening_varied")
                break

        # 3. Convert bullet points / numbered lists to conversational flow
        cleaned = cls._convert_lists_to_conversational(cleaned)

        # 4. Remove adjacent duplicate sentences within paragraphs
        cleaned = cls._remove_adjacent_duplicate_sentences(cleaned)

        # 5. Remove duplicated paragraphs
        paragraphs = cleaned.split("\n\n")
        seen_paragraphs = []
        for p in paragraphs:
            p_strip = p.strip()
            if p_strip and p_strip.lower() not in [s.lower() for s in seen_paragraphs]:
                seen_paragraphs.append(p_strip)
        if len(seen_paragraphs) < len(paragraphs):
            cls.last_corrections.append("duplicated_paragraphs_removed")
        cleaned = "\n\n".join(seen_paragraphs)

        # 6. Detect repeated responses compared to recent history
        if history:
            last_responses = [h.get("message", "").strip() for h in history if h.get("role") == "aira"]
            if last_responses:
                last_reply = last_responses[-1]
                if cleaned == last_reply:
                    cls.last_corrections.append("repetition_annotated")
                    cleaned += "\n\n(Let me know if you would like to explore another aspect of this.)"

        # 7. Ensure at least one follow-up question exists
        if "?" not in cleaned:
            cls.last_corrections.append("question_added")
            cleaned += "\n\nHow does that sound to you?"

        return cleaned

    @classmethod
    def _convert_lists_to_conversational(cls, text: str) -> str:
        lines = text.split("\n")
        new_lines = []
        bullet_idx = 0
        converted_any = False
        for line in lines:
            stripped = line.strip()
            bullet_match = re.match(r"^[-*•]\s+(.*)$", stripped)
            number_match = re.match(r"^\d+\.\s+(.*)$", stripped)

            item_text = None
            if bullet_match:
                item_text = bullet_match.group(1).strip()
            elif number_match:
                item_text = number_match.group(1).strip()

            if item_text:
                if len(item_text) > 1 and item_text[0].isupper() and not item_text.startswith("I "):
                    item_text = item_text[0].lower() + item_text[1:]
                prefix = TRANSITION_WORDS[min(bullet_idx, len(TRANSITION_WORDS) - 1)]
                new_lines.append(f"{prefix}{item_text}")
                bullet_idx += 1
                converted_any = True
            else:
                new_lines.append(line)
                bullet_idx = 0

        if converted_any:
            cls.last_corrections.append("lists_converted")
        return "\n".join(new_lines)

    @classmethod
    def _remove_adjacent_duplicate_sentences(cls, text: str) -> str:
        # Process each line / paragraph separately to retain line breaks
        lines = text.split("\n")
        out_lines = []
        for line in lines:
            if not line.strip():
                out_lines.append(line)
                continue
            sentences = re.split(r'(?<=[.!?])\s+', line)
            cleaned_sentences = []
            for s in sentences:
                s_clean = s.strip()
                if not s_clean:
                    continue
                if cleaned_sentences and s_clean.lower() == cleaned_sentences[-1].lower():
                    cls.last_corrections.append("duplicate_sentence_removed")
                    continue
                cleaned_sentences.append(s_clean)
            out_lines.append(" ".join(cleaned_sentences))
        return "\n".join(out_lines)


# Ensure orchestrator uses the canonical validator
try:
    import chatbot.conversation_orchestrator
    chatbot.conversation_orchestrator.ResponseValidator = ResponseValidator
except Exception:
    pass
