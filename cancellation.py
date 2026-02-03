import threading

import numpy as np
import pyaudio
from openwakeword.model import Model

from constants import INSA_DETECTION_THRESHOLD, play_sound_async


class CancellationWatcher:
    def __init__(self):
        # Load the model for cancellation
        self.model = Model(wakeword_models=["insa.tflite"])
        self.chunk_size = 1280
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000

        # if both are false, stopped manually
        # if _aborted is true, it was stopped due to detection
        self._running = False
        self._aborted = False
        self._thread = None
        self._pyaudio = None
        self._stream = None

    def _listen_loop(self):
        """The function that runs in the background thread."""
        self._pyaudio = pyaudio.PyAudio()

        try:
            self._stream = self._pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size,
            )

            self.model.reset()

            while self._running:
                data = self._stream.read(self.chunk_size, exception_on_overflow=False)
                audio_np = np.frombuffer(data, dtype=np.int16)

                prediction = self.model.predict(audio_np)

                # Check for "insa"
                if prediction.get("insa", 0) >= INSA_DETECTION_THRESHOLD:
                    print("\n[!] 'Insa' detected! Aborting...")
                    self._aborted = True
                    self._running = False  # Stop the loop

                    # Immediate Feedback
                    play_sound_async(500, 300)
                    play_sound_async(400, 400)
                    break

        except Exception as e:
            print(f"Error in cancellation thread: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Safely close streams."""
        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
        if self._pyaudio:
            self._pyaudio.terminate()

    def start(self):
        """Start listening for 'insa' in the background."""
        self._running = True
        self._aborted = False
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the background listener."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)  # Wait for it to finish safely

    def was_aborted(self):
        """Check if the flag was set."""
        return self._aborted


if __name__ == "__main__":
    watcher = CancellationWatcher()

    try:
        while True:
            watcher.start()
            print("Say 'Insa' to abort. (Ctrl+C to exit)")
            while not watcher.was_aborted():
                pass
            print("Insa detected, aborting main task.\n\n")
            watcher.stop()
    except KeyboardInterrupt:
        print("\nExiting...")
        watcher.stop()
