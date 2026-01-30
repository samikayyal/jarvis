import os

from dotenv import load_dotenv
from groq import Groq

from constants import LLM_MODEL, PROJECTS_DIR, TOOLS_SCHEMA

load_dotenv()


def clean_json_output(text: str | None) -> str | None:
    """
    Cleans the LLM output to ensure it is valid JSON.
    Removes ```json markers and finds the first '{' and last '}'.
    """
    if not text:
        return None

    # Remove Markdown code block syntax
    cleaned = text.replace("```json", "").replace("```", "")

    # Find the start and end of the JSON object
    # (This handles cases where the LLM says "Here is your JSON: { ... }")
    start_index = cleaned.find("{")
    end_index = cleaned.rfind("}")

    if start_index != -1 and end_index != -1:
        cleaned = cleaned[start_index : end_index + 1]

    return cleaned.strip()


def interpret_intent(transcribed_text: str) -> str | None:
    projects = "\n - ".join(os.listdir(PROJECTS_DIR))
    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")

    user_context = f"""
    USER CONTEXT:
    - Main Projects Directory: '{PROJECTS_DIR}'
        {projects}
    - Downloads Folder: '{downloads_dir}'
    """

    system_prompt = f"""
    SYSTEM IDENTITY:
    You are J.A.R.V.I.S, a smart desktop assistant for a developer.
    
    USER INPUT:
    - The user speaks Syrian Arabic (Shami) mixed with English technical terms.
    - Input may be in Arabic Script (e.g., "افتح سبوتيفاي") or Arabizi (e.g., "fta7 spotify").
    - Transcriptions may contain slight errors; infer intent where possible.
    
    YOUR TASKS:
    1. Analyze the user's request based on the context below.
    2. Map it to the correct tool function.
    3. Generate a "speech" response in ENGLISH.
    
    SPEECH GUIDELINES (JARVIS PERSONA):
    - Tone: Calm, dry, British wit, highly professional.
    - Content: Concise updates. No fake enthusiasm (no exclamation marks).
    - Style: Use words like "Protocols", "Initializing", "Sir", "Aborting".
    
    {user_context}

    AVAILABLE TOOLS:
    {TOOLS_SCHEMA}
        
    RESPONSE FORMAT:
    You must ONLY respond with a JSON object. DO NOT respond with anything else.
    {{
        "tool": "tool_name_or_none",
        "parameters": {{ ... }},
        "speech": "The verbal response in English."
    }}

    HANDLING RULES:
    - If the user wants to open Netflix, use "open_application" with "Netflix".
    
    - If the user says 'Insa', 'Cancel', 'Khalas', or similar:
      Output: {{"tool": "none", "parameters": {{}}, "speech": "Aborting."}}
      
    - If no tool fits the request (or you are just chatting):
      Output: {{"tool": "none", "parameters": {{}}, "speech": "I am unsure how to proceed with that request, sir."}}
      
    - If the request is purely conversational (e.g., "Kifak?"):
      Output: {{"tool": "none", "parameters": {{}}, "speech": "All systems operational. Ready for input."}}
    """
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": transcribed_text,
                },
            ],
            temperature=0,
            reasoning_effort="medium" if "gpt-oss" in LLM_MODEL else None,
            stream=False,
        )

        return clean_json_output(completion.choices[0].message.content) or None
    except Exception as e:
        print(f"[!] Error interpreting intent: {e}")
        return None


if __name__ == "__main__":
    sample_text = "مرحبا كيفك؟ افتح لي Spotify."
    print("Interpretation Result:")
    print(interpret_intent(sample_text))
    if not interpret_intent(sample_text):
        exit(1)
