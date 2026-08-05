import os
import requests
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Abstract interface defining the contract for LLM inference providers."""
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate response from the LLM based on the prompt."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the name of the model being used."""
        pass





class GroqProvider(LLMProvider):
    """Production implementation delegating to the Groq API."""
    
    def generate_response(self, prompt: str) -> str:
        api_key = (os.getenv("GROQ_API_KEY") or "").strip()
        model = (os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile").strip()
        
        if not api_key:
            return "Groq API key is missing. Please configure GROQ_API_KEY in your environment."

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 160
        }

        try:
            # We use a standard timeout of 30 seconds for production API calls
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return "I'm sorry, I received an empty response from Groq. Please try again."

        except requests.exceptions.ConnectionError:
            return (
                "I'm temporarily unable to reach my thinking engine (Connection Error). "
                "Please verify your network connection and try again."
            )

        except requests.exceptions.Timeout:
            return (
                "It's taking longer than usual to retrieve a response from Groq. "
                "Please try again in a moment!"
            )

        except requests.exceptions.HTTPError as e:
            return (
                f"I ran into an issue communicating with Groq (HTTP {e.response.status_code}). "
                "Please check the API status and try again shortly."
            )

        except Exception as e:
            return f"An unexpected error occurred while compiling my response: {str(e)}"

    @property
    def model_name(self) -> str:
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return f"Groq-{model}"


# Production LLM provider is locked to Groq (Ollama is deprecated and disabled in runtime execution flow)
llm_provider: LLMProvider = GroqProvider()
