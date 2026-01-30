import os
import time
from datetime import datetime

import speech_recognition as sr
from dotenv import load_dotenv
from groq import Groq

from constants import KEYWORDS, play_sound_async  # noqa: F401

load_dotenv()


def record() -> bytes | None:
    """
    Returns:
        bytes: The audio data of the recording.
    """
    # Record speech using speechrecognition library
    try:
        recognizer = sr.Recognizer()

        # How long of a pause indicates the end of a sentence
        recognizer.pause_threshold = 1.3
        # Minimum audio energy to consider for recording
        recognizer.energy_threshold = 500

        recognizer.dynamic_energy_threshold = False  # Faster startup

        # higher sample rate for better quality
        with sr.Microphone(sample_rate=16000) as source:
            print("Please speak now...")
            play_sound_async(1000, 200)
            # Play a sound to indicate recording started
            audio_data = recognizer.listen(source)
            wav_data = audio_data.get_wav_data()
            print("Recording finished")

        return wav_data
    except Exception as e:
        print(f"Error during recording: {e}")
        return None


def save_recording(audio_data: bytes) -> str | None:
    """
    Saves the audio data to a file.

    Args:
        audio_data (bytes): The audio data to save.

    Returns:
        str: The filename where the audio was saved.
    """
    try:
        os.makedirs("recordings", exist_ok=True)
        filename = (
            f"recordings/recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        )
        with open(filename, "wb") as f:
            f.write(audio_data)
        print("Recording saved")
        return filename
    except Exception as e:
        print(f"Error saving recording: {e}")
        return None


def transcribe(audio_data: bytes) -> str | None:
    """
    Args:
        audio_data (bytes): The audio data to transcribe.
    Returns:
        str: Transcribed text from the audio data.
    """
    if not audio_data:
        print("Error: No audio data provided for transcription.")
        return None

    # Transcribe the recorded audio using Groq API
    try:
        client = Groq()
        system_prompt: str = (
            "This is a conversation in Syrian Arabic (Levantine) mixed with English technical terms. "
            "Do not translate technical terms. Write technical terms in Latin script. "
            "These are some terms the user might use:"
            "3mel Search عميل سيرش, Fta7 فتاح, Shaghil شغل, Saakker سكر"
        )
        transcription = client.audio.transcriptions.create(
            file=("recording.wav", audio_data),
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
    audio_data = record()
    if not audio_data:
        exit(1)

    start_time = time.perf_counter()
    transcription = transcribe(audio_data)  # type: ignore
    print(f"Transcription Time: {time.perf_counter() - start_time:.2f} seconds")
    print("Transcription:")
    print(transcription)

    save_recording(audio_data)  # type: ignore

    with open("test.txt", "w", encoding="utf-8") as f:
        f.write(transcription or "")

    if not transcription:
        exit(1)
