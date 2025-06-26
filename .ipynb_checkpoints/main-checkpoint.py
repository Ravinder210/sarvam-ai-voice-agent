import streamlit as st
from agent import RestaurantAgent
from voice_service import transcribe_audio, text_to_speech
from st_audiorec import st_audiorec

st.set_page_config(page_title="GoodFoods AI Assistant", page_icon="🎙️")

st.title("🎙️ GoodFoods AI Voice Assistant")
st.caption("Your smart guide to finding and booking the perfect table. Try voice or text!")

# --- Session State Initialization ---
if "agent" not in st.session_state:
    st.session_state.agent = RestaurantAgent()
    print("🤖 New agent initialized for the session.")

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant", 
        "content": "Welcome to GoodFoods! I'm here to help you find and book a table. You can talk to me by clicking the microphone below, or type a message."
    }]

# This flag is crucial to prevent the infinite loop bug with the audio recorder.
if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# --- Main Display Loop ---
# This loop is responsible for drawing the entire chat history from the session state.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # If the message has audio, display a standard audio player.
        if "audio" in message and message["audio"]:
            # The autoplay command will now work because we are not interrupting it.
            st.audio(message["audio"], autoplay=True)

# --- VOICE INPUT SECTION ---
st.markdown("### Speak to the Assistant")
audio_bytes = st_audiorec()

# This logic robustly handles the voice input and prevents the infinite loop.
if audio_bytes and audio_bytes != st.session_state.get("last_processed_audio"):
    st.session_state.last_processed_audio = audio_bytes

    with st.spinner("Transcribing your voice..."):
        transcript = transcribe_audio(audio_bytes)
    
    if transcript and "Error:" not in transcript:
        # Add user's transcribed message to history
        st.session_state.messages.append({"role": "user", "content": f"🗣️ *{transcript}*"})
        
        # Get agent's response (both text and speech)
        with st.spinner("Thinking... then speaking..."):
            response_text = st.session_state.agent.run(transcript)
            response_audio = text_to_speech(response_text)
        
        # Add the complete assistant response to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response_text, 
            "audio": response_audio
        })
        
    elif transcript:
        st.error(f"Sorry, I couldn't process the audio. {transcript}")
    
    # st.rerun() # <-- REMOVED to allow autoplay to work.

# --- TEXT INPUT SECTION ---
st.markdown("---")
if prompt := st.chat_input("Or, type your message here..."):
    # Add user's typed message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get agent's text-only response
    with st.spinner("Thinking..."):
        response_text = st.session_state.agent.run(prompt)
    
    # Save the text-only response to history
    st.session_state.messages.append({"role": "assistant", "content": response_text, "audio": None})
    
    # st.rerun() # <-- REMOVED to make the UI behavior consistent.