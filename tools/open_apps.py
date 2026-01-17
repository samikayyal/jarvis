import os


def open_application() -> bool:
    return True


def open_directory(path: str) -> bool:
    print(f"[*] Opening Directory: {path}")

    # Clean up the path for Windows (handling / vs \)
    norm_path = os.path.normpath(path)

    if os.path.exists(norm_path):
        try:
            os.startfile(norm_path)
            return True
        except Exception as _:
            return False
    else:
        return False
