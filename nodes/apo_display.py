import json

any_type = type("AnyType", (str,), {"__ne__": lambda self, o: False})
ANY = any_type("*")


class ApoStudioDisplay:
    CATEGORY = "ApoStudio"
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {"anything": (ANY, {})},
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def VALIDATE_INPUTS(cls, **kwargs):
        return True

    def run(self, unique_id=None, extra_pnginfo=None, anything=None, **kwargs):
        if anything is None:
            text = ""
        elif isinstance(anything, str):
            text = anything
        elif isinstance(anything, (list, dict)):
            try:
                text = json.dumps(anything, indent=2, ensure_ascii=False)
            except Exception:
                text = str(anything)
        else:
            text = str(anything)

        # Save text into workflow JSON for persistence on reload
        if unique_id and extra_pnginfo and isinstance(extra_pnginfo, list):
            for info in extra_pnginfo:
                if isinstance(info, dict) and "workflow" in info:
                    for node in info["workflow"].get("nodes", []):
                        if str(node.get("id")) == str(unique_id):
                            node["widgets_values"] = [text]
                            break

        return {"ui": {"text": [text]}, "result": (text,)}
