"""
wellness_coach.py  --  AIRA Wellness Coach Module
==================================================
Pure utility module with NO Flask dependency and NO database calls.

Transforms AIRA from a reactive advisor into a proactive coaching loop.

Public API:
    from chatbot.wellness_coach import WellnessCoach

    decision = WellnessCoach.classify_intent(message, history, assessment, ctx)
    ctx      = WellnessCoach.build_coaching_context(prev_ctx, decision, message)
    prompt   = WellnessCoach.build_coaching_prompt(message, decision, ctx, assessment)

Intent modes:
    venting          -- student is expressing emotion, not asking for help
    seeking_advice   -- student wants guidance but has not specified a goal
    goal_planning    -- student has identified a concrete task/deadline
    progress_update  -- student is reporting back on a prior coaching turn
    crisis           -- safety-net fallback; routes back to CrisisHandler
"""

from __future__ import annotations
import re
from typing import TypedDict


# ---------------------------------------------------------------------------
# Type definitions
# ---------------------------------------------------------------------------

class CoachingDecision(TypedDict):
    mode:               str
    follow_up_question: str
    coaching_goal:      str
    action_type:        str
    confidence:         float
    reasoning:          str


class CoachingContext(TypedDict):
    active_goal:       str
    mode_history:      list
    turns_in_planning: int
    last_question:     str


# ---------------------------------------------------------------------------
# Signal tables
# ---------------------------------------------------------------------------

_CRISIS_PATTERNS = [
    re.compile(r"\b(kill|end)\s+(my|myself|my life|it all)\b", re.I),
    re.compile(r"\b(want|going)\s+to\s+(die|disappear)\b", re.I),
    re.compile(r"\bdon'?t\s+want\s+to\s+(live|exist|be here)\b", re.I),
    re.compile(r"\bhurt\s+my(self)?\b", re.I),
    re.compile(r"\bsuicid(e|al)\b", re.I),
    re.compile(r"\bno\s+reason\s+to\s+(live|go on)\b", re.I),
]

_VENTING_KEYWORDS = frozenset([
    "i hate", "so fed up", "can't take it", "drives me crazy", "so unfair",
    "nobody cares", "nobody understands", "why does this always", "i'm done",
    "everything is terrible", "life is awful", "why me", "sick of this",
    "i give up", "pointless", "what's the point", "tired of everything",
])
_VENTING_PATTERNS = [
    re.compile(r"\b(ugh|argh|aaah)\b", re.I),
    re.compile(r"i('?m| am) (so |really |extremely )?(frustrated|exhausted|done|finished|over it)\b", re.I),
    re.compile(r"\b(scream|cry|break down)\b", re.I),
]

_ADVICE_KEYWORDS = frozenset([
    "what should i", "how do i", "how can i", "what can i do",
    "i don't know what to do", "i have no idea", "i need help",
    "please help", "can you help", "any advice", "any tips",
    "what do you think", "is there a way", "help me",
    "i'm lost", "i don't know how", "not sure what",
    "give me tips", "tips to", "tips for", "tips on",
    "how to manage", "ways to manage", "how to cope", "how to deal",
    "how to reduce", "suggest some", "techniques to",
])

_PLANNING_KEYWORDS = frozenset([
    "exam on", "test on", "quiz on", "due on", "due friday", "due monday",
    "chapters left", "pages left", "assignments left", "need to finish",
    "i have to", "deadline", "by tomorrow", "by tonight", "before monday",
    "next week", "this week", "study for", "prepare for", "review",
    "how many", "finish before", "complete before", "plan my goals",
    "plan goals", "set goals", "goals for", "goal planning", "plan",
    "planning", "schedule", "routine",
])
_PLANNING_PATTERNS = [
    re.compile(r"\b(physics|chemistry|math|biology|history|english|economics|"
               r"computer science|statistics|calculus|algebra|literature)\b", re.I),
    re.compile(r"\b(chapter(s)?|module(s)?|topic(s)?|unit(s)?|section(s)?)\b", re.I),
    re.compile(r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.I),
    re.compile(r"\b(\d+)\s+(chapters?|pages?|problems?|questions?|topics?)\b", re.I),
    re.compile(r"\b(semester|midterm|final|quiz|assignment|project|lab report)\b", re.I),
]

