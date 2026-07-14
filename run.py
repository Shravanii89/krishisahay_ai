from dotenv import load_dotenv
load_dotenv()  # Load GEMINI_API_KEY and other vars from .env before app starts

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
