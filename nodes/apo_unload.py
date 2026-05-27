import subprocess
import sys


class ApoStudioUnloadModels:
    CATEGORY = "ApoStudio"
    FUNCTION = "run"
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "execute": ("BOOLEAN", {"default": True, "label_on": "Unload on Run", "label_off": "Skip"}),
            },
            "optional": {
                # Wire Chat node's response here — guarantees it runs AFTER response is delivered
                "trigger_in": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("status", "trigger_out",)

    def run(self, execute, trigger_in=None):
        if not execute:
            return ("Skipped — unload disabled.", trigger_in or "",)

        command = "lms.exe" if sys.platform == "win32" else "lms"
        try:
            result = subprocess.run(
                [command, "unload", "--all"],
                check=True, text=True, capture_output=True
            )
            status = result.stdout.strip() or "All models unloaded successfully."
        except FileNotFoundError:
            status = f"ERROR: '{command}' not found — is LM Studio CLI installed and on PATH?"
        except subprocess.CalledProcessError as e:
            status = f"ERROR: {e.stderr.strip() or str(e)}"
        except Exception as e:
            status = f"ERROR: {e}"

        return (status, trigger_in or "",)
