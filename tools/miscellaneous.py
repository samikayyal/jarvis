import subprocess

import pyautogui


def press_key(key: str) -> str:
    print(f"[*] Pressing key: {key}")
    try:
        pyautogui.press(key)
        print("[✅] Key pressed successfully")
        return "Pressed"
    except Exception as e:
        print(f"[!] Error pressing key {key}: {e}")
        return "Failed"


def shutdown_system() -> str:
    print("[*] Shutting down the system")
    try:
        subprocess.run(
            "shutdown /s /t 30",
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        return "Shutdown Initiated"
    except Exception as e:
        print(f"[!] Error shutting down the system: {e}")
        return "Failed"
