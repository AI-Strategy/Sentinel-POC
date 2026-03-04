import os
import sys
from google import genai
from dotenv import load_dotenv

load_dotenv()

def test_gemini():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or "your_gemini" in api_key:
        print(f"FAILED: Key is '{api_key}'")
        return

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents="say 'SENTINEL_ACK'"
        )
        print(f"SUCCESS: {response.text.strip()}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_gemini()
