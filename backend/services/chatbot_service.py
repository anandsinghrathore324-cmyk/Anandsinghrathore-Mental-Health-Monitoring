from chatbot.conversation_orchestrator import ConversationOrchestrator


class ChatbotService:
    """
    Service layer for AIRA chatbot responses.

    Delegates processing entirely to the ConversationOrchestrator.
    """

    @staticmethod
    def generate_response(message: str, user_id: str | None = None) -> str:
        """
        Validate and route the query through the ConversationOrchestrator.

        Args:
            message: Raw input string from the student.
            user_id: Optional unique user ID for authenticated context.

        Returns:
            A reply string.
        """
        return ConversationOrchestrator.orchestrate(message, user_id)

