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
    os.makedirs("recordings", exist_ok=True)
    filename = f"recordings/recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
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


def transcribe(filename: str) -> str:
    """
    Returns:
        str: Transcribed text from the audio data.
    """
    # Transcribe the recorded audio using Groq API
    client = Groq()
    system_prompt: str = (
        f"This is a conversation in Syrian Arabic (Levantine) mixed with English technical terms. "
        f"Do not translate technical terms. Write technical terms in Latin script. "
        f"Context: {KEYWORDS}. "
        f"Example: 'Sma3 khaye. Bdi afta7 Spotify w el Portal tba3 el jam3a'"
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


if __name__ == "__main__":
    filename = record()

    transcription = transcribe(filename)
    print("Transcription:")
    print(transcription)
