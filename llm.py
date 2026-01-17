import os

from dotenv import load_dotenv
from groq import Groq

from constants import TOOLS_SCHEMA

load_dotenv()


def interpret_intent(transcribed_text: str) -> None:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    user_context = """
    USER CONTEXT:
    - Main Projects Directory: 'D:/Projects/'
    - Downloads Folder: 'C:/Users/kayya/Downloads/'
    """

    system_prompt = f"""
     You are a smart desktop assistant for a developer. 
        The user speaks Syrian Arabic mixed with English technical terms.
        Analyze the user's request and map it to the correct tool function.
        
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
    """
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
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
        reasoning_effort="high",
        stream=True,
    )
    for chunk in completion:
        print(chunk.choices[0].delta.content or "", end="")


if __name__ == "__main__":
    sample_text = "مرحبا كيفك؟ افتح لي Spotify."
    interpret_intent(sample_text)
