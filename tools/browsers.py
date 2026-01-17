import webbrowser


def open_url(url: str) -> bool:
    """
    Opens a specific URL in the default browser.
    """
    if not url.startswith("http"):
        url = "https://" + url

    print(f"[*] Opening URL: {url}")
    webbrowser.open(url)
    return True


def web_search(query: str) -> bool:
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    print(f"[*] Performing web search: {search_url}")
    webbrowser.open(search_url)
    return True
