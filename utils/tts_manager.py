import base64
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


class TextToSpeech:
    def __init__(self, voice_id):
        self.api_key = os.getenv("ELEVEN_TTS")
        self.voice_id = voice_id

    def text_to_speech(self, text):
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "voice_settings": {
                "stability": 0.7,
                "similarity_boost": 0.75
            }
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            return response.content
        else:
            print("Error:", response.status_code, response.text)


    @staticmethod
    def render_audio_ui(audio_bytes: bytes):
        if not audio_bytes:
            return

        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        st.markdown("""
        <div id="speaking-indicator" style="font-size: 30px; text-align: center; margin-top: 10px; display: none;">
            🗣️ <span class="dot-animation">Speaking...</span>
        </div>
    
        <style>
            .dot-animation {
                animation: blink 1s infinite;
            }
            @keyframes blink {
                0% {opacity: 0.2;}
                50% {opacity: 1;}
                100% {opacity: 0.2;}
            }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <audio id="ttsAudio" autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
    
        <script>
            const audio = document.getElementById("ttsAudio");
            const indicator = document.getElementById("speaking-indicator");
    
            audio.onplay = () => {{
                indicator.style.display = "block";
            }};
            audio.onended = () => {{
                indicator.style.display = "none";
            }};
        </script>
        """, unsafe_allow_html=True)
