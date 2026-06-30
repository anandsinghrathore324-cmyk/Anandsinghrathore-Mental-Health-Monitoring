import sys
import time
import re
import random
from typing import List, Dict, Optional

class ResponseValidator:
    """Upgraded post-processing stage to sanitize and format raw LLM outputs."""
    
    # Store corrections applied during the most recent validation call
    last_corrections: List[str] = []

    @classmethod
    def validate(cls, raw_response: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        cls.last_corrections = []
        cleaned = raw_response.strip()

        # 1. Reject empty response
        if not cleaned:
            cls.last_corrections.append("empty_fallback")
            return "I'm listening. Please go ahead and share what's on your mind when you're ready."

        # 2. Enforce conversational transitions over dry bullet points/lectures
        lines = cleaned.split("\n")
        formatted_lines = []
        bullet_count = 0
        transitions = ["First, you could ", "Additionally, try to ", "Another option is to ", "Finally, consider "]
        list_detected = False
        
        for line in lines:
            line_strip = line.strip()
            if line_strip.startswith(("-", "*", "•")):
                content = line_strip.lstrip("-*• ").strip()
                if content:
                    content = content[0].lower() + content[1:]
                    transition = transitions[min(bullet_count, len(transitions)-1)]
                    formatted_lines.append(transition + content)
                    bullet_count += 1
                    list_detected = True
            elif re.match(r'^\d+\.\s+', line_strip):
                content = re.sub(r'^\d+\.\s+', '', line_strip).strip()
                if content:
                    content = content[0].lower() + content[1:]
                    transition = transitions[min(bullet_count, len(transitions)-1)]
                    formatted_lines.append(transition + content)
                    bullet_count += 1
                    list_detected = True
            else:
                formatted_lines.append(line)
                
        if list_detected:
            cls.last_corrections.append("list_converted_to_conversational")
        cleaned = "\n".join(formatted_lines)

        # 3. Remove repeated opening phrases
        forbidden = [
            "i'm sorry to hear that", "i'm sorry to hear", "i am sorry to hear",
            "i'm sorry", "i am sorry", "sorry",
            "it sounds like you are", "it sounds like you're", "it sounds like",
            "i understand how you feel", "i understand that", "i understand", "i can understand",
            "it seems like"
        ]
        matched_opening = False
        for prefix in forbidden:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):].lstrip(" ,.;!:-")
                matched_opening = True
                break
        
        if matched_opening:
            cls.last_corrections.append("repetitive_opening_removed")
            openings = [
                "I hear you, and it's completely okay to feel that way.",
                "Thanks for opening up about this.",
                "I'm really glad you shared that with me.",
                "That sounds like a lot to handle, but you're not alone.",
                "I appreciate you sharing this—it takes strength to open up.",
                "That does sound challenging, but we can take it one step at a time.",
                "I'm here for you, and we'll work through this together.",
                "It's completely understandable to feel overwhelmed by that.",
                "Thanks for reaching out. Let's figure this out together.",
                "That sounds really tough, but I'm glad you're talking about it."
            ]
            cleaned = random.choice(openings) + " " + cleaned

        # 4. Remove accidental repeated adjacent sentences
        sentences = re.split(r'(?<=[.!?])\s+', cleaned)
        unique_sentences = []
        repeated_sentence_detected = False
        for s in sentences:
            s_strip = s.strip()
            if not s_strip:
                continue
            norm_s = re.sub(r'[^\w\s]', '', s_strip.lower())
            if unique_sentences:
                norm_last = re.sub(r'[^\w\s]', '', unique_sentences[-1].lower())
                if norm_s == norm_last:
                    repeated_sentence_detected = True
                    continue
            unique_sentences.append(s_strip)
        if repeated_sentence_detected:
            cls.last_corrections.append("repeated_sentences_removed")
        cleaned = " ".join(unique_sentences)

        # 5. Remove duplicated paragraphs
        paragraphs = cleaned.split("\n\n")
        seen_paragraphs = []
        paragraph_dup_detected = False
        for p in paragraphs:
            p_strip = p.strip()
            if p_strip:
                if p_strip.lower() not in [s.lower() for s in seen_paragraphs]:
                    seen_paragraphs.append(p_strip)
                else:
                    paragraph_dup_detected = True
        if paragraph_dup_detected:
            cls.last_corrections.append("duplicated_paragraphs_removed")
        cleaned = "\n\n".join(seen_paragraphs)

        # 6. Clean forbidden conversational endings
        endings = [
            "i hope this helps.", "i hope this helps!", "take care.", 
            "let me know if you need anything.", "let me know if you need anything else."
        ]
        lower_cleaned = cleaned.lower()
        ending_removed_detected = False
        for ending in endings:
            if ending in lower_cleaned:
                idx = lower_cleaned.rfind(ending)
                if idx != -1:
                    cleaned = cleaned[:idx] + cleaned[idx+len(ending):]
                    cleaned = cleaned.strip()
                    ending_removed_detected = True
        if ending_removed_detected:
            cls.last_corrections.append("ending_phrases_removed")

        # 7. Ensure exactly one final question
        parts = cleaned.split('?')
        if len(parts) > 2:
            cls.last_corrections.append("extra_questions_defused")
            cleaned = "?".join(parts[:-1]).replace('?', '.') + "?" + parts[-1]
        elif len(parts) == 1:
            cls.last_corrections.append("question_added")
            cleaned = cleaned.rstrip(".") + "?"
            questions = [
                "What's one tiny thing that might help you feel a bit better right now?",
                "How does that sound to you?",
                "What feels like a realistic first step for you today?",
                "What would make this feel just a little bit more manageable?",
                "Would you like to talk more about what's causing that?",
                "Is there anything specific we could focus on to help ease that stress?",
                "What is one small thing you can do to take care of yourself today?",
                "How are you planning to spend your evening or break today?",
                "What's been helping you get through these tough days?",
                "Do you have a friend or family member you could reach out to today?"
            ]
            cleaned += " " + random.choice(questions)

        # 8. Trim responses exceeding 120 words while preserving the trailing question
        words = cleaned.split()
        if len(words) > 120:
            cls.last_corrections.append("response_trimmed_to_length")
            parts = cleaned.split('?')
            last_question = ""
            if len(parts) > 1:
                last_question = parts[-2].split('.')[-1].strip() + "?"
            
            truncated_body = " ".join(words[:80])
            last_dot = max(truncated_body.rfind('.'), truncated_body.rfind('!'))
            if last_dot != -1:
                truncated_body = truncated_body[:last_dot+1]
            else:
                truncated_body += "..."
                
            if last_question:
                cleaned = truncated_body + " " + last_question
            else:
                cleaned = truncated_body + " How does that sound to you?"

        return cleaned

# Monkeypatch ConversationOrchestrator to use this ResponseValidator
try:
    import chatbot.conversation_orchestrator
    chatbot.conversation_orchestrator.ResponseValidator = ResponseValidator
except Exception:
    pass
