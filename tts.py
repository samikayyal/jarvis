import asyncio
import json
import os
import uuid

import edge_tts
import pygame
import soundfile as sf
from pedalboard import (
    Chorus,
    Compressor,
    Gain,
    HighpassFilter,
    LowpassFilter,
    Pedalboard,
    Phaser,  # noqa: F401
    Reverb,
)

# --- 1. BASE VOICE TUNING (The Source) ---
# Ryan is the best base.
VOICE = "en-GB-RyanNeural"
# Pitch: Lower = darker/calmer. -5Hz to -10Hz is the sweet spot.
PITCH = "-8Hz"
# Rate: Faster = more efficient/computer-like. +10% to +15%.
RATE = "+15%"

# Files
BUFFER_FILE = "raw_audio.mp3"
PROCESSED_FILE = "jarvis_output.wav"

# Cache
CACHE_DIR = "responses"
CACHE_FILE = "responses_cache.json"

# In-memory cache
_cache: dict[str, str] = {}


def _load_cache() -> dict[str, str]:
    """Load cache from disk into memory."""
    global _cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            _cache = json.load(f)
    else:
        _cache = {}
    return _cache


def _save_cache():
    """Save in-memory cache to disk."""
    global _cache
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(_cache, f, indent=4, ensure_ascii=False)
    # Reload cache after saving
    _load_cache()


def _get_cached_file(text: str) -> str | None:
    """Check if text is cached and return the file path if it exists."""
    if text in _cache:
        cached_path = os.path.join(CACHE_DIR, _cache[text])
        if os.path.exists(cached_path):
            return cached_path
    return None


def _add_to_cache(text: str, filename: str):
    """Add a new entry to the cache."""
    _cache[text] = filename
    _save_cache()


# Initialize cache on module load
os.makedirs(CACHE_DIR, exist_ok=True)
_load_cache()


async def _generate_audio(text):
    communicate = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await communicate.save(BUFFER_FILE)


def _process_audio_dsp():
    """
    Applies the 'Iron Man Helmet' effects chain.
    """
    try:
        # Load audio (Pedalboard requires reading via soundfile)
        audio, sample_rate = sf.read(BUFFER_FILE)

        # --- 2. THE EFFECT CHAIN (The Tuning Lab) ---
        # Modify these numbers to change the 'flavor' of the robot

        board = Pedalboard(
            [
                # A. PRE-FILTERING
                # Cutting lows makes him sound crisp/digital.
                HighpassFilter(cutoff_frequency_hz=200),
                # B. COMPRESSION
                # Keeps his voice volume perfectly steady, never whispering, never shouting.
                Compressor(threshold_db=-15, ratio=4),
                #
                # C. THE ROBOTIC TEXTURE (Choose ONE or mix gently)
                # OPTION 1: CHORUS (The "Metallic Sheen") - Preferred for Jarvis
                # Makes it sound like the voice is coming from multiple slightly sync-off speakers.
                Chorus(rate_hz=1.0, depth=0.1, mix=0.3),
                # OPTION 2: PHASER (The "Sci-Fi" wobble) - Use very low mix or it sounds like C-3PO
                # Phaser(rate_hz=0.5, depth=0.1, mix=0.1),
                #
                # D. SPACE (The "Helmet" Environment)
                Reverb(room_size=0.1, damping=0.8, wet_level=0.1, dry_level=0.9),
                #
                # E. FINAL POLISH
                # Cutting ultra-high frequencies removes digital hiss
                LowpassFilter(cutoff_frequency_hz=7000),
                # Boost volume back up after filtering
                Gain(gain_db=3),
            ]
        )

        # Run the effects
        processed_audio = board(audio, sample_rate)

        # Save result
        sf.write(PROCESSED_FILE, processed_audio, sample_rate)
        return True

    except Exception as e:
        print(f"[!] DSP Error: {e}")
        return False


def speak(text: str):
    print(f"🗣️ Jarvis: {text}")

    # Check cache first
    cached_file = _get_cached_file(text)
    if cached_file:
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(cached_file)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.quit()
            return
        except Exception as e:
            print(f"[!] Cache Playback Error: {e}")
            # Fall through to regenerate

    try:
        # 1. Generate Raw
        asyncio.run(_generate_audio(text))

        # 2. Process
        if _process_audio_dsp():
            # Generate unique filename and cache it
            unique_id = uuid.uuid4().hex[:8]
            cached_filename = f"response_{unique_id}.wav"
            cached_path = os.path.join(CACHE_DIR, cached_filename)

            # Move processed file to cache
            os.rename(PROCESSED_FILE, cached_path)
            _add_to_cache(text, cached_filename)

            playback_file = cached_path
        else:
            playback_file = BUFFER_FILE

        # 3. Play
        pygame.mixer.init()
        pygame.mixer.music.load(playback_file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()

    except Exception as e:
        print(f"[!] Playback Error: {e}")
    finally:
        # Cleanup temp files only (cached files are kept)
        if os.path.exists(BUFFER_FILE):
            os.remove(BUFFER_FILE)
        if os.path.exists(PROCESSED_FILE):
            os.remove(PROCESSED_FILE)


if __name__ == "__main__":
    # Test phrase with lots of 'S' and 'T' sounds to test crispness
    # speak("System diagnostics complete. All systems online. Ready for input, sir.")
    speak("Yes sir.")