_PROGRESS_KEYWORDS = frozenset([
    "i did it", "i finished", "i completed", "i managed", "i tried",
    "it went", "i studied", "i couldn't do it", "i failed", "i passed",
    "i got", "update:", "just wanted to say", "i'm done with",
    "actually did", "ended up", "turned out", "i made progress",
])

_GENERAL_KEYWORDS = frozenset([
    "hello", "hi", "hey", "good morning", "good evening", "good afternoon",
    "my name is", "what is", "tell me about", "write an essay", "can you write",
    "explain", "i am happy", "feeling good", "i feel happy", "great day",
    "awesome", "yay", "wonderful", "who is", "how are you", "who are you",
    "what are you", "tell me a joke", "i'm happy", "im happy",
])

_DEFAULT_FOLLOW_UPS = {
    "seeking_advice": [
        "Which part would you like to start with?",
        "How does that approach feel to you?",
        "What would feel like the most helpful next step for you today?",
    ],
    "goal_planning": [
        "How much time do you have before the deadline?",
        "Which part feels most important to tackle first?",
        "If you could tackle just one small piece right now, what would it be?",
    ],
    "progress_update": [
        "That is awesome progress! How are you feeling after getting that done?",
        "How are you feeling right now -- more confident or ready for a break?",
        "What would make the next step feel easiest for you?",
    ],
    "venting": [
        "I'm right here with you. What feels like the heaviest part of it right now?",
        "I'm listening whenever you want to share more. How are you holding up at this moment?",
        "Take a deep breath -- you're not alone in this. What would help you feel a bit lighter today?",
    ],
    "general_chat": [
        "How is the rest of your day going?",
        "What's on your mind today?",
        "Is there anything specific you'd like to explore together?",
    ],
}


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _keyword_hits(text_lower: str, keywords: frozenset) -> int:
    return sum(1 for kw in keywords if kw in text_lower)


def _pattern_hits(text: str, patterns: list) -> int:
    return sum(1 for p in patterns if p.search(text))


def _pick_follow_up(mode: str, coaching_context) -> str:
    options = _DEFAULT_FOLLOW_UPS.get(mode, [])
    if not options:
        return ""
    last = (coaching_context or {}).get("last_question", "")
    for q in options:
        if q != last:
            return q
    return options[0]


def _extract_goal(text: str) -> str:
    """Extract a compact coaching goal string from the student message."""
    subj_pat = re.compile(
        r"\b(physics|chemistry|math|biology|history|english|economics|"
        r"computer science|statistics|calculus|algebra|literature)\b", re.I
    )
    day_pat  = re.compile(
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|"
        r"tomorrow|tonight|this week|next week)\b", re.I
    )
    chap_pat = re.compile(r"\b(\d+)\s+(chapters?|pages?|topics?|questions?)\b", re.I)

    subj  = subj_pat.search(text)
    day   = day_pat.search(text)
    chaps = chap_pat.search(text)

    parts = []
    if subj:  parts.append(f"Prepare {subj.group(0).title()}")
    if chaps: parts.append(f"({chaps.group(0)})")
    if day:   parts.append(f"by {day.group(0).lower()}")
    return " ".join(parts) if parts else text[:80].strip()


# ---------------------------------------------------------------------------
# WellnessCoach
# ---------------------------------------------------------------------------

