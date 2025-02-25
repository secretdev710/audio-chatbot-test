import React, { useEffect, useRef, useState } from "react";
import { io } from "socket.io-client";
import RecordRTC from "recordrtc";

import "./App.css";

const socket = io("https://bb4d-38-170-181-10.ngrok-free.app");

function isAudioPlaying(audio: HTMLAudioElement) {
  return !audio.paused && !audio.ended && audio.readyState > 2;
}

function App() {
  const [transcript, setTranscript] = useState("");
  const mediaSource = new MediaSource();
  const audio = new Audio();
  audio.src = URL.createObjectURL(mediaSource);

  useEffect(() => {
    mediaSource.addEventListener("sourceopen", () => {
      const sourceBuffer = mediaSource.addSourceBuffer("audio/mpeg");

      socket.on("response_audio", (chunk: ArrayBuffer) => {
        console.log("response arrived");
        if (!sourceBuffer.updating) {
          sourceBuffer.appendBuffer(new Uint8Array(chunk)); // Append new chunk
        }

        if (!isAudioPlaying(audio)) {
          audio.play();
        }
      });
    });

    return () => {
      socket.off("response_audio");
    };
  }, []);

  const submitTranscript = () => {
    console.log(transcript);
    socket.emit("submit_transcript", transcript);
  };

  return (
    <div className="App">
      <textarea
        style={{ width: 500, height: 300 }}
        onChange={(event) => setTranscript(event.target.value)}
      />
      <button onClick={submitTranscript}>Submit Transcript</button>
    </div>
  );
}

export default App;
