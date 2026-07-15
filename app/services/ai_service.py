import os
import time

from app.models import CustomScheme

try:
    import google.generativeai as genai
    GEMINI_SDK_AVAILABLE = True
except ImportError:
    GEMINI_SDK_AVAILABLE = False


class AIService:

    GEMINI_MODEL ="gemini-2.5-flash"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

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
                }
            )
        else:
            self.model = None

    def _build_system_context(self, user):

        crops = user.crop_type if user.crop_type else "Not specified"

        land_ha = user.land_size

        land_acres = round(land_ha * 2.47105, 2)

        if land_ha <= 1:
            farmer_scale = "Marginal Farmer"

        elif land_ha <= 2:
            farmer_scale = "Small Farmer"

        else:
            farmer_scale = "Large Farmer"

        # Read ALL schemes from database
        schemes = CustomScheme.query.all()

        scheme_text = ""

        for s in schemes:
            scheme_text += f"""
Scheme Name : {s.name}

Category : {s.category}

Project Cost : {s.project_cost}

Subsidy : {s.subsidy}

Description : {s.description}

Eligibility : {s.eligibility}

--------------------------------------
"""

        context = f"""
You are KrishiSahay AI.

You are an agricultural expert.

You MUST recommend schemes from the database below whenever applicable.

Never ignore these schemes.

Farmer Profile

Name : {user.full_name}

Age : {user.age}

State : {user.state}

District : {user.district}

Village : {user.village}

Land : {land_ha} hectares ({land_acres} acres)

Farmer Type : {farmer_scale}

Annual Income : ₹{user.annual_income}

Category : {user.category}

Crops : {crops}


=========================
AVAILABLE SCHEMES
=========================

{scheme_text}


Instructions

1. If user asks about schemes, recommend ONLY from the above list.

2. Explain subsidy.

3. Explain project cost.

4. Explain eligibility.

5. Explain benefits.

6. Answer in simple English.

7. If user asks in Marathi, reply in Marathi.

8. Use markdown headings.

9. Address the farmer politely.
"""

        return context

    def ask_gemini(self, user, user_message, conversation_history=None):
        """
        Send a message to Gemini and get AI-powered recommendations.
        """
        
        # Check if service is ready
        if not self.is_ready:
            if not GEMINI_SDK_AVAILABLE:
                return "Gemini SDK is not installed."
            return "Gemini API Key is missing."

        # Build system context
        system_context = self._build_system_context(user)

        # Prepare conversation history
        history = []

        if conversation_history:
            for item in conversation_history:
                history.append({
                    "role": item["role"],
                    "parts": [item["text"]]
                })

        try:
            # Start chat with history
            chat = self.model.start_chat(history=history)

            # Build the prompt
            prompt = f"""
{system_context}

Farmer Question:

{user_message}

Remember:

• Recommend schemes from the database.

• If multiple schemes match, show all.

• Mention subsidy.

• Mention project cost.

• Mention eligibility.

• Mention why the farmer qualifies.

• If user asks about dairy, recommend Dairy Farming scheme.

• If user asks about goat, recommend Goat Farming scheme.

• If user asks about poultry, recommend Poultry Farming scheme.

• If user asks about tractor, recommend Tractor Purchase.

• If user asks about polyhouse, recommend Polyhouse.

• If user asks about warehouse, recommend Warehouse.

• If user asks about cold storage, recommend Cold Storage.

• If user asks about fruit processing, recommend Fruit Processing Unit.

• If no matching scheme exists, say politely that no matching scheme was found.
"""

            # Send message and get response
            response = chat.send_message(prompt)

            # Return the text response
            if response and hasattr(response, 'text'):
                return response.text
            else:
                return "No response received from AI model."

        except Exception as e:
            return f"AI Error: {str(e)}"

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