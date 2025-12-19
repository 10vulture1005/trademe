import os
import google.generativeai as genai
from dotenv import load_dotenv

# Explicitly load .env
load_dotenv(override=True)

api_key = os.getenv("GEMINI_API_KEY")
print(f"Loaded Key (First 5 chars): {api_key[:5] if api_key else 'None'}...")

if not api_key:
    print("ERROR: No API Key found in environment.")
    exit(1)

genai.configure(api_key=api_key)

models_to_test = [
    'gemini-1.5-flash',
    'gemini-2.0-flash-exp',
    'gemini-1.5-pro'
]

print("\n--- Testing Models ---")
for model_name in models_to_test:
    print(f"\nTesting {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'Hello' if you are working.")
        print(f"SUCCESS: {response.text}")
    except Exception as e:
        print(f"FAILED: {e}")