class WellnessCoach:
    """
    Stateless intent classifier and coaching prompt builder.
    All methods are static -- no instance required.
    """

    @staticmethod
    def classify_intent(
        message:          str,
        history:          list | None = None,
        assessment:       dict | None = None,
        coaching_context: dict | None = None,
    ) -> CoachingDecision:
        """
        Classify the student's message into one of 5 coaching modes.

        Priority order:
            1. Crisis safety-net check      -> "crisis"
            2. Context-aware progress check -> "progress_update"
            3. Planning signal score        -> "goal_planning"
            4. Advice signal score          -> "seeking_advice"
            5. Default                      -> "venting"

        Returns:
            CoachingDecision with all 6 keys populated.
        """
        if not message or not message.strip():
            return CoachingDecision(
                mode="venting", follow_up_question="", coaching_goal="",
                action_type="validate", confidence=0.5,
                reasoning="Empty message -- defaulting to venting"
            )

        text   = message.strip()
        lower  = text.lower()
        ctx    = coaching_context or {}
        scores = assessment or {}

        # 1. Crisis safety-net
        if _pattern_hits(text, _CRISIS_PATTERNS) > 0:
            return CoachingDecision(
                mode="crisis", follow_up_question="", coaching_goal="",
                action_type="validate", confidence=0.95,
                reasoning="Crisis pattern matched -- routing to CrisisHandler"
            )
        risk = str(scores.get("risk_level", "")).lower()
        if risk in ("critical", "high") and any(
            kw in lower for kw in ("die", "hurt", "end", "kill")
        ):
            return CoachingDecision(
                mode="crisis", follow_up_question="", coaching_goal="",
                action_type="validate", confidence=0.90,
                reasoning=f"High-risk assessment + distress keyword"
            )

        # 2. Progress update (context-aware)
        active_goal = ctx.get("active_goal", "")
        if active_goal:
            prog_hits = _keyword_hits(lower, _PROGRESS_KEYWORDS)
            if prog_hits >= 1:
                follow_up = _pick_follow_up("progress_update", ctx)
                return CoachingDecision(
                    mode="progress_update",
                    follow_up_question=follow_up,
                    coaching_goal=active_goal,
                    action_type="reinforce",
                    confidence=min(0.6 + prog_hits * 0.1, 0.95),
                    reasoning=f"Active goal + {prog_hits} progress signal(s)"
                )

        # 3. Score signals
        plan_score = (
            _keyword_hits(lower, _PLANNING_KEYWORDS) * 2
            + _pattern_hits(text, _PLANNING_PATTERNS) * 3
        )
        advice_score = (
            _keyword_hits(lower, _ADVICE_KEYWORDS) * 2
            + (2 if "?" in text else 0)
        )
        vent_score = (
            _keyword_hits(lower, _VENTING_KEYWORDS) * 2
            + _pattern_hits(text, _VENTING_PATTERNS) * 2
        )

        # Boost advice if student sent two messages in a row (escalation)
        if history:
            prior_roles = [h.get("role", "") for h in history[-2:]]
            if "aira" not in prior_roles:
                advice_score += 1

        # Boost planning if high stress detected
        if int(scores.get("stress", 0)) >= 70:
            plan_score += 1

        # Routing with tie-breaking
        if plan_score >= 4 and plan_score >= advice_score + 2:
            follow_up = _pick_follow_up("goal_planning", ctx)
            goal = _extract_goal(text)
            return CoachingDecision(
                mode="goal_planning",
                follow_up_question=follow_up,
                coaching_goal=goal,
                action_type="ask_question",
                confidence=min(0.55 + plan_score * 0.05, 0.95),
                reasoning=f"plan={plan_score}, advice={advice_score}, vent={vent_score}"
            )

        if advice_score >= 2 and advice_score >= vent_score:
            follow_up = _pick_follow_up("seeking_advice", ctx)
            return CoachingDecision(
                mode="seeking_advice",
                follow_up_question=follow_up,
                coaching_goal="",
                action_type="ask_question",
                confidence=min(0.5 + advice_score * 0.05, 0.95),
                reasoning=f"advice={advice_score}, plan={plan_score}, vent={vent_score}"
            )

        # General / positive chat signals
        gen_hits = _keyword_hits(lower, _GENERAL_KEYWORDS)
        if gen_hits >= 1 and vent_score == 0 and plan_score < 4 and advice_score < 2:
            follow_up = _pick_follow_up("general_chat", ctx)
            return CoachingDecision(
                mode="general_chat",
                follow_up_question=follow_up,
                coaching_goal="",
                action_type="engage",
                confidence=min(0.6 + gen_hits * 0.1, 0.90),
                reasoning=f"General/positive chat signals={gen_hits}"
            )

        # Default: venting
        follow_up = _pick_follow_up("venting", ctx)
        return CoachingDecision(
            mode="venting",
            follow_up_question=follow_up,
            coaching_goal=active_goal,
            action_type="validate",
            confidence=max(0.45, min(0.5 + vent_score * 0.07, 0.90)),
            reasoning=f"Default venting. vent={vent_score}, advice={advice_score}, plan={plan_score}"
        )

    # -------------------------------------------------------------------------

    @staticmethod
    def build_coaching_context(
        previous_context: dict | None,
        decision:         CoachingDecision,
        message:          str,
    ) -> CoachingContext:
        """
        Create or update the session coaching context dict.

        Must be persisted per-user (e.g. in ChatbotModel) so the coach
        remembers the active goal across conversation turns.

        Returns:
            Updated CoachingContext TypedDict.
        """
        prev      = previous_context or {}
        mode_hist = list(prev.get("mode_history", []))
        mode_hist.append(decision["mode"])
        mode_hist = mode_hist[-5:]

        active_goal = decision.get("coaching_goal") or prev.get("active_goal", "")

        turns_in_planning = prev.get("turns_in_planning", 0)
        if decision["mode"] == "goal_planning":
            turns_in_planning += 1
        elif decision["mode"] not in ("seeking_advice", "progress_update"):
            turns_in_planning = 0

        return CoachingContext(
            active_goal       = active_goal,
            mode_history      = mode_hist,
            turns_in_planning = turns_in_planning,
            last_question     = decision.get("follow_up_question", ""),
        )

    # -------------------------------------------------------------------------

    @staticmethod
    def build_coaching_prompt(
        message:          str,
        decision:         CoachingDecision,
        coaching_context: dict | None = None,
        assessment:       dict | None = None,
        history:          list | None = None,
        student_profile:  dict | None = None,
    ) -> str:
        """
        Assemble a natural, empathetic coaching-mode LLM prompt.

        Returns:
            A single prompt string ready for OllamaClient.generate_response().
        """
        ctx     = coaching_context or {}
        scores  = assessment or {}
        mode    = decision["mode"]
        fup     = decision.get("follow_up_question", "")
        goal    = ctx.get("active_goal") or decision.get("coaching_goal", "")
        emotion = str(scores.get("emotion", ""))

        parts = []

        # System header
        parts.append(
            "You are AIRA, a warm, supportive, and intelligent AI Student Wellness Companion & Digital Bestie. "
            "Talk like a caring, empathetic, and encouraging student peer and mentor. "
            "Be conversational, natural, and helpful. "
            "If the student asks for advice or tips, provide practical, actionable, easy-to-digest suggestions. "
            "If the student shares happy news, celebrate enthusiastically. "
            "If the student is stressed or venting, validate them warmly without repeating canned robotic phrases. "
            "If the student asks a general question or needs study/academic help, answer helpfully and clearly. "
            "Never diagnose or prescribe medication."
        )

        if student_profile and student_profile.get("name"):
            parts.append(f"Student's Name: {student_profile['name']}")

        if emotion and emotion.lower() not in ("calm", "neutral", ""):
            parts.append(f"Recent assessment report mood: {emotion}.")

        if goal:
            parts.append(f"Active coaching goal: {goal}")

        # Recent conversation history
        if history:
            recent_turns = history[-4:]
            hist_lines = []
            for item in recent_turns:
                r = "Student" if item.get("role") == "student" else "AIRA"
                hist_lines.append(f"{r}: {item.get('message', '').strip()}")
            if hist_lines:
                parts.append("Recent conversation history:\n" + "\n".join(hist_lines))

        mode_instructions = {
            "seeking_advice": (
                "The student is seeking advice or practical tips. Provide clear, empathetic, and actionable guidance, "
                "then invite them to share how that feels."
            ),
            "goal_planning": (
                "The student has a specific task, exam, or deadline. Help them break it down realistically and encourage them."
            ),
            "progress_update": (
                "The student is sharing an update or progress. Celebrate their effort warmly and encourage the next step."
            ),
            "venting": (
                "The student is expressing distress or venting. Validate their feelings with genuine empathy and warmth. "
                "Do NOT repeat robotic phrases like 'That sounds really hard'."
            ),
            "general_chat": (
                "The student is greeting you, sharing happy news, or asking a general question. Respond warmly, engagingly, and helpfully."
            ),
        }
        if mode in mode_instructions:
            parts.append(mode_instructions[mode])

        parts.append(f"Student: {message.strip()}")

        if fup:
            parts.append(f'Suggested follow-up to inspire your response (do not repeat verbatim if context demands otherwise): "{fup}"')

        parts.append("AIRA:")

        return "\n\n".join(parts)
