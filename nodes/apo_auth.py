"""Optional API-key support for OpenAI-compatible servers that require one (e.g. Unsloth Studio).

The key is NEVER a node widget, because ComfyUI saves widget values into workflow
JSON and into generated PNGs. It is read from, in order:
  1. environment variable APOSTUDIO_API_KEY (or UNSLOTH_API_KEY)
  2. a plain-text file called  api_key.txt  in the ComfyUI-ApoStudio folder (first non-empty line)
If neither exists, no Authorization header is sent (LM Studio and other keyless servers keep working).
"""
import os

_KEY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "api_key.txt")


def get_api_key():
    for var in ("APOSTUDIO_API_KEY", "UNSLOTH_API_KEY"):
        val = os.environ.get(var, "").strip()
        if val:
            return val
    try:
        with open(_KEY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    except OSError:
        pass
    return ""


def build_headers():
    headers = {"Content-Type": "application/json"}
    key = get_api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    return headers
