# KrishiSahay AI (कृषिसहाय AI)

KrishiSahay AI is a full-stack web application built to help Indian farmers discover government schemes they are eligible for. The application is designed to be mobile-friendly and lightweight, with an agricultural aesthetic. It includes a rule-based eligibility matching engine and a modular architecture prepared for future integrations with the Gemini API (for voice-to-text transcriptions, land document OCR, and multilingual chat support).

## Features

1. **Farmer Registration & Login**: Collects name, age, mobile number (used as username), state, district, village, land size in hectares, crops grown, and annual income. Securely hashes passwords using PBKDF2/SHA256.
2. **Dashboard**: Shows a summary of the farmer's profile, total number of matching schemes, recent documents scanned, and quick action buttons.
3. **Schemes Directory**: Fully searchable and filterable catalog of government programs, matching by keyword, category, or region.
4. **Rule-Based Eligibility Matcher**: Evaluates constraints including age requirements, land size caps, income limitations, and crop-specific rules to determine eligibility.
5. **AI Document Scan Portal**: Supports uploading images (Aadhaar cards, Patta land records), audio files, and video records, with simulated Gemini Flash processing to parse details.
6. **Smart AI Advisor**: Provides a clean conversational explanation of matches, step-by-step instructions, and official links.
7. **Admin Portal**: Statistics panel listing recent farmer registrations, file uploads, and a form to add new schemes.

## Tech Stack

- **Backend**: Python 3, Flask, Flask-SQLAlchemy (SQLite database), Flask-Login
- **Frontend**: HTML5, CSS3, Bootstrap 5, FontAwesome, JavaScript
- **AI Integration**: Modular interface matching standard Gemini 1.5/2.0 API patterns

---

## Setup Instructions

### 1. Prerequisite: Python 3
Ensure Python 3.9+ is installed on your local computer.

### 2. Create Virtual Environment
Run the following commands in your terminal:
```bash
# Navigate to the project root directory
cd C:\Users\adhav\.gemini\antigravity\scratch\krishisahay_ai

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows Powershell)
.\venv\Scripts\Activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize and Seed the Database
Initialize tables and seed the database with standard agricultural schemes:
```bash
python db_init.py
```
This seeds 5 major Indian farming schemes (PM-KISAN, PMFBY, PMKSY, KCC, Maharashtra Baliraja Jal Sanjivani Yojana) and creates a default test user.

### 5. Start the Application
```bash
python run.py
```
The application will boot in debug mode. Open your browser and navigate to:
- URL: **http://127.0.0.1:5000**
- Admin dashboard: **http://127.0.0.1:5000/admin**

### 6. Default Test Login
To immediately test the farmer dashboard and eligibility features, use these credentials:
- **Mobile Number**: `9876543210`
- **Password**: `password123`

---

## Future Gemini API Integration Design
The file `app/services/ai_service.py` is configured as a standalone wrapper class. To enable real-world Gemini AI features:
1. Obtain a API key from Google AI Studio.
2. Set the environment variable: `set GEMINI_API_KEY=your_key` or `export GEMINI_API_KEY=your_key`
3. Install the google SDK: `pip install google-generativeai`
4. Update `AIService` class methods to instantiate `genai.GenerativeModel('gemini-1.5-flash')` and run `generate_content` for transcriptions and document parsing.
