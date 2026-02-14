from google import genai
import os

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBX62HuLbfNpjuYbDufprU37L-b6J2TXD8")

# Correct Client usage based on new SDK docs
# If the SDK uses `genai.Client`, we use that. 
# Some previews use `from google.genai import Client`
from google.genai import types

client = genai.Client(api_key=GEMINI_API_KEY)

try:
    response = client.models.generate_content(
        model="gemini-3-pro-preview", 
        contents="Hello, this is a test of Gemini text to speech.",
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"]
        )
    )
    
    # Save the audio
    # The response structure for audio might need inspection.
    # Usually it's in response.candidates[0].content.parts[0].inline_data.data
    # But let's check the SDK docs or just print/inspect first.
    
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                import base64
                # It might be bytes already if using the new SDK?
                # Let's write to file
                with open("test_audio.wav", "wb") as f:
                    f.write(part.inline_data.data)
                print("Audio saved to test_audio.wav")
                break
    else:
        print("No audio content in response")
        print(response)

except Exception as e:
    print(f"Error: {e}")
