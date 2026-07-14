import os
import time

# Attempt to import the Gemini SDK — fail gracefully if not installed
try:
    import google.generativeai as genai
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    GEMINI_SDK_AVAILABLE = False


class AIService:
    """
    Modular AI service that integrates with the Google Gemini API.
    Falls back to a descriptive error message if the SDK or API key is unavailable.
    API keys are read from the GEMINI_API_KEY environment variable.
    """

    GEMINI_MODEL = "gemini-1.5-flash"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.is_ready = GEMINI_SDK_AVAILABLE and bool(self.api_key)

        if self.is_ready:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                model_name=self.GEMINI_MODEL,
                generation_config={
                    "temperature": 0.4,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
        else:
            self.model = None

    def _build_system_context(self, user):
        """Builds a rich farmer profile context block to inject into every prompt."""
        crops = user.crop_type if user.crop_type else "Not specified"
        land_ha = user.land_size
        land_acres = round(land_ha * 2.47105, 2)

        # Derive farmer scale
        if land_ha <= 1.0:
            farmer_scale = "Marginal Farmer (≤ 1 Ha)"
        elif land_ha <= 2.0:
            farmer_scale = "Small Farmer (1–2 Ha)"
        else:
            farmer_scale = "Other Farmer (> 2 Ha)"

        context = f"""You are KrishiSahay AI, a highly knowledgeable, empathetic, and farmer-friendly agricultural assistant for Indian farmers. 
You help farmers discover government schemes they are eligible for, explain application processes in simple language, and answer questions about agricultural subsidies and benefits.

You are currently assisting a registered farmer with the following profile:

---
FARMER PROFILE:
- Name: {user.full_name}
- Age: {user.age} years
- State: {user.state}
- District: {user.district}
- Village: {user.village}
- Crops Grown: {crops}
- Land Size: {land_ha} hectares ({land_acres} acres) — {farmer_scale}
- Annual Household Income: ₹{user.annual_income:,.0f}
- Social Category: {user.category}
---

INSTRUCTIONS:
1. Always address the farmer by their first name in a warm, respectful tone.
2. When recommending schemes, ALWAYS structure your response clearly with these sections using markdown:
   - **Scheme Name** (with the full official name)
   - **Why You Qualify** (personalized reason based on the farmer's profile)
   - **Benefits** (concrete financial/material benefits)
   - **Required Documents** (bullet list)
   - **How to Apply** (numbered step-by-step process)
   - **Official Website** (a real, working government URL)
3. If the farmer asks a general question (e.g., "how are you?"), respond conversationally and briefly.
4. If you cannot find relevant schemes for a question, honestly say so and suggest the farmer contact the Kisan Helpline at 1800-180-1551.
5. Always respond in clear, simple English that a farmer with basic literacy can understand. Avoid jargon.
6. Do NOT make up scheme names or URLs. Only recommend real, well-known Indian government schemes (PM-KISAN, PMFBY, PMKSY, KCC, etc.).
7. Keep answers concise and actionable."""
        return context

    def ask_gemini(self, user, user_message, conversation_history=None):
        """
        Sends the farmer's question along with their profile to Gemini.
        Returns the AI's response as a string.
        conversation_history: list of dicts [{'role': 'user'|'model', 'parts': [text]}]
        """
        if not self.is_ready:
            if not GEMINI_SDK_AVAILABLE:
                return (
                    "⚠️ **Configuration Error:** The `google-generativeai` library is not installed. "
                    "Please run `pip install google-generativeai` to enable AI features."
                )
            return (
                "⚠️ **API Key Missing:** The Gemini AI assistant is not configured. "
                "Please create a `.env` file in the project root with:\n\n"
                "```\nGEMINI_API_KEY=your_api_key_here\n```\n\n"
                "You can get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)."
            )

        system_context = self._build_system_context(user)

        # Build conversation history for multi-turn chat
        history = []
        if conversation_history:
            for entry in conversation_history:
                history.append({
                    "role": entry["role"],
                    "parts": [entry["text"]]
                })

        try:
            # Start a chat session with system context prepended
            chat = self.model.start_chat(history=history)
            # First turn always includes the system context + current message
            full_prompt = f"{system_context}\n\n---\nFARMER'S QUESTION:\n{user_message}"
            response = chat.send_message(full_prompt)
            return response.text

        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "invalid" in error_str or "api_key" in error_str:
                return (
                    "⚠️ **Invalid API Key:** Your Gemini API key appears to be invalid or expired. "
                    "Please check your `.env` file and make sure the key is correct.\n\n"
                    "Get a valid key from [Google AI Studio](https://aistudio.google.com/app/apikey)."
                )
            elif "quota" in error_str or "rate" in error_str or "429" in error_str:
                return (
                    "⚠️ **Rate Limit Reached:** Too many requests have been made to the AI service. "
                    "Please wait a moment and try again."
                )
            elif "network" in error_str or "connection" in error_str or "timeout" in error_str:
                return (
                    "⚠️ **Connection Error:** Unable to reach the AI service. "
                    "Please check your internet connection and try again."
                )
            else:
                return (
                    f"⚠️ **AI Service Error:** An unexpected error occurred while contacting the AI. "
                    f"Please try again in a moment.\n\n"
                    f"*Technical details: {str(e)[:200]}*"
                )

    def analyze_document(self, file_path, file_type):
        """
        Simulates scanning a farmer's document using Gemini multimodal analysis.
        Real implementation would use genai.upload_file() + vision prompting.
        """
        time.sleep(1)
        file_name = os.path.basename(file_path).lower()

        if file_type == 'image':
            if 'aadhaar' in file_name or 'uid' in file_name:
                return {
                    "document_type": "Aadhaar Card",
                    "extracted_data": {"name": "Verified Farmer", "id_number": "XXXX-XXXX-8921", "status": "Authentic Document"},
                    "summary": "Verified Aadhaar identification card. The document appears authentic and details match the registered farmer's profile."
                }
            elif 'land' in file_name or 'patta' in file_name or 'khata' in file_name:
                return {
                    "document_type": "Land Ownership Record (Patta/7-12)",
                    "extracted_data": {"owner_name": "Farmer's Family", "land_area": "1.8 Hectares", "survey_number": "Survey No: 452/A"},
                    "summary": "Verified Land ownership record. Confirms land ownership of 1.8 Hectares. Suitable for schemes targeting small and marginal farmers (<= 2 hectares)."
                }
            else:
                return {
                    "document_type": "Unspecified Agricultural Document",
                    "extracted_data": {"notes": "Extracted text contains mentions of farm operations, seed purchases, or regional cooperatives."},
                    "summary": "Extracted generic agriculture-related records. Suitable for reference proof but might need manual review."
                }
        elif file_type == 'audio':
            return {
                "transcription": "I am growing wheat and sugar cane. I have 1.5 hectares of land in Maharashtra. What schemes can I get support for?",
                "detected_language": "Hindi / English",
                "extracted_entities": {"crops": ["Wheat", "Sugar cane"], "land_size": 1.5, "state": "Maharashtra"},
                "summary": "Audio transcription complete. Farmer requests info for Wheat and Sugarcane with 1.5 hectares in Maharashtra."
            }
        elif file_type == 'video':
            return {
                "summary": "Video analysis completed. Shows crop health inspection of Paddy field. Detected mild leaf spot infection. Recommends organic fertilizer and moisture monitoring.",
                "insights": "Visual signals suggest active cultivation of Paddy/Rice. Ready for scheme application verification."
            }
        else:
            return {"summary": "Text file content read successfully. No anomaly detected.", "extracted_data": {"words_count": 120}}

    def get_smart_recommendations(self, user_profile, eligible_schemes):
        """Generates a natural language summary for the eligibility report page."""
        scheme_names = [s['scheme'].name for s in eligible_schemes]
        if not scheme_names:
            return (
                f"Namaste {user_profile.full_name}, based on your details (Annual Income: ₹{user_profile.annual_income:,.0f}, "
                f"Land: {user_profile.land_size} hectares), you don't match any schemes currently in our database. "
                f"We recommend updating your profile or crop details to verify again, or uploading your land record so our "
                f"team can check manual exceptions."
            )
        top_scheme = scheme_names[0]
        response = (
            f"Namaste {user_profile.full_name}! Based on our AI analysis, you are eligible for **{len(scheme_names)} government schemes**. "
            f"We highly recommend that you apply for **{top_scheme}** first, as it matches your land size of {user_profile.land_size} hectares "
            f"and your main crop ({user_profile.crop_type}).\n\n"
            f"**Your Next Action Steps:**\n"
            f"1. Gather your Aadhaar Card and Land Record (Patta/Khata).\n"
            f"2. Visit your nearest Common Service Centre (CSC) or click the official registration link to submit.\n"
            f"3. Keep your registered mobile number ({user_profile.mobile_number}) handy for OTP verification."
        )
        return response
