import os

from dotenv import load_dotenv
from groq import Groq

from constants import LLM_MODEL, PROJECTS_DIR, TOOLS_SCHEMA

load_dotenv()


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
     You are a smart desktop assistant for a developer. 
        The user speaks Syrian Arabic mixed with English technical terms.
        Analyze the user's request and map it to the correct tool function.
        The user's command may write English technical terms in Arabic.
        
        {user_context}

        Here are the available tools and their schemas:
        {TOOLS_SCHEMA}
        
    You should only respond with a JSON object that specifies the tool to use and its parameters.
    Example response:
    {{
        "tool": "open_application",
        "parameters": {{
            "app_name": "VSCode"
        }}
    }}

    Notes:
        - If the user wants to open netflix, use the "open_application" tool with app_name "Netflix".
        - If none of the tools fit the user's request, respond with: {{"tool": "none", "parameters": {{}}}}
        - If the user says 'Insa انسا', 'cancel', or similar, respond with: {{"tool": "none", "parameters": {{}}}}
        - The input might be in Arabic Script (افتح سبوتيفاي) or Arabizi (fta7 spotify). Handle both.
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

        return completion.choices[0].message.content or None
    except Exception as e:
        print(f"[!] Error interpreting intent: {e}")
        return None


if __name__ == "__main__":
    sample_text = "مرحبا كيفك؟ افتح لي Spotify."
    print("Interpretation Result:")
    print(interpret_intent(sample_text))
    if not interpret_intent(sample_text):
        exit(1)
