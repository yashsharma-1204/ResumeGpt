# parser.py
import re
from typing import Dict, List

def split_section(text: str, header: str) -> List[str]:
    """
    Extract lines under a header like "SUMMARY:" until the next header or end.
    Returns a list of lines (stripped).
    """
    # Find header position
    pattern = rf"{re.escape(header)}\s*(.*?)(?=\n[A-Z ]+?:|\Z)"
    m = re.search(pattern, text, flags=re.S)
    if not m:
        return []
    block = m.group(1).strip()

    # Split by newline and remove empty lines and leading "- " if present
    lines = []
    for line in block.splitlines():
        line = line.strip()
        if not line:
            continue
        # Remove leading "- " or bullets
        line = re.sub(r"^[\-\u2022]\s*", "", line)
        lines.append(line)
    return lines

def parse_llm_response(text: str) -> Dict[str, List[str]]:
    """
    Parse the LLM raw text into structured parts:
    { "summary": [...], "bullets": [...], "skills": [...] }
    """
    if not text:
        return {"summary": [], "bullets": [], "skills": []}

    # Normalize CRLF etc.
    text = text.replace("\r\n", "\n")

    summary = split_section(text, "SUMMARY:")
    bullets = split_section(text, "IMPROVED BULLETS:")
    skills = split_section(text, "SUGGESTED SKILLS:")
    # Fallback: sometimes model uses slightly different headers
    if not summary:
        summary = split_section(text, "SUMMARY")
    if not bullets:
        bullets = split_section(text, "IMPROVED BULLETS")
    if not skills:
        skills = split_section(text, "SUGGESTED SKILLS")

    return {"summary": summary, "bullets": bullets, "skills": skills}
