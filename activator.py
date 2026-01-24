import time

import keyboard
import numpy as np
import pyaudio
from openwakeword.model import Model


class AssistantActivator:
    def __init__(self):
        self.model_name = "jarvis"

        # Load the wake word model
        self.model = Model(wakeword_models=[f"{self.model_name}.tflite"])

        self.CHUNK = 1280
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.SAMPLE_RATE = 16000
        self.p = pyaudio.PyAudio()

    def wait_for_activation(self, trigger_key):
        """
        Listens to the microphone until the wake word is detected
        OR the trigger key is pressed.
        Returns: 'voice' or 'key'
        """
        # Open the stream
        stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.SAMPLE_RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        triggered_by = None

        try:
            while True:
                # Get audio
                data = stream.read(self.CHUNK)
                audio_np = np.frombuffer(data, dtype=np.int16)

                # Predict
                predictions = self.model.predict(audio_np)

                # Check Wake Word
                if predictions[self.model_name] >= 0.5:
                    triggered_by = "voice"
                    break

                # Check Key Press
                if keyboard.is_pressed(trigger_key):
                    triggered_by = "key"
                    break

        finally:
            # Close stream so main.py can use the mic later
            stream.stop_stream()
            stream.close()

        return triggered_by

    def __del__(self):
        self.p.terminate()  # Cleanup when program exits


if __name__ == "__main__":
    activator = AssistantActivator()
    while True:
        print("\nListening for wake word or key press...")
        source = activator.wait_for_activation("scroll lock")
        print(f"Activated by: {source}")
        time.sleep(1)  # Debounce delay
