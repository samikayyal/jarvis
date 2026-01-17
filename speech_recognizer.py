import os
from datetime import datetime

import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
# Record speech into a file using speechrecognition library
os.makedirs("recordings", exist_ok=True)
filename = f"recordings/recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.1

with sr.Microphone() as source:
    print("Please speak now...")
    audio_data = recognizer.listen(source)
    with open(filename, "wb") as f:
        f.write(audio_data.get_wav_data())

# Transcribe the recorded audio using Groq API
client = Groq()

with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
        file=(filename, file.read()),
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
        prompt="This is a technical conversation in Syrian Arabic. We use English terms like Spotify, VSCode, Python, Browser, Windows, API, and many others. Please transcribe accordingly.",
    )
    print(transcription.text)
