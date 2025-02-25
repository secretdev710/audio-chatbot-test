import React, { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import RecordRTC from "recordrtc";

import "./App.css";

const socket = io("http://localhost:8000");

function App() {
  const [transcript, setTranscript] = useState("");
  const [responseText, setResponseText] = useState("");
  const audioChunksRef = useRef<Blob[]>([]);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const mediaRecorderRef = useRef<RecordRTC | null>(null);

  useEffect(() => {
    socket.on("connect", () => console.log("Connected to server"));

    socket.on("transcription", (data: string) => {
      setTranscript((prevTranscript) => prevTranscript + " " + data);
    });

    socket.on("response_text", (data: string) => {
      setResponseText((prevResponse) => prevResponse + " " + data);
    });

    socket.on("response_audio", (chunk: ArrayBuffer) => {
      const blob = new Blob([chunk], { type: "audio/webm" });
      const url = URL.createObjectURL(blob); // Create an Object URL

      // Play the audio immediately
      const audio = new Audio(url);
      audio.play();
    });

    return () => {
      socket.off("transcription");
      socket.off("response_text");
      socket.off("audio_chunk");
    };
  }, []);

  const startRecording = async () => {
    console.log("start recording");
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorderRef.current = new RecordRTC(stream, {
      type: "audio",
      mimeType: "audio/webm",
      recorderType: RecordRTC.StereoAudioRecorder,
      timeSlice: 500,
      ondataavailable: (blob: Blob) => {
        blob.arrayBuffer().then((buffer) => {
          socket.emit("send_audio_chunk", buffer);
        });
      },
    });

    mediaRecorderRef.current.startRecording();
  };

  const stopRecording = () => {
    console.log("stop recording");
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stopRecording(() => {
        mediaRecorderRef.current = null;
      });
    }
  };

  const submitTranscript = () => {
    socket.emit("submit_transcript", transcript);
  };

  return (
    <div className="App">
      <h1>Live Transcription System</h1>
      <button onClick={startRecording}>Start Recording</button>
      <button onClick={stopRecording}>Stop Recording</button>
      <h2>Transcript:</h2>
      <p>{transcript}</p>
      <button onClick={submitTranscript}>Submit Transcript</button>
      <h2>Response:</h2>
      <p>{responseText}</p>
    </div>
  );
}

export default App;
