import json
import time
import winsound

import keyboard

import speech_recognizer
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
    filename = speech_recognizer.record()
    print(f"Recording Time: {time.perf_counter() - start_time:.2f} seconds")
    if not filename:
        return

    transcription = speech_recognizer.transcribe(filename)
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


def main():
    TRIGGER_KEY = "scroll lock"

    print("🤖 Assistant is running...")
    print(f"👉 Press '{TRIGGER_KEY}' to speak.")

    while True:
        try:
            # This blocks the code until the key is pressed
            keyboard.wait(TRIGGER_KEY)

            run_conversation_cycle()

            print(f"\n Waiting for trigger ({TRIGGER_KEY})...")

            # Small sleep to prevent accidental double-triggering
            # if you hold the key slightly too long
            time.sleep(1)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Critical Error in main loop: {e}")


if __name__ == "__main__":
    main()
