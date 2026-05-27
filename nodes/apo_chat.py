import requests
import base64
import json
import time
import io
import numpy as np


def tensor_to_base64(tensor):
    from PIL import Image
    arr = (tensor.squeeze(0).cpu().numpy() * 255).clip(0, 255).astype(np.uint8)
    pil = Image.fromarray(arr)
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


class ApoStudioChat:
    CATEGORY = "ApoStudio"
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_url":        ("STRING",  {"default": "http://localhost:1234/v1", "multiline": False}),
                "model":          ("STRING",  {"default": "enter-model-id-here",      "multiline": False}),
                "user_prompt":    ("STRING",  {"default": "",  "multiline": True}),
                "system_prompt":  ("STRING",  {"default": "",  "multiline": True}),
                "temperature":    ("FLOAT",   {"default": 0.7,  "min": 0.0,  "max": 2.0,   "step": 0.05}),
                "max_tokens":     ("INT",     {"default": 2048, "min": 128,  "max": 32000,  "step": 128}),
                "top_p":          ("FLOAT",   {"default": 0.95, "min": 0.0,  "max": 1.0,   "step": 0.01}),
                "top_k":          ("INT",     {"default": 40,   "min": 0,    "max": 200,    "step": 1}),
                "min_p":          ("FLOAT",   {"default": 0.05, "min": 0.0,  "max": 1.0,   "step": 0.01}),
                "repeat_penalty": ("FLOAT",   {"default": 1.1,  "min": 1.0,  "max": 2.0,   "step": 0.05}),
                "seed":           ("INT",     {"default": -1,   "min": -1,   "max": 2**31 - 1}),
            },
            "optional": {
                "user_prompt_in":   ("STRING", {"forceInput": True}),
                "system_prompt_in": ("STRING", {"forceInput": True}),
                "history_in":       ("APO_HISTORY",),
                "image":            ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "APO_HISTORY", "FLOAT", "STRING")
    RETURN_NAMES = ("response", "full_context", "history_out", "elapsed_seconds", "token_usage")

    def run(
        self,
        api_url, model,
        user_prompt, system_prompt,
        temperature, max_tokens, top_p, top_k, min_p, repeat_penalty, seed,
        user_prompt_in=None, system_prompt_in=None,
        history_in=None, image=None,
    ):
        final_user   = (user_prompt_in   or "").strip() or user_prompt.strip()
        final_system = (system_prompt_in or "").strip() or system_prompt.strip()

        if not final_user and not final_system and image is None:
            return ("ERROR: Nothing to send — provide a user prompt, system prompt, or image.", "", [], 0.0, "")

        api_url = api_url.rstrip("/")
        history = list(history_in) if history_in else []

        if image is not None:
            img_b64 = tensor_to_base64(image)
            content_parts = [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}]
            if final_user:
                content_parts.append({"type": "text", "text": final_user})
            history.append({"role": "user", "content": content_parts})
        elif final_user:
            history.append({"role": "user", "content": final_user})

        messages = []
        if final_system:
            messages.append({"role": "system", "content": final_system})
        messages.extend(history)

        params = {
            "model": model, "messages": messages, "temperature": temperature,
            "max_tokens": max_tokens, "top_p": top_p, "top_k": top_k,
            "repeat_penalty": repeat_penalty, "stream": False,
        }
        if min_p > 0: params["min_p"] = min_p
        if seed >= 0: params["seed"]  = seed

        try:
            start = time.perf_counter()
            r = requests.post(f"{api_url}/chat/completions",
                              headers={"Content-Type": "application/json"},
                              json=params, timeout=300)
            elapsed = round(time.perf_counter() - start, 3)
            r.raise_for_status()
            data = r.json()
        except requests.exceptions.ConnectionError:
            return (f"ERROR: Cannot connect to {api_url}.", "", [], 0.0, "")
        except requests.exceptions.Timeout:
            return ("ERROR: Request timed out (300s).", "", [], 0.0, "")
        except Exception as e:
            return (f"ERROR: {e}", "", [], 0.0, "")

        try:
            response_text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            return (f"ERROR: Unexpected API response: {e}\n{json.dumps(data)}", "", [], elapsed, "")

        history.append({"role": "assistant", "content": response_text})

        usage          = data.get("usage", {})
        prompt_tok     = usage.get("prompt_tokens",     0)
        completion_tok = usage.get("completion_tokens", 0)
        total_tok      = usage.get("total_tokens",      prompt_tok + completion_tok)
        token_usage    = f"prompt: {prompt_tok}  completion: {completion_tok}  total: {total_tok}"
        full_context   = json.dumps(messages, indent=2, ensure_ascii=False)

        return (response_text, full_context, history, elapsed, token_usage)
