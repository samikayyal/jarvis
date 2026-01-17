import json

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


def main():
    filename = speech_recognizer.record()

    transcription = speech_recognizer.transcribe(filename)
    print("Transcription:")
    print(transcription)

    print("\nInterpreted Intent and Tool Invocation:")
    intent_json = interpret_intent(transcription)
    print(intent_json)

    # Execute the interpreted function (example)
    if intent_json:
        try:
            intent = json.loads(intent_json)
            tool_name = intent.get("tool")
            parameters = intent.get("parameters", {})
            result = execute_function(tool_name, parameters)
            print("\nFunction Execution Result:")
            print(result)
        except json.JSONDecodeError:
            print("Error: Failed to parse the intent JSON.")


if __name__ == "__main__":
    main()
