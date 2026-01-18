import webbrowser


def open_url(url: str) -> str:
    """
    Opens a specific URL in the default browser.
    """
    try:
        if not url.startswith("http"):
            url = "https://" + url

        print(f"[*] Opening URL: {url}")
        webbrowser.open(url)
        return "Opened"
    except Exception as e:
        print(f"[!] Error opening URL {url}: {e}")
        return "Failed"


def web_search(query: str) -> str:
    try:
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        print(f"[*] Performing web search: {search_url}")
        webbrowser.open(search_url)
        return "Opened"
    except Exception as e:
        print(f"[!] Error performing web search for {query}: {e}")
        return "Failed"
