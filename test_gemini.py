import google.generativeai as genai
import os

# Use the key the user provided (hardcoded in the file they edited)
GEMINI_API_KEY = "AIzaSyBX62HuLbfNpjuYbDufprU37L-b6J2TXD8"

try:
    genai.configure(api_key=GEMINI_API_KEY)
    print("Configured Gemini.")
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("Using model: gemini-2.0-flash")
    
    response = model.generate_content("Hello")
    print("Response received:")
    print(response.text)
    
except Exception as e:
    print(f"Error: {e}")
