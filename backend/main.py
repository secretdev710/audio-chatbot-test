from fastapi import FastAPI
import socketio
import asyncio
import numpy as np
import soundfile as sf
import io
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment

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

transcription = "An audio chatbot is a voice-enabled AI that allows users to interact using speech instead of text. It uses speech recognition to convert voice to text, NLP to understand intent, and text-to-speech (TTS) to respond with audio. Popular services include Google Speech-to-Text, Amazon Polly, and OpenAI’s Whisper. These bots are used in virtual assistants, customer support, smart homes, and healthcare. They integrate with APIs for real-time responses and can be built using frameworks like Dialogflow or Rasa. Developers use React Native, Flutter, or web apps for the frontend. The key challenge is ensuring accurate speech recognition across different accents and environments."
words = transcription.split()
word_index = 0

response = "A cross-platform mobile app developer specializes in building applications that run on both iOS and Android using a single codebase. They typically work with frameworks like React Native, Flutter, or Xamarin to create efficient and scalable apps. Their role involves designing user-friendly interfaces, optimizing performance, and integrating APIs for seamless functionality. They ensure compatibility across different devices and operating systems while maintaining a native-like experience. Debugging and testing on multiple platforms are crucial to delivering a smooth user experience. Collaboration with designers and backend developers helps in building feature-rich applications. Their expertise allows businesses to reduce development costs and time while reaching a broader audience."
response_words = response.split()

def split_audio(file_path, chunk_duration=500):
    """Splits an audio file into chunks of 'chunk_duration' milliseconds."""
    audio = AudioSegment.from_mp3(file_path)  # Load the audio file
    chunks = [audio[i:i + chunk_duration] for i in range(0, len(audio), chunk_duration)]
    return chunks  # List of AudioSegment chunks

response_audio_chunks = split_audio("audio.mp3")

# Mock real-time transcription generator
async def mock_transcription(sid):
    global word_index  # Use the global variable
    await sio.emit("transcription", words[word_index], to=sid)
    word_index += 1  # Move to the next word

# Mock response after transcript submission
async def mock_response(sid, response_index):
	asyncio.create_task(sio.emit("response_text", response_words[response_index], to=sid))
	await asyncio.sleep(0.2)
	buffer = io.BytesIO()
	response_audio_chunks[response_index].export(buffer, format="wav")  # Use "mp3" if needed
	audio_bytes = buffer.getvalue()
	asyncio.create_task(sio.emit("response_audio", audio_bytes, to=sid))

# Handle audio chunk from frontend
@sio.on("send_audio_chunk")
async def receive_audio_chunk(sid, data):
    print(f"Received audio chunk from {sid}: {len(data)} bytes")
    await mock_transcription(sid)

# Handle transcript submission
@sio.on("submit_transcript")
async def handle_transcript(sid, data):
    response_index = 0
    print(f"Received transcript submission from {sid}: {data}")
    while response_index < 50:
      await mock_response(sid, response_index)
      response_index += 1
      await asyncio.sleep(0.3)

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
