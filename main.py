import os
import subprocess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory to serve generated videos
# Ensure the directory exists
os.makedirs("generated_videos", exist_ok=True)
app.mount("/videos", StaticFiles(directory="generated_videos"), name="videos")

# Configure Gemini
# Ideally, get this from environment variables
GEMINI_API_KEY = "AIzaSyBX62HuLbfNpjuYbDufprU37L-b6J2TXD8"

class VideoRequest(BaseModel):
    prompt: str

import json

def generate_solution(prompt: str) -> dict:
    if not GEMINI_API_KEY:
        return {"solution_steps": "API CONFIG ERROR", "manim_script": "# API Key invalid"}
        
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    system_prompt = '''
    You are an expert Math/Physics tutor and Manim developer.
    Your task is to:
    1. SOLVE the user's problem step-by-step in clear text (in English - for the JSON response).
    2. Write a COMPLETE, RUNNABLE Manim Python script to visualize it WITH DIAGRAMS & ANIMATIONS.
    3. Provide NARRATION text for each step to be converted to audio.

    CRITICAL LANGUAGE REQUIREMENTS - AUTOMATIC LANGUAGE DETECTION:
    - **DETECT the language of the user's input question**
    - **USE THE SAME LANGUAGE for both video and audio**:
      * If input is in Marathi (मराठी) → All on-screen text in Marathi, All narrations in Marathi
      * If input is in Hindi (हिंदी) → All on-screen text in Hindi, All narrations in Hindi
      * If input is in English → All on-screen text in English, All narrations in English
      * If input is in any other language → Use that language for both text and narration
    - **The solution_steps in the JSON response should always be in English** (for technical reference)
    - **Match the input language exactly** - use appropriate script (Devanagari, Latin, etc.)

    IMPORTANT: The system DOES NOT have LaTeX installed.
    You MUST NOT use `MathTex` or `Tex`.
    You MUST use `Text` for all text and equations.
    Do NOT use LaTeX syntax like `\\frac`, `^`, `_`, `\\text{...}` inside `Text`.

    MANIM SCRIPT RULES:
    1. **Visual Design (DIAGRAMS + TEXT)**:
       - **USE DIAGRAMS**: Create visual representations using Circle, Rectangle, Arrow, Dot, Line, etc.
       - **ADD ANIMATIONS**: Use moving objects, transformations, color changes
       - **LAYOUT**: Put titles at top (UP*2.5), diagrams in center, text below
       - **ENGAGING**: Make it visually interesting and educational!

    2. **Safe Area & Text Handling**:
       - **MAX LINE LENGTH**: Limit lines to **40 characters**.
       - **MANUAL WRAPPING**: Insert line breaks manually.
       - **TRIPLE QUOTES**: Use triple quotes (`"""`) for ALL `Text` strings.
       - **FONT SIZES**:
         - Title: 48 (Top of screen, UP*2.5)
         - Body: 28-32 (Below diagrams, DOWN*2)
         - Labels: 24 (On diagrams)

    3. **Presentation Style & AUDIO SYNC (CRITICAL)**:
       - **STEP STRUCTURE**:
         ```python
         self.add_sound("step1")
         # Create all objects
         self.play(Write(title), Create(diagram), run_time=2)
         self.wait(10)  # MUST be at least 8-12 seconds for audio to complete!
         self.play(FadeOut(title), FadeOut(diagram), run_time=1)
         self.wait(1)  # Gap between steps to prevent overlap
         ```
       - **WAIT TIMES ARE CRITICAL**: Each step MUST `self.wait(10)` or more to allow audio to finish
       - **TRANSITIONS**: Add `self.wait(1)` between steps to prevent overlap
       - **AUDIO SYNC**: Include `self.add_sound("stepX")` at start of EACH step

    4. **Animations to Use**:
       - **For objects appearing**: `Create()`, `Write()`, `FadeIn()`, `GrowFromCenter()`
       - **For movement**: `obj.animate.shift()`, `obj.animate.move_to()`
       - **For emphasis**: `obj.animate.scale(1.5)`, `obj.animate.set_color(YELLOW)`
       - **For transformations**: `Transform()`, `ReplacementTransform()`
       - **IMPORTANT**: NEVER use `run_time=0` - minimum is 0.1 seconds. Typical values: 1-3 seconds

    5. **Diagram Examples**:
       - **Forces**: Arrows with labels
       - **Velocities/Acceleration**: Colored vectors
       - **Objects**: Circles, Rectangles with labels
       - **Graphs**: Lines showing relationships
       - **Coordinate systems**: NumberPlane for trajectories

    6. **Aesthetics**:
       - Professional colors: `BLUE_E` (physics), `YELLOW` (math), `RED` (important), `GREEN` (results)
       - Background: `self.camera.background_color = "#0E1117"`
       - Smooth animations: `run_time=1.5` for most animations

    7. **Advanced Features (Optional but Recommended)**:
       - **TracedPath**: For showing trajectories: `path = TracedPath(obj.get_center, stroke_color=YELLOW)`
       - **Updaters**: For continuous animations: `obj.add_updater(lambda m: m.move_to(...))` then `obj.remove_updater(func)`
       - **ValueTracker**: For parameterized animations: `tracker = ValueTracker(0)` then `self.play(tracker.animate.set_value(5))`
       - **Groups**: Organize related objects: `group = VGroup(obj1, obj2)` then `self.play(FadeOut(group))`
       - **Always ensure animations have positive run_time (minimum 0.1, typical 1-3)**
    
    OUTPUT FORMAT:
    You MUST return a valid JSON object with the following structure:
    {
        "solution_steps": "Step 1: ...\\nStep 2: ...",  (Always in English)
        "narrations": {
            "step1": "[In the SAME language as user input]",
            "step2": "[In the SAME language as user input]",
            "step3": "[In the SAME language as user input]"
        },
        "manim_script": "from manim import *\\n\\nclass GenScene(Scene):\\n   def construct(self):\\n       self.camera.background_color = '#0E1117'\\n\\n       # STEP 1\\n       self.add_sound('step1')\\n       title = Text('Given', font_size=48).to_edge(UP)\\n       block = Rectangle(width=2, height=1.5, color=BLUE)\\n       self.play(Write(title), Create(block))\\n       self.wait(10)\\n       self.play(FadeOut(title), FadeOut(block))\\n       self.wait(1)\\n       ..."
    }

    EXAMPLE with proper timing and language matching:

    If user asks in MARATHI: "५ किलो वस्तुमानावर २० न्यूटन बल कार्यरत आहे. प्रवेग शोधा."
    ```python
    self.add_sound("step1")
    title = Text("पायरी १: दिलेली माहिती", font_size=48).move_to(UP*2.5)
    formula = Text("बल = वस्तुमान × प्रवेग", font_size=36)
    # Narration: "चला या समस्येकडे पाहूया..."
    ```

    If user asks in ENGLISH: "A 5kg mass has 20N force applied. Find acceleration."
    ```python
    self.add_sound("step1")
    title = Text("Step 1: Given Data", font_size=48).move_to(UP*2.5)
    formula = Text("Force = Mass × Acceleration", font_size=36)
    # Narration: "Let's look at this problem..."
    ```

    If user asks in HINDI: "५ किलो द्रव्यमान पर २० न्यूटन बल लगाया गया। त्वरण ज्ञात करें।"
    ```python
    self.add_sound("step1")
    title = Text("चरण १: दी गई जानकारी", font_size=48).move_to(UP*2.5)
    formula = Text("बल = द्रव्यमान × त्वरण", font_size=36)
    # Narration: "आइए इस समस्या को देखें..."
    ```

    IMPORTANT: ALWAYS match the language of the user's input question!

    Do NOT include any markdown formatting (like ```json ... ```) in the JSON string values.
    '''
    
    try:
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=system_prompt + "\n\nUser Request: " + prompt
        )
        
        # Safe text extraction
        text = ""
        if hasattr(response, 'text') and response.text:
            text = response.text
        elif response.candidates and response.candidates[0].content.parts:
            text = response.candidates[0].content.parts[0].text
            
        # Strip markdown if present
        text = text.replace("```json", "").replace("```", "").strip()

        result = json.loads(text)
        print(f"DEBUG: Gemini response keys: {result.keys()}")
        print(f"DEBUG: Narrations in response: {result.get('narrations', {}).keys() if result.get('narrations') else 'None'}")

        return result
    except Exception as e:
        print(f"Error generating solution: {e}")
        return {
            "solution_steps": f"Error generating solution: {e}",
            "narrations": {},
            "manim_script": ""
        }


