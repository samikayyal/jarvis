import keyboard
import numpy as np
import openwakeword
import pyaudio
from openwakeword.model import Model


class AssistantActivator:
    def __init__(self, model_name="hey_jarvis_v0.1"):
        self.model_name = model_name

        # Load the wake word model
        openwakeword.utils.download_models([model_name])
        self.model = Model(wakeword_models=[f'{model_name}.tflite'])

        self.CHUNK = 1280
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.SAMPLE_RATE = 16000

    def wait_for_activation(self, trigger_key):
        """
        Listens to the microphone until the wake word is detected
        OR the trigger key is pressed.
        Returns: 'voice' or 'key'
        """
        # Open the stream
        p = pyaudio.PyAudio()
        stream = p.open(
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
                if predictions[f"{self.model_name}.tflite"] >= 0.5:
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
            p.terminate()

        return triggered_by


if __name__ == "__main__":
    activator = AssistantActivator("hey_jarvis_v0.1")
    while True:
        print("Listening for wake word or key press...")
        source = activator.wait_for_activation("scroll lock")
        print(f"Activated by: {source}")
        time.sleep(1)  # Debounce delay
