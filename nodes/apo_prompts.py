import json
import pathlib


def _get_prompt_dir(subdir: str) -> pathlib.Path:
    base = pathlib.Path(__file__).parent.parent / "prompts" / subdir
    base.mkdir(parents=True, exist_ok=True)
    return base


def _list_files(subdir: str):
    d = _get_prompt_dir(subdir)
    files = sorted(
        f.name for f in d.iterdir()
        if f.is_file() and f.suffix.lower() in {".txt", ".md", ".json"}
    )
    return files if files else ["(no files found)"]


def _read_file(subdir: str, filename: str) -> str:
    if filename == "(no files found)":
        return ""
    path = _get_prompt_dir(subdir) / filename
    if not path.exists():
        return f"ERROR: File not found — {path}"
    try:
        raw = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            try:
                data = json.loads(raw)
                for key in ("prompt", "user_prompt", "system_prompt", "content", "text", "message"):
                    if key in data and isinstance(data[key], str):
                        return data[key].strip()
                return json.dumps(data, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                return raw.strip()
        return raw.strip()
    except Exception as e:
        return f"ERROR reading file: {e}"


class ApoStudioUserPrompt:
    CATEGORY = "ApoStudio"
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file": (_list_files("user"), {}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("user_prompt",)

    def run(self, file):
        return (_read_file("user", file),)


class ApoStudioSystemPrompt:
    CATEGORY = "ApoStudio"
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file": (_list_files("system"), {}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("nan")

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("system_prompt",)

    def run(self, file):
        return (_read_file("system", file),)
