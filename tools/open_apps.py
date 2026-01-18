import os
import subprocess


def open_application(app_name: str) -> str:
    print(f"[*] Opening Application: {app_name}")

    try:
        script = f'Start-Process "shell:AppsFolder\\$((Get-StartApps | Where-Object {{$_.Name -like "*{app_name}*"}}).AppID)"'
        subprocess.run(["powershell", "-Command", script], check=True)
        return "Opened"
    except Exception as e:
        print(f"[!] Error opening application {app_name}: {e}")
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
            vscode_path = "C:\\Users\\kayya\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            subprocess.run(
                [vscode_path, norm_path],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return "Opened"
        except Exception as e:
            print(f"[!] Error opening VSCode project at {path}: {e}")
            return "Failed"
    else:
        return "Not Found"
