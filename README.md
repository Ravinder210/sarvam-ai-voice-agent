

# AI Voice Restaurant Reservation Assistant

A full-stack conversational AI system for restaurant discovery and reservations, supporting both voice and text interaction. Built with Google Gemini (Vertex AI), FastAPI, React, and SarvamAI.

---

## 🛠️ Technical Architecture

The application is decoupled into a backend agent and a modern frontend UI.

- **Backend:** Python (FastAPI)
  - **Conversational AI Model:** Google Gemini 1.5 Flash via Vertex AI SDK
  - **Voice Services:** SarvamAI SDK for Speech-to-Text and Text-to-Speech
  - **Core Logic:** Custom, stateful agent with robust tool-calling loop and prompt engineering
  - **Data:** Pandas DataFrame loaded from a CSV file as the restaurant knowledge base
- **Frontend:** React + TypeScript + Tailwind CSS (Vite)
  - **UI:** Responsive, accessible chat interface with real-time voice and text support
  - **Voice:** Web Audio API for recording, SarvamAI for TTS/STT, auto-play agent responses
  - **Markdown Rendering:** Uses `react-markdown` for structured, readable agent output

---

## ⚙️ Setup and Installation

Follow these steps to run the application locally.

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Google Cloud Project with the Vertex AI API enabled
- An API key from SarvamAI

### 1. Clone the Repository

```sh
git clone <your-repo-url>
cd reservation_agent
```

### 2. Set Up a Virtual Environment

```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Backend Dependencies

Create a `requirements.txt` file with the following content:

```
fastapi
uvicorn
google-cloud-aiplatform
sarvamai
python-dotenv
pandas
requests
```

Then, install the packages:

```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a file named `.env` in the root of the project directory and add your credentials:

```
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
SARVAM_API_KEY="your-sarvam-api-key"
```

### 5. Authenticate with Google Cloud

You must authenticate your local machine to use the Vertex AI API.

```sh
# Install gcloud CLI if you haven't already
gcloud auth application-default login
```

### 6. Start the Backend

```sh
uvicorn backend_api:app --reload
```

### 7. Set Up and Run the Frontend

```sh
cd vibe-dining-agent-web
npm install
npm run dev
```

The application will open in your web browser. You may need to grant the browser permission to use your microphone.

---

## 🧠 Prompt Engineering Approach

The agent's reliability is a direct result of an iterative prompt engineering process designed to address specific LLM failures observed during testing.

- **Zero-Trust Prompting:**  
  The prompt strictly instructs the model:  
  > "You MUST NOT answer any questions from your own internal knowledge. Your knowledge is outdated and unreliable. Every piece of information... MUST come from using a tool."
  This drastically reduced hallucination and forced the model to rely on our tools as the source of truth.

- **Multi-Step Reasoning Guidance:**  
  The model is guided to deconstruct complex user requests into logical steps, e.g.,  
  > "Deconstruct Tasks: Break down user requests into logical steps... If a user provides information that isn't relevant for an initial search (like a specific time), ignore it for the search step and use the extra information later."

- **Pre-emptive Validation:**  
  The prompt includes a critical validation rule:  
  > "Before calling any tool, you MUST validate the user's input. If a parameter is nonsensical... you MUST ask the user for a correction. You are FORBIDDEN from correcting the input yourself."
  This shifted the responsibility of data validation to the LLM's reasoning phase, making the entire system more robust.

- **Structured Output:**  
  The model is instructed to always present restaurant lists as markdown bullet lists or tables for clarity and easy rendering in the UI.

---

## 💬 Example Conversations

### 1. Text Booking Flow

**User:** I want to book a table in Koramangala  
**Agent:** Here are some restaurants in Koramangala:  
- **Asia Kitchen By Mainland China**: Asian, Chinese, Thai, Momos | ₹1500 | ⭐ 4.9  
- **Chianti**: Italian | ₹1500 | ⭐ 4.7  
Which one would you like to book?

**User:** Chianti  
**Agent:** For how many people and at what time?

**User:** 2 people at 8pm  
**Agent:** Please provide the date for your reservation.

**User:** June 20th  
**Agent:** Your reservation for 2 at Chianti on June 20th at 8:00 PM is confirmed!

---

### 2. Voice Booking Flow

- User clicks mic, says: “Book a table for 4 at Barbeque Nation tomorrow at 7pm”
- Agent: “Please provide the exact date for your reservation.”
- User: “June 21st”
- Agent: “Your reservation for 4 at Barbeque Nation on June 21st at 7:00 PM is confirmed!”

---

### 3. Edge Case: Misspelled Restaurant

**User:** I want to book at Barbequ Nation  
**Agent:** Did you mean “Barbeque Nation”? Please confirm.

---

## 📈 Key Features

- Real-time voice and text chat for restaurant search and booking
- Google Gemini (Vertex AI) for robust, context-aware dialogue
- SarvamAI speech-to-text and text-to-speech integration
- Modern, responsive React frontend with markdown rendering
- Fuzzy search and validation over 1,000+ restaurants
- Automated end-to-end voice pipeline with sub-2 second response time
- Secure, cross-origin communication and session management

