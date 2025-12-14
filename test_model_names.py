"""Test different Gemini model names to find which ones work."""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# Common Gemini model names to try
model_names = [
    "gemini-pro",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "gemini-2.0-flash-exp",
    "models/gemini-pro",
    "models/gemini-1.5-pro",
    "models/gemini-1.5-flash",
]

print("=" * 80)
print("TESTING GEMINI MODEL NAMES")
print("=" * 80)

for model_name in model_names:
    try:
        print(f"\nTesting: {model_name}... ", end="", flush=True)
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Try a simple test
        result = llm.invoke("Say 'Hello'")
        print(f"✓ WORKS!")
        print(f"  Response: {result.content[:50]}...")

    except Exception as e:
        print(f"✗ FAILED")
        print(f"  Error: {str(e)[:100]}...")

print("\n" + "=" * 80)
