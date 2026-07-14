from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import db, ChatHistory
from app.services.ai_service import AIService

chatbot_bp = Blueprint('chatbot', __name__)

# Single shared AI service instance (reads GEMINI_API_KEY from env)
ai_service = AIService()


@chatbot_bp.route('/ask-ai')
@login_required
def ask_ai():
    """Renders the main chatbot UI, loading stored conversation history."""
    history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.asc()).all()
    return render_template(
        'ask_ai.html',
        history=history,
        ai_ready=ai_service.is_ready
    )


@chatbot_bp.route('/api/chat', methods=['POST'])
@login_required
def chat():
    """
    JSON API endpoint for the chatbot.
    Accepts: { "message": "user's question" }
    Returns: { "reply": "...", "timestamp": "..." }
    """
    data = request.get_json()
    if not data or not data.get('message', '').strip():
        return jsonify({'error': 'No message provided.'}), 400

    user_message = data['message'].strip()[:2000]  # Limit input length

    # Persist the user's message
    user_entry = ChatHistory(
        user_id=current_user.id,
        message=user_message,
        is_bot=False
    )
    db.session.add(user_entry)
    db.session.commit()

    # Build recent conversation history for multi-turn context (last 10 exchanges)
    recent_history = (
        ChatHistory.query
        .filter_by(user_id=current_user.id)
        .order_by(ChatHistory.timestamp.desc())
        .limit(20)
        .all()
    )
    recent_history.reverse()

    conversation_history = []
    for entry in recent_history:
        role = "model" if entry.is_bot else "user"
        # Skip the very last entry since it's the current message we're about to send
        if entry.id == user_entry.id:
            continue
        conversation_history.append({"role": role, "text": entry.message})

    # Call Gemini
    bot_reply = ai_service.ask_gemini(current_user, user_message, conversation_history)

    # Persist bot response
    bot_entry = ChatHistory(
        user_id=current_user.id,
        message=bot_reply,
        is_bot=True
    )
    db.session.add(bot_entry)
    db.session.commit()

    return jsonify({
        'reply': bot_reply,
        'timestamp': bot_entry.timestamp.strftime('%d %b %Y, %I:%M %p')
    })


@chatbot_bp.route('/api/chat/clear', methods=['POST'])
@login_required
def clear_chat():
    """Clears all conversation history for the current user."""
    ChatHistory.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'status': 'cleared'})