---

## 🔒 License

Private, was supposed to be shared with atishay@sarvam.ai for review but i was not able to find the account.

---

**For questions or collaboration, contact [ravinderkuhar210@gmail.com]**

---

graph TD
    subgraph "User Interface (Streamlit)"
        A[User] <-->|Text/Voice| B(main.py);
    end

    subgraph "Backend Logic"
        B --> C{RestaurantAgent (agent.py)};
        C <-->|LLM Calls| D[Google Gemini 1.5 Flash];
        C <-->|Voice I/O| E[Sarvam AI API];
        C <-->|Tool Execution| F[Python Tools (tools.py)];
        F <-->|Data Queries| G[Restaurant DB (Pandas)];
    end



## 💬 Example Conversations

Here are two real, unedited conversations with the agent that demonstrate its key capabilities. These examples showcase how the agent handles ambiguity, recovers from failed searches, and maintains conversational context to provide a seamless user experience.

### Journey 1: Disambiguation and Successful Booking

*This conversation shows the agent's ability to handle ambiguity (when a search returns multiple restaurants with the same name) and gather all necessary information for a successful booking.*

> **User (Voice):** *Okay, can you help me find an Asian restaurant?*
>
> **Agent:** Here are some Asian restaurants for your date:
> *   **Flechazo**: Asian, Mediterranean, North Indian, BBQ | ₹1400 | ⭐ 4.9 (Whitefield)
> *   **Asia Kitchen By Mainland China**: Asian, Chinese, Thai, Momos | ₹1500 | ⭐ 4.9 (Koramangala 5th Block)
> *   **House Of Commons**: Continental, Asian, North Indian | ₹1000 | ⭐ 4.8 (Koramangala 5th Block)
> *   **The Globe Grub**: Continental, North Indian, Asian, Italian | ₹1300 | ⭐ 4.8 (Marathahalli)
> *   **House Of Commons**: Continental, Asian, North Indian | ₹1000 | ⭐ 4.7 (HSR)
>
> Do any of these sound good, or would you like to narrow down your search by location or cost?
>
> **User (Voice):** *Okay, I'll prefer the House of Commons.*
>
> **Agent:** There are two "House Of Commons" restaurants: one in Koramangala 5th Block and another in HSR. Which location would you prefer for your date?
>
> **User (Voice):** *The one in HSR.*
>
> **Agent:** Great choice! To make a reservation at House of Commons in HSR, I'll need a few more details: What date and time would you like to make the reservation for? (Please provide a specific date, e.g., "June 20th at 7 PM")
>
> **User (Voice):** *there will be two of us and the date will be 28th and the time will be 8:00 p.m.*
>
> **Agent:** Great, House of Commons in HSR is available for two people at 8:00 PM on the 28th. Before I make the reservation, could you please tell me your name?
>
> **User (Voice):** *My name is Ravinder.*
>
> **Agent:** Wonderful, Ravinder! Your reservation for House of Commons for 2 people at 8:00 PM is confirmed. Is there anything else I can assist you with today?
>
> **User (Voice):** *No thanks.*
>
> **Agent:** You're welcome! Enjoy your date at House of Commons.

---

### Journey 2: Failed Search, Graceful Recovery, and Contextual Memory

*This journey demonstrates how the agent recovers from a failed search by offering valid alternatives, and how it remembers context (party size, time) from earlier in the conversation to make the final booking seamless.*

> **User (Voice):** *I want to book a restaurant for four people at 8:00 p.m. on Saturday at Sky Garden Koramangala.*
>
> **Agent:** I cannot process relative dates like "Saturday". Could you please provide the specific date for your reservation at Sky Garden Koramangala?
>
> **User (Voice):** *I want to reserve for 28th June, Saturday evening, 2025 year...*
>
> **Agent:** I couldn't find a restaurant named 'Sky Garden Koramangala'. We have restaurants in these locations:
> *   BTM
> *   Banashankari
> *   Basavanagudi
> *   ...
> *   Koramangala 5th Block
> *   ...
>
> Would you like to search for a restaurant in one of these areas?
>
> **User (Voice):** *Which restaurants do we have in Koramangala fourth block?*
>
> **Agent:** In Koramangala 4th Block, we have:
> *   **The Terrace at Gilly's Redefined**: Continental, Finger Food, Asian, North Indian | ₹1400 | ⭐ 4.6
>
> **User (Voice):** *Okay, can you please make a booking?*
>
> **Agent:** Certainly! To book a reservation at The Terrace at Gilly's Redefined, I need your name.
>
> **User (Voice):** *Manisha.*
>
> **Agent:** Your reservation for Manisha at The Terrace at Gilly's Redefined for a party of 4 at 8:00 PM is confirmed! Is there anything else I can help you with today?
>
> **User (Voice):** *Thank you.*
>
> **Agent:** You're very welcome! Enjoy your reservation.
