import pyautogui


def press_key(key: str) -> bool:
    print(f"[*] Pressing key: {key}")
    try:
        pyautogui.press(key)
        print("[✅] Key pressed successfully")
        return True
    except Exception as e:
        print(f"[!] Error pressing key {key}: {e}")
        return False
