"""Check available Gemini models."""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("=" * 80)
print("AVAILABLE GEMINI MODELS")
print("=" * 80)

# List all available models
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n✓ {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Description: {model.description}")
        print(f"  Supported methods: {', '.join(model.supported_generation_methods)}")

print("\n" + "=" * 80)
