import os
import time
import winsound
from datetime import datetime

import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq

from constants import KEYWORDS  # noqa: F401

load_dotenv()


def record() -> str | None:
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
        recognizer.pause_threshold = 1.3
        # Minimum audio energy to consider for recording
        recognizer.energy_threshold = 500

        # higher sample rate for better quality
        with sr.Microphone(sample_rate=16000) as source:
            print("Please speak now...")
            # Play a sound to indicate recording started
            winsound.Beep(1000, 200)
            audio_data = recognizer.listen(source)
            with open(filename, "wb") as f:
                f.write(audio_data.get_wav_data())
            print("Recording saved")

        return filename
    except Exception as e:
        print(f"Error during recording: {e}")
        return None


def transcribe(filename: str) -> str | None:
    """
    Returns:
        str: Transcribed text from the audio data.
    """
    if not filename:
        print("Error: No filename provided for transcription.")
        return None

    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return None

    # Transcribe the recorded audio using Groq API
    try:
        client = Groq()
        system_prompt: str = (
            f"This is a conversation in Syrian Arabic (Levantine) mixed with English technical terms. "  # noqa: F541
            f"Do not translate technical terms. Write technical terms in Latin script. "  # noqa: F541
            # f"Context: {KEYWORDS}. "
            # f"Examples: The options are not limited to these, but here are some:"
            # f"1. Fta7 li Spotify bel playlist 'Fresh'"
            # f"2. Fta7 VSCode 3a project esma 'Electricity Detection'"
            # f"3. 3mel Search 3a Google 3an 'How to implement OAuth2 in Python'"
            # f"4. Kbes Space"
            # f"5. Tafi el laptop"
        )
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3",
                response_format="verbose_json",
                prompt=system_prompt,
                temperature=0,
                language="ar",
            )
        return transcription.text or None
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None


if __name__ == "__main__":
    filename = record()
    if not filename:
        exit(1)

    start_time = time.perf_counter()
    transcription = transcribe(filename)  # type: ignore
    print(f"Transcription Time: {time.perf_counter() - start_time:.2f} seconds")
    print("Transcription:")
    print(transcription)
    with open("test.txt", "w", encoding="utf-8") as f:
        f.write(transcription or "")

    if not transcription:
        exit(1)