@app.post("/generate")
async def generate_video(request: VideoRequest):
    print(f"Received request for prompt: {request.prompt[:50]}...")
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY environment variable not set")
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY environment variable not set. Please set it using 'export GEMINI_API_KEY=your_key'")

    try:
        # 1. Generate Solution & Code & Narration
        result = generate_solution(request.prompt)
        script_code = result.get("manim_script", "")
        narrations = result.get("narrations", {})
        
        # 1.5 Generate Audio Files using Gemini Speech API
        # Create assets directory for Manim
        assets_dir = "assets"
        os.makedirs(assets_dir, exist_ok=True)

        generated_audio_files = []
        client = genai.Client(api_key=GEMINI_API_KEY)

        print(f"Generating audio files with Gemini TTS...")
        print(f"Number of narrations: {len(narrations)}")

        for step_key, text in narrations.items():
            print(f"Processing {step_key}: {text[:50]}..." if len(text) > 50 else f"Processing {step_key}: {text}")
            if text and len(text.strip()) > 0:
                try:
                    # Use Gemini TTS model with speech config
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-preview-tts",
                        contents=text,
                        config=types.GenerateContentConfig(
                            response_modalities=["AUDIO"],
                            speech_config=types.SpeechConfig(
                                voice_config=types.VoiceConfig(
                                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                        voice_name="Kore"
                                    )
                                )
                            )
                        )
                    )

                    # Extract audio from response
                    if response.candidates and response.candidates[0].content.parts:
                        for part in response.candidates[0].content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                filename = f"{step_key}.wav"
                                filepath = os.path.join(assets_dir, filename)

                                # Gemini returns PCM audio at 24000 Hz - save as WAV
                                import wave
                                with wave.open(filepath, 'wb') as wav_file:
                                    wav_file.setnchannels(1)  # Mono
                                    wav_file.setsampwidth(2)   # 16-bit
                                    wav_file.setframerate(24000)  # 24kHz
                                    wav_file.writeframes(part.inline_data.data)

                                generated_audio_files.append(filepath)
                                print(f"✓ Generated {filepath}")
                                break
                except Exception as e:
                    print(f"✗ Failed to generate audio for {step_key}: {e}")
                    import traceback
                    traceback.print_exc()

        # 2. Save script to file
        script_filename = "generated_scene.py"
        with open(script_filename, "w") as f:
            f.write(script_code)
            
        # 3. Execute Manim (High Quality - 1080p, 60fps is default for -qh)
        output_filename = "GenScene.mp4"
        cmd = ["manim", "-qh", "--media_dir", ".", "-o", output_filename, script_filename, "GenScene"]
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode != 0:
            print(f"Manim Error Output: {process.stderr}")

            # Cleanup Audio Files even on failure
            for audio_file in generated_audio_files:
                if os.path.exists(audio_file):
                    os.remove(audio_file)
                    print(f"Cleaned up {audio_file}")

            # If execution fails, fallback to just returning the script/solution
            return {
                "status": "partial_success",
                "message": "Script generated but video rendering failed (likely due to missing dependencies).",
                "solution_steps": result.get("solution_steps", ""),
                "manim_script": script_code,
                "error_detail": process.stderr
            }

        print(f"Manim executed successfully. Output file: {output_filename}")
        
        # Locate video file
        output_dir = "generated_videos"
        final_video_path = os.path.join(output_dir, output_filename)
        
        # Manim outputs to ./videos/generated_scene/480p15/GenScene.mp4 with -ql
        # Search for it
        source_path = ""
        # Search in typical Manim output directories
        for search_dir in ["media", "videos"]:
            if not os.path.exists(search_dir):
                continue
            for root, dirs, files in os.walk(search_dir):
                if output_filename in files:
                    source_path = os.path.join(root, output_filename)
                    break
            if source_path:
                break
        
        # Also check current dir if --media_dir . put it there directly (unlikely with manim structure but possible)
        if not source_path and os.path.exists(output_filename):
             source_path = output_filename

        if source_path:
            import shutil
            shutil.move(source_path, final_video_path)
            # Cleanup media/videos folders (optional, but good for cleanliness)
            # Be careful not to delete if we are in the loop
            try:
                shutil.rmtree("media", ignore_errors=True)
                shutil.rmtree("videos", ignore_errors=True)
            except:
                pass
        else:
             print("Could not locate video file after successful execution.")

        # Cleanup Audio Files after video is generated
        for audio_file in generated_audio_files:
            if os.path.exists(audio_file):
                os.remove(audio_file)
                print(f"Cleaned up {audio_file}")

        return {
            "status": "success",
            "message": "Video generated successfully",
            "solution_steps": result.get("solution_steps", ""),
            "manim_script": script_code,
            "video_url": f"http://localhost:8000/videos/{output_filename}"
        }

    except Exception as e:
        print(f"General Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
