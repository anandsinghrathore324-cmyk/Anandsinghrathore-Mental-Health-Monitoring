import os
import sys
from unittest.mock import patch, MagicMock

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv()

from chatbot.conversation_orchestrator import ConversationOrchestrator
from chatbot.llm_provider import llm_provider

def test_general_conversation():
    print("\n--- Testing General Conversation ---")
    message = "Hello, I am feeling a bit tired today but overall fine."
    
    try:
        reply = ConversationOrchestrator.orchestrate(message, user_id=None)
        print(f"User: {message}")
        print(f"AIRA Reply: {reply}")
        print(f"Active Model: {llm_provider.model_name}")
        assert len(reply) > 0, "Response should not be empty"
        print("[PASS] General Conversation Test Passed!")
    except Exception as e:
        print(f"[FAIL] General Conversation Test Failed: {str(e)}")
        raise e

def test_crisis_conversation():
    print("\n--- Testing Crisis Conversation ---")
    message = "I feel so desperate, I want to end my life."
    
    try:
        reply = ConversationOrchestrator.orchestrate(message, user_id=None)
        print(f"User: {message}")
        print(f"AIRA Reply: {reply}")
        assert len(reply) > 0, "Response should not be empty"
        print("[PASS] Crisis Conversation Test Passed!")
    except Exception as e:
        print(f"[FAIL] Crisis Conversation Test Failed: {str(e)}")
        raise e

@patch("services.doctor_service.DoctorService.get_nearby_specialists")
def test_doctor_bypass(mock_get_specialists):
    print("\n--- Testing Doctor Tool Bypass ---")
    mock_get_specialists.return_value = [
        {
            "doctor_name": "Dr. Verification Specialist",
            "specialization": "Therapist",
            "specialization_type": "stress",
            "distance_km": 1.2,
            "clinic_address": "123 Mock Street, Delhi"
        }
    ]
    
    message = "Can you recommend a doctor near me?"
    try:
        reply = ConversationOrchestrator.orchestrate(message, user_id=None)
        print(f"User: {message}")
        print(f"AIRA Reply: {reply}")
        assert "specialists nearby" in reply.lower() or "verification specialist" in reply.lower(), "Should return doctor recommendation"
        print("[PASS] Doctor Tool Bypass Test Passed!")
    except Exception as e:
        print(f"[FAIL] Doctor Tool Bypass Test Failed: {str(e)}")
        raise e

@patch("services.dashboard_service.DashboardService.compile_dashboard_metrics")
def test_dashboard_bypass(mock_compile_metrics):
    print("\n--- Testing Dashboard Tool Bypass ---")
    mock_compile_metrics.return_value = {
        "stress_path": [42],
        "anxiety_path": [38],
        "depression_path": [25],
        "wellness_path": [78]
    }
    
    message = "show my dashboard scores"
    try:
        reply = ConversationOrchestrator.orchestrate(message, user_id="mock_user_id")
        print(f"User: {message}")
        print(f"AIRA Reply: {reply}")
        assert "dashboard" in reply.lower() or "stress score" in reply.lower(), "Should return dashboard scores"
        print("[PASS] Dashboard Tool Bypass Test Passed!")
    except Exception as e:
        print(f"[FAIL] Dashboard Tool Bypass Test Failed: {str(e)}")
        raise e

@patch("chatbot.memory_manager.MemoryManager.get_recent_memory")
@patch("chatbot.memory_manager.MemoryManager.is_memory_useful")
def test_memory_conversation(mock_is_useful, mock_get_memory):
    print("\n--- Testing Memory Conversation ---")
    mock_get_memory.return_value = ["Student is preparing for a calculus midterm.", "Student has a cat named Whiskers."]
    mock_is_useful.return_value = True
    
    captured_prompt = None
    
    def mock_generate(prompt):
        nonlocal captured_prompt
        captured_prompt = prompt
        return "I will help you with calculus."
        
    try:
        with patch.object(llm_provider, "generate_response", side_effect=mock_generate):
            reply = ConversationOrchestrator.orchestrate("I am really stressed about my calculus test.", user_id="mock_user_id")
            
        print(f"Captured LLM Prompt contains:\n{captured_prompt[:300]}...\n")
        assert captured_prompt is not None, "Prompt should be captured"
        assert "calculus midterm" in captured_prompt or "Whiskers" in captured_prompt, "Memory should be injected into prompt"
        print(f"AIRA Reply: {reply}")
        print("[PASS] Memory Conversation Test Passed!")
    except Exception as e:
        print(f"[FAIL] Memory Conversation Test Failed: {str(e)}")
        raise e

if __name__ == "__main__":
    print(f"Testing with LLM_PROVIDER={os.getenv('LLM_PROVIDER')} and Model={llm_provider.model_name}")
    try:
        test_general_conversation()
        test_crisis_conversation()
        test_doctor_bypass()
        test_dashboard_bypass()
        test_memory_conversation()
        print("\n[SUCCESS] ALL chatbot orchestrator verification checks passed successfully!")
        sys.exit(0)
    except Exception:
        print("\n[FAILURE] Verification checks failed.")
        sys.exit(1)
