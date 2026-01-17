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
                "description": 'The name of the application to open (e.g., "notepad", "calc").',
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
]
