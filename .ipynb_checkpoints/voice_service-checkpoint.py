import os
from dotenv import load_dotenv
from sarvamai import SarvamAI # Import the official SDK client
import io # Used to handle the in-memory audio file

import base64
# Load environment variables to get the API key
load_dotenv()

SARVAM_API_KEY = "d197cdb5-7340-4eea-9210-50667172fb44"

# Initialize the Sarvam AI client once when the module is loaded.
# This is more efficient than creating a new client for every call.
if SARVAM_API_KEY:
    client = SarvamAI(api_subscription_key=SARVAM_API_KEY)
else:
    client = None

def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Sends audio data to the Sarvam AI API using the SDK and returns the transcript.
    """
    if not client:
        return "Error: SARVAM_API_KEY is not set in the environment."
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        print("🎤 Sending audio to Sarvam AI for transcription...")
        response = client.speech_to_text.transcribe(
            file=audio_file,
            model="saarika:v2.5",
            language_code="en-IN"
        )
        transcript = response.transcript
        print(f"✅ Transcription successful: '{transcript}'")
        return transcript
    except Exception as e:
        error_message = f"An exception occurred during transcription: {e}"
        print(f"❌ {error_message}")
        return f"Error: Could not transcribe audio. {e}"

def text_to_speech(text: str) -> bytes | None:
    """
    Sends text to the Sarvam AI API and returns the synthesized speech audio.
    """
    if not client:
        print("Error: Sarvam AI client is not initialized.")
        return None

    try:
        print(f"🔊 Converting text to speech: '{text[:50]}...'")
        
        response = client.text_to_speech.convert(
            text=text,
            target_language_code="en-IN",
            speaker="anushka"
        )
        
        # --- THE DEFINITIVE FIX ---
        # The SDK returns the audio data as a Base64 encoded string.
        # We must decode this string to get the raw audio bytes for Streamlit.
        if response and hasattr(response, 'audios') and response.audios:
            base64_audio_string = response.audios[0]
            audio_bytes = base64.b64decode(base64_audio_string) # Decode from Base64
            
            print("✅ Text-to-speech conversion successful.")
            return audio_bytes
        else:
            print("❌ Text-to-speech response did not contain any audio data.")
            return None
        # --- END DEFINITIVE FIX ---

    except Exception as e:
        print(f"❌ An exception occurred during text-to-speech conversion: {e}")
        return None