import requests
from chatbot.system_prompt import SYSTEM_PROMPT

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

# ---------------------------------------------------------------------------
# Generation options (Phase 2 optimized)
# ---------------------------------------------------------------------------
# num_predict   : caps output at ~160 tokens (~120-160 words at ~1.3 tok/word)
# stop          : halts generation if model tries to continue as student,
#                 preventing runaway loops and wasted compute
# temperature   : 0.7 — warm and empathetic without being chaotic
# top_p         : 0.9 — nucleus sampling for coherent, focused output
# top_k         : 40  — constrains vocabulary for faster token selection
# repeat_penalty: 1.15 — penalizes repetitive phrasing without harming tone
_GENERATION_OPTIONS = {
    "num_predict":    160,
    "stop":           ["\nStudent:", "\nS:", "\n\nStudent", "\n\nS:"],
    "temperature":    0.7,
    "top_p":          0.9,
    "top_k":          40,
    "repeat_penalty": 1.15,
}


def generate_response(prompt: str) -> str:
    """
    Send the assembled prompt to the local Ollama LLM and return AIRA's response.

    If the prompt already begins with SYSTEM_PROMPT (i.e. it was pre-assembled
    by prompt_builder.build_prompt or crisis_handler.build_crisis_prompt), it is
    sent as-is. Otherwise the raw message is wrapped with SYSTEM_PROMPT.

    Generation is optimised for conversational speed:
      - Capped at 160 tokens to target 120-160 word responses.
      - Stop sequences prevent the model from continuing as the student.
      - repeat_penalty reduces repetitive phrasing.
      - top_p / top_k balance quality with token selection speed.

    Args:
        prompt: Either a pre-assembled full prompt string or a raw student message.

    Returns:
        A string response from AIRA, or a friendly fallback if Ollama is
        unavailable or the request fails.
    """
    if prompt.strip().startswith(SYSTEM_PROMPT.strip()):
        full_prompt = prompt.strip()
    else:
        full_prompt = (
            SYSTEM_PROMPT.strip()
            + "\n\nStudent Message: "
            + prompt.strip()
            + "\n\nAIRA:"
        )

    payload = {
        "model":   OLLAMA_MODEL,
        "prompt":  full_prompt,
        "stream":  False,
        "options": _GENERATION_OPTIONS,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "I'm sorry, I didn't get a response. Please try again.")

    except requests.exceptions.ConnectionError:
        return (
            "I'm temporarily unavailable right now. "
            "Please make sure Ollama is running and try again in a moment."
        )

    except requests.exceptions.Timeout:
        return (
            "It's taking longer than usual to respond. "
            "Please try again in a moment - I'm here for you!"
        )

    except requests.exceptions.HTTPError as e:
        return (
            f"I ran into a hiccup on my end (HTTP {e.response.status_code}). "
            "Please try again shortly."
        )

    except Exception:
        return (
            "Something unexpected happened on my end. "
            "Please try again in a moment - I haven't gone anywhere!"
        )
