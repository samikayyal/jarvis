import json
import time
import winsound

import speech_recognizer
from activator import AssistantActivator
from constants import AVAILABLE_FUNCTIONS
from llm import interpret_intent


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


def run_conversation_cycle():
    """
    Runs one full cycle: Record -> Transcribe -> Interpret -> Execute
    """
    start_time = time.perf_counter()
    audio_data = speech_recognizer.record()
    print(f"Recording Time: {time.perf_counter() - start_time:.2f} seconds")
    if not audio_data:
        return

    transcription = speech_recognizer.transcribe(audio_data)
    if not transcription:
        return

    print(f"\n User said: {transcription}")
    print(f"Transcription Time: {time.perf_counter() - start_time:.2f} seconds")

    # Interpret Intent
    intent_json = interpret_intent(transcription)
    print(f"Intent: {intent_json}")
    print(f"Interpretation Time: {time.perf_counter() - start_time:.2f} seconds")

    # Execute
    if intent_json:
        try:
            intent = json.loads(intent_json)
            tool_name = intent.get("tool")
            parameters = intent.get("parameters", {})
            if tool_name.lower() == "none":
                print("No applicable tool found for the request.")
                winsound.Beep(500, 500)  # Error sound
                return

            print(f"Executing: {tool_name} with {parameters}")
            result = execute_function(tool_name, parameters)

            print(f"Result: {result}")
            print(f"Execution Time: {time.perf_counter() - start_time:.2f} seconds")

            # Play a success sound (Low-High)
            winsound.Beep(800, 100)
            winsound.Beep(1200, 100)

        except json.JSONDecodeError:
            print("Error: Failed to parse the intent JSON.")
            winsound.Beep(500, 500)  # Error sound

    speech_recognizer.save_recording(audio_data)


def main():
    TRIGGER_KEY = "scroll lock"
    activator = AssistantActivator()

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
            winsound.Beep(600, 100)

            run_conversation_cycle()
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
