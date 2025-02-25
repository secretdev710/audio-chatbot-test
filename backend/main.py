from fastapi import FastAPI
import socketio
import io
from fastapi.middleware.cors import CORSMiddleware
import requests
import nltk
nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize
import asyncio
import httpx


nltk.download("punkt")  # Download the sentence tokenizer model

app = FastAPI()
sio = socketio.AsyncServer(
    cors_allowed_origins="*",  # Allows all origins
    async_mode="asgi"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change to your frontend URL for security)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

API_KEY = "sk_bc1cb48740139b31b087090ba0645d27087c09ee89b3e260"
VOICE_ID = "cjVigY5qzO86Huf0OWal"

async def fetch_voice(sentence, sid):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"text": sentence}

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print("Voice generated")
            await sio.emit("response_audio", response.content, to=sid)  # Non-blocking emit
        else:
            print("Error:", response.text)
    except Exception as e:
        print("Request failed:", e)

# Handle transcript submission
@sio.on("submit_transcript")
async def handle_transcript(sid, data):
    print(f"Received transcript submission from {sid}: {data}")
    sentences = sent_tokenize(data)
    index = 0
    while index < len(sentences):
      sentence = sentences[index]
      if(index < len(sentences) - 1):
          sentence += sentences[index + 1]
      await fetch_voice(sentence, sid)
      index += 2

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit("message", "Connected to server", to=sid)

@sio.event
async def disconnect(sid):
    global word_index
    global response_index
    word_index = 0
    response_index = 0
    print(f"Client disconnected: {sid}")

@app.get("/")
def read_root():
    return {"message": "Socket.io server running"}

# Run the ASGI app
import uvicorn
if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
