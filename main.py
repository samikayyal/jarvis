import json
import threading
import time

import speech_recognizer
from activator import AssistantActivator
from cancellation import CancellationWatcher
from constants import AVAILABLE_FUNCTIONS, play_sound_async
from llm import interpret_intent
from tts import speak


def run_interruptible(func, watcher, *args, **kwargs):
    """
    Runs a function in a separate thread to allow main thread to check for cancellation.
    Returns early if watcher detects abortion.
    """
    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e

    t = threading.Thread(target=target)
    t.start()

    while t.is_alive():
        if watcher.was_aborted():
            return None
        time.sleep(0.1)

    if exception[0]:
        raise exception[0]

    return result[0]


def execute_function(function_name: str, args: dict):
    """
    Maps the string function name from the LLM to the actual Python function.
    """
    # Map of string names to actual function objects

    if function_name in AVAILABLE_FUNCTIONS:
        func = AVAILABLE_FUNCTIONS[function_name]
        # Call the function with **args (unpacks the dictionary)
        return func(**args)
    else:
        return f"Error: Function {function_name} is not implemented."


def run_conversation_cycle(cancellation_watcher: CancellationWatcher):
    """
    Runs one full cycle: Record -> Transcribe -> Interpret -> Execute
    """
    start_time = time.perf_counter()

    # =============== Record Audio ===============
    # Mute pc audio during recording, restore previous state after
    audio_data = speech_recognizer.record()

    print(f"Recording Time: {time.perf_counter() - start_time:.2f} seconds")
    start_time = time.perf_counter()
    if not audio_data:
        return

    # Start watching for "Insa" now that we are processing
    cancellation_watcher.start()

    try:
        # =============== Transcribe Audio ===============
        transcription = run_interruptible(
            speech_recognizer.transcribe, cancellation_watcher, audio_data
        )

        if cancellation_watcher.was_aborted():
            return
        if not transcription:
            return

        print(f"\n User said: {transcription}")
        print(f"Transcription Time: {time.perf_counter() - start_time:.2f} seconds")
        start_time = time.perf_counter()

        # ============== Interpret Intent ===============
        intent_json = run_interruptible(
            interpret_intent, cancellation_watcher, transcription
        )

        if cancellation_watcher.was_aborted():
            return

        print(f"Intent: {intent_json}")
        print(f"Interpretation Time: {time.perf_counter() - start_time:.2f} seconds")
        start_time = time.perf_counter()

        # ============= Execute ===============
        if intent_json:
            try:
                intent = json.loads(intent_json)
                tool_name = intent.get("tool")
                parameters = intent.get("parameters", {})
                if not tool_name or tool_name.lower() == "none":
                    print("No applicable tool found for the request.")
                    play_sound_async(500, 500)  # Error sound
                else:
                    print(f"Executing: {tool_name} with {parameters}")
                    result = run_interruptible(
                        execute_function, cancellation_watcher, tool_name, parameters
                    )

                    if cancellation_watcher.was_aborted():
                        return

                    print(f"Result: {result}")
                    print(
                        f"Execution Time: {time.perf_counter() - start_time:.2f} seconds"
                    )

                    # Play a success sound (Low-High)
                    play_sound_async(800, 100)
                    play_sound_async(1200, 100)

                # ============== Speak the response ===============
                speech = intent.get("speech", "")
                if speech:
                    speak(speech)

            except json.JSONDecodeError:
                print("Error: Failed to parse the intent JSON.")
                play_sound_async(500, 500)  # Error sound

        speech_recognizer.save_recording(audio_data)

    finally:
        # Ensure we always stop the watcher (releases microphone)
        cancellation_watcher.stop()


def main():
    TRIGGER_KEY = "scroll lock"
    activator = AssistantActivator()

    cancellation_watcher = CancellationWatcher()

    print("🤖 Assistant is running...")
    print(f"👉 Say 'Jarvis' or Press '{TRIGGER_KEY}' to speak.")

    while True:
        try:
            trigger_source = activator.wait_for_activation(TRIGGER_KEY)
            if trigger_source == "voice":
                print("\n[Activated by Voice]")
            elif trigger_source == "key":
                print("\n[Activated by Key Press]")
            else:
                print("\n[Unknown Activation]")
                continue

            # Acknowledgement beep
            play_sound_async(600, 100)

            run_conversation_cycle(cancellation_watcher)
            print("\n Waiting for trigger ...")

            # Small buffer to prevent immediate re-triggering
            time.sleep(1.5)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Critical Error in main loop: {e}")
            # Sleep briefly to avoid infinite error loops
            time.sleep(1)


if __name__ == "__main__":
    main()
