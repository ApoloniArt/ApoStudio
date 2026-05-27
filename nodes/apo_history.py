import json
import pathlib
import time

DEFAULT_SESSION = pathlib.Path(__file__).parent.parent / "prompts" / "session.json"


def _load(path: pathlib.Path) -> list:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
            return data.get("messages", [])
    except Exception:
        pass
    return []


def _save(path: pathlib.Path, history: list):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {"version": 1, "saved": time.strftime("%Y-%m-%dT%H:%M:%S"), "messages": history},
            indent=2, ensure_ascii=False
        ),
        encoding="utf-8"
    )


def _to_markdown(history: list) -> str:
    if not history:
        return ""
    lines = []
    for msg in history:
        role    = msg.get("role", "unknown")
        content = msg.get("content", "")
        # Handle multimodal content (list of parts)
        if isinstance(content, list):
            text_parts = [p.get("text", "") for p in content if isinstance(p, dict) and p.get("type") == "text"]
            content = " ".join(text_parts)
        if role == "system":
            lines.append(f"### 🔧 System\n{content}\n")
        elif role == "user":
            lines.append(f"### 👤 User\n{content}\n")
        elif role == "assistant":
            lines.append(f"### 🤖 Assistant\n{content}\n")
        else:
            lines.append(f"### {role.capitalize()}\n{content}\n")
    return "\n---\n\n".join(lines)


class ApoStudioHistory:
    CATEGORY = "ApoStudio"
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "action": (["load", "load & append", "clear", "save"],),
                "session_file": ("STRING", {
                    "default": str(DEFAULT_SESSION),
                    "multiline": False,
                }),
            },
            "optional": {
                "history_in": ("APO_HISTORY",),
            },
        }

    RETURN_TYPES = ("APO_HISTORY", "STRING", "STRING", "INT")
    RETURN_NAMES = ("history_out", "history_json", "history_md", "turn_count")

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    def run(self, action, session_file, history_in=None):
        path     = pathlib.Path(session_file.strip()) if session_file.strip() else DEFAULT_SESSION
        incoming = list(history_in) if history_in else []

        if action == "load":
            history = _load(path)
            print(f"[ApoStudio History] Loaded {len(history)} messages from file")

        elif action == "load & append":
            existing = _load(path)
            print(f"[ApoStudio History] Existing in file: {len(existing)} messages")
            print(f"[ApoStudio History] Incoming from Chat: {len(incoming)} messages")
            history = incoming if incoming else existing
            if history:
                _save(path, history)
            print(f"[ApoStudio History] Saved {len(history)} messages to file")

        elif action == "clear":
            history = []
            try:
                if path.exists():
                    path.unlink()
                    print(f"[ApoStudio History] Cleared session file")
            except Exception as e:
                print(f"[ApoStudio History] Clear error: {e}")

        elif action == "save":
            history = incoming
            if history:
                _save(path, history)
                print(f"[ApoStudio History] Saved {len(history)} messages")

        else:
            history = incoming

        raw_json   = json.dumps(history, indent=2, ensure_ascii=False) if history else "[]"
        markdown   = _to_markdown(history)
        turn_count = sum(1 for m in history if m.get("role") == "assistant")
        return (history, raw_json, markdown, turn_count)
