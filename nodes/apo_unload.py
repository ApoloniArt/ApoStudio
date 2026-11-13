import subprocess
import sys

import requests

from .apo_auth import build_headers
from .apo_state import take_models, restore_models

SERVERS = ["LM Studio", "Unsloth Studio"]


def _base_url(api_url):
    url = (api_url or "").strip().rstrip("/")
    if url.endswith("/v1"):
        url = url[:-3]
    return url


class ApoStudioUnloadModels:
    CATEGORY = "ApoStudio"
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "execute": ("BOOLEAN", {"default": True, "label_on": "Unload on Run", "label_off": "Skip"}),
                "server": (SERVERS, {"default": SERVERS[0]}),
                "api_url": ("STRING", {"default": "http://127.0.0.1:8888/v1", "multiline": False}),
                "model": ("STRING", {"default": "", "multiline": False, "tooltip": "Leave empty: unloads the model(s) the Chat node used (Unsloth Studio)."}),
            },
            "optional": {
                # Wire Chat node's response here — guarantees it runs AFTER response is delivered
                "trigger_in": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("status", "trigger_out",)

    def run(self, execute, server=SERVERS[0], api_url="http://127.0.0.1:8888/v1",
            model="", trigger_in=None):
        if not execute:
            return ("Skipped — unload disabled.", trigger_in or "",)

        if server == "Unsloth Studio":
            status = self._unload_unsloth(api_url, model)
        else:
            status = self._unload_lmstudio()
        return (status, trigger_in or "",)

    @staticmethod
    def _post_unload(base, model_id):
        r = requests.post(f"{base}/api/inference/unload", headers=build_headers(),
                          json={"model_path": model_id}, timeout=120)
        if not r.ok:
            return f"{r.status_code} {r.reason}: {(r.text or '').strip()[:300]}"
        return None

    @staticmethod
    def _list_loaded(base):
        """Fallback only: loaded chat/vision models reported by Studio (can be slow)."""
        r = requests.get(f"{base}/v1/models", headers=build_headers(), timeout=90)
        r.raise_for_status()
        return [m["id"] for m in r.json().get("data", [])
                if m.get("loaded") and not m.get("task") and m.get("id")]

    @staticmethod
    def _unload_unsloth(api_url, model):
        """Which model to unload, in order of priority:
        1. the `model` box, if you typed one
        2. the model(s) the Chat node asked for since the last unload (automatic)
        3. fallback: ask Studio what is loaded (used e.g. after restarting ComfyUI)
        """
        base = _base_url(api_url)
        model = (model or "").strip()
        if model:
            targets, taken = [model], []
        else:
            taken = take_models()
            targets = list(taken)
        try:
            if not targets:
                try:
                    targets = ApoStudioUnloadModels._list_loaded(base)
                except requests.exceptions.Timeout:
                    return "ERROR: Studio did not answer the 'what is loaded' question in time. Type the model name into this node instead."
                if not targets:
                    return "No model is loaded - nothing to unload."
                targets = targets[:1] if len(targets) > 1 else targets
            done, errors, failed = [], [], []
            for t in targets:
                try:
                    err = ApoStudioUnloadModels._post_unload(base, t)
                except requests.exceptions.Timeout:
                    err = "timed out"
                if err:
                    errors.append(f"{t}: {err}")
                    failed.append(t)
                else:
                    done.append(t)
            restore_models(failed)
            if errors:
                return "ERROR: " + " | ".join(errors) + (("  (unloaded: " + ", ".join(done) + ")") if done else "")
            return "unloaded: " + ", ".join(done)
        except requests.exceptions.ConnectionError:
            restore_models(taken)
            return f"ERROR: Cannot connect to {base}."
        except Exception as e:
            restore_models(taken)
            return f"ERROR: {e}"

    @staticmethod
    def _unload_lmstudio():
        command = "lms.exe" if sys.platform == "win32" else "lms"
        try:
            result = subprocess.run(
                [command, "unload", "--all"],
                check=True, text=True, capture_output=True
            )
            return result.stdout.strip() or "All models unloaded successfully."
        except FileNotFoundError:
            return f"ERROR: '{command}' not found — is LM Studio CLI installed and on PATH?"
        except subprocess.CalledProcessError as e:
            return f"ERROR: {e.stderr.strip() or str(e)}"
        except Exception as e:
            return f"ERROR: {e}"
