# backend_api.py
# Run with: uvicorn backend_api:app --reload

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from agent import RestaurantAgent
from fastapi.responses import JSONResponse
import base64
from voice_service import transcribe_audio, text_to_speech
import re

app = FastAPI()

# Allow CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent (one instance for all requests)
agent = RestaurantAgent()

def strip_markdown(text: str) -> str:
    # Remove bold, italics, and other markdown symbols
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)        # italics
    text = re.sub(r'_([^_]+)_', r'\1', text)            # underline/italics
    text = re.sub(r'`([^`]+)`', r'\1', text)            # inline code
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text) # links
    text = re.sub(r'[#>-]', '', text)                    # headers, blockquotes, lists
    text = re.sub(r'\|', '', text)                      # vertical bars
    text = re.sub(r'\n+', '. ', text)                   # newlines to pauses
    return text.strip()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    user_message = data.get("message")
    print(f"[BACKEND] Received user message: {user_message}")  # Debug print
    if not user_message:
        return {"error": "No message provided."}
    response = agent.run(user_message)
    print(f"[BACKEND] Agent response: {response}")  # Debug print
    return {"response": response}

@app.post("/voice-chat")
async def voice_chat(
    message: str = Form(None),
    audio: UploadFile = File(None)
):
    """
    Accepts either a text message or an audio file. Returns agent's response as text and audio (base64).
    """
    transcript = None
    if audio is not None:
        audio_bytes = await audio.read()
        transcript = transcribe_audio(audio_bytes)
        if transcript.startswith("Error:"):
            return JSONResponse({"error": transcript}, status_code=400)
        user_message = transcript
    elif message is not None:
        user_message = message
    else:
        return JSONResponse({"error": "No message or audio provided."}, status_code=400)

    print(f"[BACKEND] /voice-chat user_message: {user_message}")
    response_text = agent.run(user_message)
    print(f"[BACKEND] /voice-chat agent response: {response_text}")
    tts_input = strip_markdown(response_text)
    response_audio_bytes = text_to_speech(tts_input)
    response_audio_b64 = base64.b64encode(response_audio_bytes).decode('utf-8') if response_audio_bytes else None
    return {
        "response_text": response_text,
        "response_audio_b64": response_audio_b64,
        "transcript": transcript
    } 