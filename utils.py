# utils.py

def clean_text(text: str) -> str:
    """
    Simple helper to strip extra spaces and handle None safely.
    """
    if not text:
        return ""
    return text.strip()
