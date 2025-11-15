from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from routes import agent, token, events, groq_llm, summary, guest_invitations

# Initialize FastAPI app
app = FastAPI(
    title="Conversational Event Planner",
    description="AI-powered event planning assistant using Agora Conversational AI, Groq LLM, and ElevenLabs TTS",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Conversational Event Planner API",
        "status": "running",
        "version": "1.0.0",
        "features": [
            "AI-powered event planning conversations",
            "Real-time voice interaction",
            "Event management and RSVP tracking",
            "Venue suggestions and budget estimates",
            "Groq LLM integration (OpenAI-compatible)",
            "ElevenLabs TTS for natural speech",
            "ARES ASR for speech recognition"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the web interface
@app.get("/demo")
async def demo():
    return FileResponse('static/index.html')

# Serve the voice demo
@app.get("/voice")
async def voice_demo():
    return FileResponse('static/voice-demo.html')

# Serve the real voice demo
@app.get("/realvoice")
async def real_voice_demo():
    return FileResponse('static/real-voice.html')

# Register routes
app.include_router(agent.router)
app.include_router(token.router)
app.include_router(events.router)
app.include_router(groq_llm.router)
app.include_router(summary.router)
app.include_router(guest_invitations.router)

# Main entry point
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)