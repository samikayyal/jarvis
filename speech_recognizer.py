import os
from datetime import datetime

import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq

from constants import KEYWORDS

load_dotenv()


def record() -> str:
    """
    Returns:
        str: The filename where the recorded audio is saved.
    """
    # Record speech into a file using speechrecognition library
    try:
        os.makedirs("recordings", exist_ok=True)
        filename = (
            f"recordings/recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        )
        recognizer = sr.Recognizer()

        # How long of a pause indicates the end of a sentence
        recognizer.pause_threshold = 1.1
        # Minimum audio energy to consider for recording
        recognizer.energy_threshold = 500

        # higher sample rate for better quality
        with sr.Microphone(sample_rate=16000) as source:
            print("Please speak now...")
            audio_data = recognizer.listen(source)
            with open(filename, "wb") as f:
                f.write(audio_data.get_wav_data())
            print("Recording saved")

        return filename
    except Exception as e:
        print(f"Error during recording: {e}")
        return ""


def transcribe(filename: str) -> str:
    """
    Returns:
        str: Transcribed text from the audio data.
    """
    if not filename:
        print("Error: No filename provided for transcription.")
        return ""

    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return ""

    # Transcribe the recorded audio using Groq API
    try:
        client = Groq()
        system_prompt: str = (
            f"This is a conversation in Syrian Arabic (Levantine) mixed with English technical terms. "
            f"Do not translate technical terms. Write technical terms in Latin script. "
            f"Context: {KEYWORDS}. "
            f"Examples:"
            f"1. Fta7 li Spotify bel playlist 'Fresh'"
            f"2. Ifta7 li VSCode 3al project esma 'Electricity Detection'"
            f"3. 3mel Search 3a Google 3an 'How to implement OAuth2 in Python'"
            f"4. Kbes Space"
        )
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                prompt=system_prompt,
                temperature=0,
                language="ar",
            )
        return transcription.text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""


if __name__ == "__main__":
    filename = record()
    if not filename:
        exit(1)

    transcription = transcribe(filename)
    print("Transcription:")
    print(transcription)

    if not transcription:
        exit(1)
