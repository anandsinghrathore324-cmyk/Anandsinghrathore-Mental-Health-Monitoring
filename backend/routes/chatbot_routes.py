from flask import Blueprint, request, jsonify
from database.chatbot_model import ChatbotModel
from middleware.auth_middleware import token_required
from services.chatbot_service import ChatbotService

chatbot_bp = Blueprint("chatbot", __name__)

@chatbot_bp.route("/chatbot", methods=["POST"])
@token_required
def chatbot(current_user):
    """Endpoint representing Aira AI conversational responses and history retention."""
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    
    if not message:
        return jsonify({
            "status": "error",
            "message": "Missing message input for AI conversationalist."
        }), 400
        
    try:
        # Generate responsive counseling vibes
        response = ChatbotService.generate_response(message)
        
        # Save to database chatbot records
        ChatbotModel.save_chat(
            user_id=current_user["_id"],
            message=message,
            response=response
        )
        
        return jsonify({
            "status": "success",
            "message": "AI reply compiled successfully.",
            "response": response
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Conversational interface failed: {str(e)}"
        }), 500

@chatbot_bp.route("/chat-history", methods=["GET"])
@token_required
def chat_history(current_user):
    """Endpoint returning previous messaging cards for rendering on page load."""
    try:
        history = ChatbotModel.get_chat_history(current_user["_id"])
        return jsonify({
            "status": "success",
            "history": history
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Could not compile conversation history: {str(e)}"
        }), 500
