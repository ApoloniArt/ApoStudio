"""
ApoStudio — ComfyUI custom node package
"""

import importlib
import subprocess
import sys
import os

def _ensure(package: str, import_name=None):
    name = import_name or package
    try:
        importlib.import_module(name)
    except ImportError:
        print(f"[ApoStudio] Installing: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

_ensure("requests")
_ensure("Pillow", "PIL")

from .nodes.apo_chat       import ApoStudioChat
from .nodes.apo_prompts    import ApoStudioUserPrompt, ApoStudioSystemPrompt
from .nodes.apo_unload     import ApoStudioUnloadModels
from .nodes.apo_history    import ApoStudioHistory
from .nodes.apo_display    import ApoStudioDisplay
from .nodes.apo_load_image import ApoStudioLoadImage

NODE_CLASS_MAPPINGS = {
    "ApoStudio_Chat":         ApoStudioChat,
    "ApoStudio_UserPrompt":   ApoStudioUserPrompt,
    "ApoStudio_SystemPrompt": ApoStudioSystemPrompt,
    "ApoStudio_UnloadModels": ApoStudioUnloadModels,
    "ApoStudio_History":      ApoStudioHistory,
    "ApoStudio_Display":      ApoStudioDisplay,
    "ApoStudio_LoadImage":    ApoStudioLoadImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ApoStudio_Chat":         "ApoStudio Chat",
    "ApoStudio_UserPrompt":   "ApoStudio User Prompt",
    "ApoStudio_SystemPrompt": "ApoStudio System Prompt",
    "ApoStudio_UnloadModels": "ApoStudio Unload Models",
    "ApoStudio_History":      "ApoStudio History",
    "ApoStudio_Display":      "ApoStudio Display",
    "ApoStudio_LoadImage":    "ApoStudio Load Image",
}

# WEB_DIRECTORY tells ComfyUI to serve files from this folder as static assets.
# The JS at web/js/apo_display.js will be served and auto-loaded by ComfyUI.
WEB_DIRECTORY = "web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]

print("[ApoStudio] Loaded — 7 nodes registered.")
