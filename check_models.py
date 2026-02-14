import google.generativeai as genai
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBX62HuLbfNpjuYbDufprU37L-b6J2TXD8")
genai.configure(api_key=GEMINI_API_KEY)

print("Listing available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
