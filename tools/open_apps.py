import json
import os
import subprocess
from datetime import datetime, timedelta


def open_application(app_name: str) -> str:
    print(f"[*] Opening Application: {app_name}")

    cache_file = os.path.join(os.path.dirname(__file__), "app_cache.json")
    cache = {}

    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cache = json.load(f)
        except Exception as e:
            print(f"[!] Error loading cache: {e}")

    # Remove entries older than 2 weeks
    current_time = datetime.now()
    cache = {
        k: v
        for k, v in cache.items()
        if current_time
        - datetime.fromisoformat(v.get("timestamp", "1970-01-01T00:00:00"))
        < timedelta(weeks=2)
    }

    app_id = None
    if app_name in cache:
        app_id = cache[app_name]["app_id"]
    else:
        try:
            # Find AppID
            script = f"(Get-StartApps | Where-Object {{ $_.Name -like '*{app_name}*' }} | Select-Object -First 1).AppID"
            result = subprocess.run(
                ["powershell", "-Command", script], capture_output=True, text=True
            )

            if result.returncode == 0 and result.stdout.strip():
                app_id = result.stdout.strip()
                cache[app_name] = {
                    "app_id": app_id,
                    "timestamp": current_time.isoformat(),
                }
                try:
                    with open(cache_file, "w") as f:
                        json.dump(cache, f, indent=4)
                except Exception as e:
                    print(f"[!] Error saving cache: {e}")
            else:
                print(f"[!] Cloud not find AppID for: {app_name}")
        except Exception as e:
            print(f"[!] Error searching for app: {e}")

    if app_id:
        try:
            script = f'Start-Process "shell:AppsFolder\\{app_id}"'
            subprocess.run(["powershell", "-Command", script], check=True)
            return "Opened"
        except Exception as e:
            print(f"[!] Error opening application {app_name}: {e}")
            return "Failed"

    return "Failed"


def open_directory(path: str) -> str:
    print(f"[*] Opening Directory: {path}")

    # Clean up the path for Windows (handling / vs \)
    norm_path = os.path.normpath(path)

    if os.path.exists(norm_path):
        try:
            os.startfile(norm_path)
            return "Opened"
        except Exception as e:
            print(f"[!] Error opening directory {path}: {e}")
            return "Failed"
    else:
        return "Not Found"


def open_vscode_project(path: str) -> str:
    print(f"[*] Opening VSCode Project at: {path}")

    # Clean up the path for Windows (handling / vs \)
    norm_path = os.path.normpath(path)

    if os.path.exists(norm_path):
        try:
            appdata_path = os.getenv("LOCALAPPDATA")
            if not appdata_path:
                raise EnvironmentError("LOCALAPPDATA environment variable not found.")
            vscode_path = os.path.join(
                appdata_path, "Programs", "Microsoft VS Code", "Code.exe"
            )
            subprocess.run(
                [vscode_path, norm_path],
                shell=False,  # To be able to pass list of args
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return "Opened"
        except Exception as e:
            print(f"[!] Error opening VSCode project at {path}: {e}")
            return "Failed"
    else:
        return "Not Found"


def open_university_portal() -> str:
    """TODO: Implement university portal automation."""
    print("[*] Opening PSUT Portal")
    return "Not Implemented"
    # browser.get("https://portal.psut.edu.jo")

    # # Define wait object
    # wait = WebDriverWait(browser, 10)

    # # Login
    # username_input = wait.until(EC.presence_of_element_located((By.ID, "UserID")))
    # password_input = browser.find_element(By.ID, "loginPass")

    # username_input.send_keys(USERNAME)
    # password_input.send_keys(PASSWORD)

    # password_input.submit()

    # close_notifications(browser)

    # # Change language to English
    # dropdown = wait.until(EC.presence_of_element_located((By.ID, "dropdown-flag")))
    # dropdown.click()
    # english_option = wait.until(
    #     EC.presence_of_element_located(
    #         (By.XPATH, '//*[@id="navbar-mobile"]/ul[2]/li[2]/div/a[2]')
    #     )
    # )
    # english_option.click()


#     from gemini:
#     # pip install webdriver-manager
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.core.os_manager import ChromeType

# brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# options = Options()
# options.binary_location = brave_path

# # explicit tells the manager: "Find the driver that matches the Brave binary"
# service = Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install())

# browser = webdriver.Chrome(service=service, options=options)

# Check https://pypi.org/project/webdriver-manager/ for more info
