from typing import Callable

from tools.browsers import open_url, web_search
from tools.miscellaneous import press_key, shutdown_system
from tools.open_apps import open_application, open_directory, open_vscode_project

KEYWORDS: list[str] = [
    "Spotify",
    "Portal",
    "University",
    "Brave",
    "Netflix",
    "Terminal",
    "Powershell",
    "VSCode",
    "Settings",
    "GitHub",
    "Space",
    "Enter",
    "Escape",
    "Folder",
    "Downloads",
    "Projects",
    "Shutdown",
    "Discord",
    "Laptop",
    "PSUT",
]

TOOLS_SCHEMA: list[dict] = [
    # Open App tool
    {
        "name": "open_application",
        "description": "Open a desktop application.",
        "parameters": [
            {
                "name": "app_name",
                "type": "string",
                "description": "The name of the application to open.",
            }
        ],
    },
    # Open URL tool
    {
        "name": "open_url",
        "description": "Open a specific URL in the default web browser.",
        "parameters": [
            {
                "name": "url",
                "type": "string",
                "description": 'The full URL to open (e.g., "https://google.com").',
            }
        ],
    },
    # Web Search tool
    {
        "name": "web_search",
        "description": "Perform a Google search for a given query.",
        "parameters": [
            {
                "name": "query",
                "type": "string",
                "description": "The search query string.",
            }
        ],
    },
    # Open Directory tool
    {
        "name": "open_directory",
        "description": "Open a specific folder/directory in File Explorer.",
        "parameters": [
            {
                "name": "path",
                "type": "string",
                "description": "The absolute path or a known shortcut (e.g., 'Downloads', 'C:/Projects').",
            }
        ],
    },
    # Open VsCode Project tool
    {
        "name": "open_vscode_project",
        "description": "Open Visual Studio Code in a specific directory.",
        "parameters": [
            {
                "name": "path",
                "type": "string",
                "description": "The path to the project folder.",
            }
        ],
    },
    # Press Key tool
    {
        "name": "press_keyboard_key",
        "description": "Press a keyboard key (e.g., Enter, Space, Escape, etc...).",
        "parameters": [
            {
                "name": "key",
                "type": "string",
                "description": "The keyboard key to press (e.g., 'Enter', 'Space', 'Escape').",
            }
        ],
    },
    # Shutdown tool
    {
        "name": "shutdown_system",
        "description": "Shut down the computer system.",
        "parameters": [],
    },
]

AVAILABLE_FUNCTIONS: dict[str, Callable] = {
    "open_application": open_application,
    "open_url": open_url,
    "web_search": web_search,
    "open_directory": open_directory,
    "open_vscode_project": open_vscode_project,
    "press_keyboard_key": press_key,
    "shutdown_system": shutdown_system,
}


# For testing
if __name__ == "__main__":
    print(open_application("matlab"))
