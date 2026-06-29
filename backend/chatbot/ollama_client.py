import requests
from chatbot.system_prompt import SYSTEM_PROMPT

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"


def generate_response(prompt: str) -> str:
    """
    Send the user message to the local Ollama LLM and return AIRA's response.

    The SYSTEM_PROMPT is prepended to every request to enforce AIRA's
    identity, topic scope, safety rules, and tone guidelines.

    Args:
        prompt: The raw message string sent by the student.

    Returns:
        A string response from the LLM, or a friendly fallback message
        if Ollama is unavailable or the request fails.
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
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,
        "options": {
            "num_predict": 200,
            "temperature": 0.7
        }
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
            "Please try again in a moment — I'm here for you!"
        )

    except requests.exceptions.HTTPError as e:
        return (
            f"I ran into a hiccup on my end (HTTP {e.response.status_code}). "
            "Please try again shortly."
        )

    except Exception:
        return (
            "Something unexpected happened on my end. "
            "Please try again in a moment — I haven't gone anywhere!"
        )
