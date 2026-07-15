from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import db, ChatHistory, CustomScheme
from app.services.ai_service import AIService
from sqlalchemy import or_

chatbot_bp = Blueprint('chatbot', __name__)

# Gemini AI
ai_service = AIService()

# Keyword to scheme mapping
SCHEME_KEYWORDS = {
    "goat": ["Goat"],
    "goat farming": ["Goat"],
    "sheli": ["Goat"],
    "sheli palan": ["Goat"],
    "sheळी": ["Goat"],
    "cow": ["Cow"],
    "dairy": ["Cow"],
    "milk": ["Cow"],
    "gai": ["Cow"],
    "tractor": ["Tractor"],
    "polyhouse": ["Polyhouse"],
    "shednet": ["Shednet"],
    "poultry": ["Poultry"],
    "chicken": ["Poultry"],
    "dal mill": ["Dal"],
    "oil mill": ["Oil"],
    "spirulina": ["Spirulina"],
    "warehouse": ["Warehouse"],
    "cold storage": ["Cold"],
    "vermicompost": ["Vermicompost"],
    "fruit processing": ["Fruit"],
    "agro tourism": ["Tourism"]
}


def format_scheme_response(scheme):
    """Format a scheme object into a markdown response."""
    return f"""# 🌾 {scheme.name}

## 📂 Category
{scheme.category}

## 💰 Project Cost
{scheme.project_cost}

## 🎁 Government Subsidy
{scheme.subsidy}

## 👤 Eligibility
{scheme.eligibility}

## 📝 Description
{scheme.description}

## 📄 Required Documents
{scheme.required_documents or "Please contact your nearest Agriculture Office."}

## 🚀 Application Process
{scheme.application_process or "Apply through the MahaDBT portal."}

## 🌐 Official Website
{scheme.official_link or "https://mahadbt.maharashtra.gov.in"}

---
### 💡 AI Suggestion

Based on your profile, this scheme appears suitable for you.

For faster approval, keep your Aadhaar Card, land records, bank passbook, and mobile number ready before applying.
"""


def find_matching_scheme(user_message):
    """
    Search for a matching scheme based on user message.
    Returns the scheme object or None if not found.
    """
    message_lower = user_message.lower()
    
    # First, try exact scheme name match
    scheme = CustomScheme.query.filter(
        db.func.lower(CustomScheme.name).contains(message_lower)
    ).first()
    
    if scheme:
        return scheme
    
    # Then, try keyword matching
    for keyword, scheme_names in SCHEME_KEYWORDS.items():
        if keyword in message_lower:
            # Find scheme matching any of the scheme names
            scheme = CustomScheme.query.filter(
                CustomScheme.name.in_(scheme_names)
            ).first()
            
            if scheme:
                return scheme
    
    return None


@chatbot_bp.route('/ask-ai')
@login_required
def ask_ai():
    try:
        history = ChatHistory.query.filter_by(
            user_id=current_user.id
        ).order_by(ChatHistory.timestamp.asc()).all()

        return render_template(
            "ask_ai.html",
            history=history,
            ai_ready=ai_service.is_ready
        )
    except Exception as e:
        return jsonify({"error": "Failed to load chat history"}), 500


@chatbot_bp.route("/api/chat", methods=["POST"])
@login_required
def chat():
    try:
        data = request.get_json()

        if not data or not data.get("message"):
            return jsonify({"error": "No message provided"}), 400

        user_message = data["message"].strip()
        
        if not user_message:
            return jsonify({"error": "Empty message"}), 400

        # Save user message
        user_chat = ChatHistory(
            user_id=current_user.id,
            message=user_message,
            is_bot=False
        )
        db.session.add(user_chat)
        db.session.commit()

        # Get previous conversation history (excluding current message)
        history = ChatHistory.query.filter_by(
            user_id=current_user.id
        ).filter(ChatHistory.id != user_chat.id).order_by(
            ChatHistory.timestamp.desc()
        ).limit(20).all()

        history.reverse()

        conversation_history = [
            {
                "role": "model" if msg.is_bot else "user",
                "text": msg.message
            }
            for msg in history
        ]

        # Search for matching scheme
        matching_scheme = find_matching_scheme(user_message)
        
        if matching_scheme:
            bot_reply = format_scheme_response(matching_scheme)
        else:
            # Fall back to Gemini AI
            bot_reply = ai_service.ask_gemini(
                current_user,
                user_message,
                conversation_history
            )
            
            if not bot_reply:
                return jsonify({"error": "Failed to get AI response"}), 500

        # Save bot reply
        bot_chat = ChatHistory(
            user_id=current_user.id,
            message=bot_reply,
            is_bot=True
        )
        db.session.add(bot_chat)
        db.session.commit()

        return jsonify({
            "reply": bot_reply,
            "timestamp": bot_chat.timestamp.strftime("%d %b %Y, %I:%M %p")
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An error occurred while processing your message"}), 500


@chatbot_bp.route("/api/chat/clear", methods=["POST"])
@login_required
def clear_chat():
    try:
        ChatHistory.query.filter_by(
            user_id=current_user.id
        ).delete()
        db.session.commit()

        return jsonify({"status": "cleared"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to clear chat history"}), 500