import google.generativeai as genai
import os

# Get API key from environment variable (more secure)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ Please set your GEMINI_API_KEY environment variable")
    print("Example: export GEMINI_API_KEY='your-api-key-here'")
else:
    genai.configure(api_key=api_key)
    
    try:
        models = genai.list_models()
        print("✅ Available Gemini Models:")
        for m in models:
            print(f"  - {m.name}")
    except Exception as e:
        print(f"❌ Error connecting to Gemini API: {e}")
