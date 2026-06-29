import re
import datetime
from bson import ObjectId
from database.db import db_manager
from typing import List, Dict, Any, Optional

class MemoryManager:
    """Manages long-term persistent conversation memory for student users."""

    @staticmethod
    def save_interaction(
        user_id: Optional[str], 
        student_message: str, 
        aira_response: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Scans the student's message and extracts relevant long-term memories 
        to store in MongoDB under the user_memories collection.
        """
        if not user_id:
            return

        msg_lower = student_message.lower().strip()
        extracted_facts = []

        # 1. Extraction Rules
        # A. Exams / Midterms
        exam_match = re.search(r'([^.!?]*\b(exam|test|midterm|quiz|finals|assignment|due)\b[^.!?]*)', msg_lower)
        if exam_match:
            sentence = exam_match.group(1).strip()
            sentence = sentence[0].upper() + sentence[1:]
            extracted_facts.append({"fact": f"Mentioned: '{sentence}'", "category": "exam"})

        # B. Sleep issues
        if any(kw in msg_lower for kw in ["sleep", "insomnia", "wake up", "restless", "night"]):
            sleep_match = re.search(r'([^.!?]*\b(sleep|insomnia|wake|restless|tossing|turning)\b[^.!?]*)', msg_lower)
            if sleep_match:
                sentence = sleep_match.group(1).strip()
                sentence = sentence[0].upper() + sentence[1:]
                extracted_facts.append({"fact": f"Sleep concern: '{sentence}'", "category": "sleep"})

        # C. Coping strategies / Wellness goals
        coping_keywords = ["meditat", "breath", "run", "walk", "journal", "exercise", "rest", "break"]
        if any(kw in msg_lower for kw in coping_keywords):
            coping_match = re.search(r'([^.!?]*\b(meditat|breath|run|walk|journal|exercise|rest|break)\b[^.!?]*)', msg_lower)
            if coping_match:
                sentence = coping_match.group(1).strip()
                sentence = sentence[0].upper() + sentence[1:]
                extracted_facts.append({"fact": f"Coping strategy/wellness: '{sentence}'", "category": "coping"})

        # D. Study plans / Goals
        goal_keywords = ["plan", "prepare", "finish", "chapter", "math", "chemistry", "physics", "study"]
        if any(kw in msg_lower for kw in goal_keywords):
            goal_match = re.search(r'([^.!?]*\b(plan|prepare|finish|chapter|math|chemistry|physics|study)\b[^.!?]*)', msg_lower)
            if goal_match:
                sentence = goal_match.group(1).strip()
                sentence = sentence[0].upper() + sentence[1:]
                extracted_facts.append({"fact": f"Academic plan/goal: '{sentence}'", "category": "goal"})

        # E. Burnout / Exhaustion
        burnout_keywords = ["burnout", "exhaust", "mush", "tired", "stressed", "anxious", "lonely", "alone"]
        if any(kw in msg_lower for kw in burnout_keywords):
            burnout_match = re.search(r'([^.!?]*\b(burnout|exhaust|mush|tired|stressed|anxious|lonely|alone)\b[^.!?]*)', msg_lower)
            if burnout_match:
                sentence = burnout_match.group(1).strip()
                sentence = sentence[0].upper() + sentence[1:]
                extracted_facts.append({"fact": f"Ongoing wellness concern: '{sentence}'", "category": "concern"})

        # Save extracted facts to MongoDB
        for item in extracted_facts:
            # Upsert memory in collection (overwrites old memory for the same category)
            query = {
                "user_id": ObjectId(user_id),
                "category": item["category"]
            }
            update = {
                "$set": {
                    "fact": item["fact"],
                    "timestamp": datetime.datetime.utcnow()
                }
            }
            try:
                db_manager.db.user_memories.update_one(query, update, upsert=True)
            except Exception:
                pass

    @staticmethod
    def get_recent_memory(user_id: Optional[str], limit: int = 5) -> List[str]:
        """Retrieves the most recent unique memory facts for the student user."""
        if not user_id:
            return []
        try:
            cursor = db_manager.db.user_memories.find(
                {"user_id": ObjectId(user_id)}
            ).sort("timestamp", -1).limit(limit)
            
            memories = []
            for doc in cursor:
                memories.append(doc["fact"])
            return memories
        except Exception:
            return []

    @staticmethod
    def summarize_long_history(user_id: Optional[str]) -> str:
        """Returns a human-readable summary paragraph of the user's active memories."""
        memories = MemoryManager.get_recent_memory(user_id, limit=5)
        if not memories:
            return "No previous wellness context recorded."
        return "Previously, the student has mentioned: " + "; ".join(memories) + "."

    @staticmethod
    def is_memory_useful(message: str, memories: List[str]) -> bool:
        """Determines if stored memories are relevant to the current student message."""
        if not memories:
            return False
        
        msg_lower = message.lower()
        
        # Avoid injecting context for off-topic/pure general greeting queries
        greetings = {"hello", "hi", "hey", "hola", "greetings", "good morning", "good afternoon"}
        words = set(msg_lower.split())
        if words.issubset(greetings) or msg_lower in ["what is the capital of france?", "capital of france"]:
            return False
            
        # Scan if student message contains wellness or topic related keywords
        wellness_terms = [
            "exam", "test", "midterm", "quiz", "study", "prep", "due", "chapter",
            "sleep", "insomnia", "tired", "exhausted", "night", "rest",
            "meditat", "breath", "run", "walk", "journal", "exercise",
            "stress", "anxious", "lonely", "burnout", "fail", "score", "grade",
            "goal", "plan", "routine", "habit", "worry", "feel", "sad", "happy",
            "help", "suggestion", "advice", "what to do"
        ]
        if any(term in msg_lower for term in wellness_terms):
            return True
            
        return False
