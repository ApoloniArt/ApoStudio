<h1 align="center">𝔸𝕡𝕠𝕊𝕥𝕦𝕕𝕚𝕠</h1>
<p align="center"><b>ComfyUI custom node package for LLM-powered workflows.</b></p>

<p align="center">
  <a href="https://github.com/comfyanonymous/ComfyUI"><img alt="ComfyUI extension" src="https://img.shields.io/badge/ComfyUI-Extension-5ea500?style=flat"></a>
  <a href="https://github.com/ApoloniArt/ApoStudio/releases"><img alt="Version" src="https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fraw.githubusercontent.com%2Fapoloniart%2FApoStudio%2Fmain%2Fpyproject.toml&query=%24.project.version&label=Version&color=ed7d31&style=flat"></a>
  <a href="https://github.com/ApoloniArt/ApoStudio/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/apoloniart/ApoStudio?label=License&color=e0414a&style=flat"></a>
  <a href="https://github.com/ApoloniArt/ApoStudio/blob/main/requirements.txt"><img alt="Dependencies" src="https://img.shields.io/badge/Dependencies-2-0075c2?style=flat"></a>
  <a href="https://github.com/ApoloniArt/ApoStudio/commits"><img alt="Last update" src="https://img.shields.io/github/last-commit/apoloniart/ApoStudio?label=Last%20Update&color=ed7d31&style=flat"></a>
  <a href="https://github.com/ApoloniArt/ApoStudio/commits"><img alt="Activity" src="https://img.shields.io/github/commit-activity/m/apoloniart/ApoStudio?label=Activity&color=d4b300&style=flat"></a>
  <a href="https://github.com/ApoloniArt/ApoStudio/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/apoloniart/ApoStudio?logo=github&color=555&style=flat"></a>
  <a href="https://discord.gg/XDExAUzuZp"><img alt="Discord" src="https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white&style=flat"></a>
  <a href="https://github.com/ApoloniArt"><img alt="Follow on GitHub" src="https://img.shields.io/github/followers/ApoloniArt?label=Follow&logo=github&color=555&style=flat"></a>
  <a href="https://ko-fi.com/apoloniart"><img alt="Ko-fi" src="https://img.shields.io/badge/Ko--fi-Support-F16061?logo=ko-fi&logoColor=white&style=flat"></a>
</p>

Chat, prompt enhancement, image captioning, and multi-turn conversation via any **OpenAI-compatible** server — LM Studio, Unsloth Studio, Ollama, OpenAI API, and more.

![ApoStudio Node Collection](assets/screenshots/ApoStudio-Nodes.jpg)

---

## Finding ApoStudio Nodes

Double-click the ComfyUI canvas and search **"apo"** to find all nodes instantly.

![Finding ApoStudio Nodes](assets/screenshots/ApoStudio-Search.jpg)

---

## Example Workflows

### Chat with Context Memory
Full multi-turn conversation with persistent history across workflow runs.

![ApoStudio Chat v1 with Context Memory](assets/screenshots/ApoStudio-Chatv1.jpg)

### Image Captioning
Single image captioning using a vision model.

![ApoStudio Image Caption v1](assets/screenshots/ApoStudio-ImageCaption.jpg)

---

## Node Reference

### ApoStudio Chat
The core node. Sends a prompt to your LLM server and returns the response. Handles text-only, vision, and multi-turn conversation depending on what is connected.

**Required inputs**
| Input | Type | Default | Notes |
|-------|------|---------|-------|
| `api_url` | STRING | `http://localhost:1234/v1` | OpenAI-compatible endpoint |
| `model` | STRING | `enter-model-id-here` | Exact model ID as shown in your server |
| `user_prompt` | STRING | _(empty)_ | Typed user message. Overridden if `user_prompt_in` is connected |
| `system_prompt` | STRING | _(empty)_ | Typed system prompt. Overridden if `system_prompt_in` is connected |
| `temperature` | FLOAT | 0.7 | 0.0 – 2.0. Higher = more creative, lower = more deterministic |
| `max_tokens` | INT | 2048 | Maximum response length |
| `top_p` | FLOAT | 0.95 | Nucleus sampling threshold |
| `top_k` | INT | 40 | Top-K sampling |
| `min_p` | FLOAT | 0.05 | Minimum probability threshold |
| `repeat_penalty` | FLOAT | 1.1 | Penalises repetition. 1.0 = off |
| `seed` | INT | -1 | -1 = random each run |

**Optional inputs**
| Input | Type | Notes |
|-------|------|-------|
| `user_prompt_in` | STRING | From User Prompt node — overrides typed text |
| `system_prompt_in` | STRING | From System Prompt node — overrides typed text |
| `history_in` | APO_HISTORY | Conversation history from a History node (load action) |
| `image` | IMAGE | Connect any IMAGE for vision/captioning tasks |

**Outputs**
| Output | Type | Notes |
|--------|------|-------|
| `response` | STRING | The LLM's reply text |
| `full_context` | STRING | Full message array sent to API as JSON — useful for debugging |
| `history_out` | APO_HISTORY | Updated conversation history — wire to History node (load & append) |
| `elapsed_seconds` | FLOAT | Response time in seconds |
| `token_usage` | STRING | `prompt: X  completion: Y  total: Z` |

**API key (optional)**
Some servers need an API key, for example Unsloth Studio when it has to load a model on request. The key is deliberately **not** a node input: ComfyUI saves widget values inside workflow files and generated images, so a key typed into a node would leak whenever you share them. Instead, either:
- create a plain text file named `api_key.txt` inside the `ComfyUI-ApoStudio` folder and paste the key as its only line, or
- set the `APOSTUDIO_API_KEY` (or `UNSLOTH_API_KEY`) environment variable.

If no key is found, nothing is sent, so keyless servers such as LM Studio work exactly as before. Keep your key private and never upload or share `api_key.txt`.

If the server returns an error, the node now shows the server's own error message in `response`. The Chat node also remembers which `model` it asked for, so the Unload node can unload it automatically.

**Supported input combinations**

| What you connect | What happens |
|-----------------|--------------|
| User prompt only | Sends as a plain user message |
| System prompt only | Model responds to the system prompt directly |
| Both prompts | System sets context/role, user carries the request |
| Image only | Model describes the image |
| Image + user text | Image with a specific instruction |
| Image + system prompt | System sets role, image is the user message |
| All three | Full vision task with role, instruction, and image |

---

### ApoStudio User Prompt
File picker for user prompts. Reads `.txt`, `.md`, and `.json` files from the `prompts/user/` folder inside the package directory. Drop your own files into that folder — the dropdown refreshes automatically on every run without restarting ComfyUI.

For `.json` files, the node extracts the value of the first matching key it finds: `prompt`, `user_prompt`, `content`, `text`, or `message`. If none match, the full JSON is returned as a string.

**Input:** `file` dropdown  
**Output:** `user_prompt` STRING → wire to Chat's `user_prompt_in`

**Tip:** Leave the Chat node's `user_prompt` text area empty when using this node — the connected input takes priority automatically.

---

### ApoStudio System Prompt
Identical to User Prompt but reads from `prompts/system/`. Use this to load different roles and personas without retyping them.

Ships with three ready-to-use system prompts:
- **`assistant.txt`** — general-purpose helpful assistant
- **`vision_captioner.txt`** — detailed image analysis for captioning and description tasks
- **`prompt_enhancer.txt`** — expands rough ideas into full, detailed diffusion model prompts

**Input:** `file` dropdown  
**Output:** `system_prompt` STRING → wire to Chat's `system_prompt_in`

---

### ApoStudio History
Manages multi-turn conversation history by reading from and writing to a JSON session file on disk. Because ComfyUI cannot loop data within a single run, history is persisted between runs via the file system.

**How it works:** One History node loads the previous session at the start of each run. Another History node saves the updated session after Chat completes. Both nodes point to the same session file.

**Inputs**
| Input | Type | Notes |
|-------|------|-------|
| `action` | Dropdown | See actions table below |
| `session_file` | STRING | Full path to your session JSON file, e.g. `C:/chats/session.json` |
| `history_in` | APO_HISTORY | Wire Chat's `history_out` here on the save-side node |

**Actions**
| Action | Which node | What it does |
|--------|-----------|--------------|
| `load` | Left node (before Chat) | Reads history from the session file and outputs it to Chat's `history_in` |
| `load & append` | Right node (after Chat) | Receives Chat's `history_out`, saves the full updated conversation to the session file |
| `clear` | Either node | Deletes the session file and resets history to empty. Run once then switch back |
| `save` | Either node | Manually saves incoming history to the session file without loading |

**Outputs**
| Output | Type | Notes |
|--------|------|-------|
| `history_out` | APO_HISTORY | Wire left node's output to Chat's `history_in` |
| `history_json` | STRING | Full conversation as raw JSON — wire to Display for debugging |
| `history_md` | STRING | Full conversation formatted as readable Markdown — wire to Display for reading |
| `turn_count` | INT | Number of completed assistant replies in the current session |

**Wiring for multi-turn chat:**
```
[History: load] ──history_out──► Chat (history_in)
                                  Chat (history_out) ──► [History: load & append]
                                  Chat (response) ──► Display
                [History: load & append] ──history_md──► Display (full conversation)
```

**Starting a fresh conversation:** Switch the right History node action to `clear`, run once, then switch back to `load & append`. The session file will be deleted and history resets.

**Important:** Both History nodes must point to the exact same `session_file` path.

---

### ApoStudio Unload Models
Frees VRAM at the end of a workflow run. Works with **LM Studio** (via its CLI, `lms unload --all`) and **Unsloth Studio** (via its API). Wire it after your Chat node to automatically free VRAM when the workflow finishes. Use the execute toggle to quickly disable it without disconnecting anything.

**Inputs**
| Input | Type | Notes |
|-------|------|-------|
| `execute` | BOOLEAN | `Unload on Run` / `Skip` — toggle off when iterating quickly |
| `server` | Dropdown | `LM Studio (lms CLI)` (default) or `Unsloth Studio` |
| `api_url` | STRING | Unsloth Studio only. Default `http://127.0.0.1:8888/v1` |
| `model` | STRING | Unsloth Studio only. **Leave empty** to unload the model(s) the Chat node used since the last unload — when you switch models you only change the Chat node's `model`. Type a model name to unload that one instead |
| `trigger_in` | STRING (optional) | Wire Chat's `response` here to ensure it runs after Chat completes |

**Outputs**
| Output | Type | Notes |
|--------|------|-------|
| `status` | STRING | Result message — wire to Display to confirm unload |
| `trigger_out` | STRING | Passes `trigger_in` through — wire to Display to close the execution chain |

**Wiring:**
```
Chat (response) ──► Unload (trigger_in) ──trigger_out──► Display
```

> **Notes:** The `LM Studio` option requires the LM Studio CLI (`lms`) installed and available on your system PATH. The `Unsloth Studio` option uses Studio's API and sends your API key if you have set one (see [Using Unsloth Studio](#using-unsloth-studio)). If you restart ComfyUI while a model is still loaded and leave `model` empty, the node has to ask Studio what is loaded, which can be slow on installs with many models — type the model name in that case.

---

### ApoStudio Display
Universal display node. Accepts any input type and renders it as readable text directly in the node body after each run. Replaces the need for third-party Show Any nodes within ApoStudio workflows.

Wire any output from any node into `anything` — STRING, FLOAT, INT, APO_HISTORY, lists, or dicts are all handled. Lists and dicts are formatted as readable JSON automatically.

**Input:** `anything` — accepts any type  
**Output:** `text` STRING — passes the displayed text downstream for chaining

---

### ApoStudio Load Image
Image loader with a file picker for your ComfyUI `input/` directory. Supports jpg, jpeg, png, webp, bmp, tiff, and gif (first frame only). Includes EXIF orientation auto-correction so rotated phone photos load upright.

**Input:** `image` dropdown + "choose file to upload" button  
**Outputs**
| Output | Type | Notes |
|--------|------|-------|
| `image` | IMAGE | Tensor ready to wire into Chat's `image` input |
| `mask` | MASK | Alpha channel as mask, or solid white if no alpha |
| `width` | INT | Image width in pixels |
| `height` | INT | Image height in pixels |
| `filename` | STRING | Base filename of the loaded image |

---

## ⚙️ Installation

1. ### **<ins>Comfy Manager Install [recommended]:</ins>**
   My nodes have absolute minimal requirements, so you can confidently & safely install via Comfy Manager, without the fear of dependencies breaking your entire Comfy. Search **APO** in manager. After installation, rename the folder to **ComfyUI-ApoStudio**

2. ### **<ins>Manual Install [git clone]:</ins>**
   ```bash
   cd ComfyUI/custom_nodes
   git clone https://github.com/ApoloniArt/ApoStudio ComfyUI-ApoStudio
   ```
3. Install dependencies:
   ```bash
   # Windows portable:
   python -m pip install -r ComfyUI-ApoStudio\requirements.txt

   # Standard install:
   pip install -r ComfyUI-ApoStudio\requirements.txt
   ```  
4. Restart ComfyUI.
5. All 7 nodes appear under the **ApoStudio** category. Search **"apo"** in the node finder to see them all.
   
6. Updating my nodes:
 ```bash
   cd ComfyUI/custom_nodes/ComfyUI-ApoStudio
   git pull
   ```

---

## ✍🏻 Adding your own prompt files

Drop `.txt`, `.md`, or `.json` files into:
- `prompts/user/` — for user prompts
- `prompts/system/` — for system prompts

Files appear in the dropdown on the next workflow run. No restart needed.

**JSON format:** Any JSON file with one of these keys will have its value extracted automatically: `prompt`, `user_prompt`, `system_prompt`, `content`, `text`, `message`.

---

## 🖥️ Server compatibility

| Server | Default URL |
|--------|------------|
| LM Studio | `http://localhost:1234/v1` |
| Unsloth Studio | `http://127.0.0.1:8888/v1` |
| Ollama | `http://localhost:11434/v1` |
| OpenAI API | `https://api.openai.com/v1` |
| LiteLLM / vLLM / text-generation-webui | Set your own URL |

> The **Unload Models** node supports LM Studio (CLI) and Unsloth Studio (API). All other nodes work with any OpenAI-compatible server.

### Using Unsloth Studio
1. In Unsloth Studio, open **Settings → API**, create an API key, and turn on **Model auto-switch** so Studio loads the model named in the Chat node when it is requested.
2. Save the key in `api_key.txt` (see [API key](#apostudio-chat) under the Chat node). Never type it into a node.
3. Set the Chat node's `api_url` to `http://127.0.0.1:8888/v1` and `model` to a model id from Studio's model list, e.g. `unsloth/gemma-4-12b-it-GGUF`.
4. Set the Unload node's `server` to `Unsloth Studio` and leave its `model` empty.
5. Switching to another model later only needs a new `model` in the Chat node. Each model loads with the run settings saved for it in Studio, so set those once per model.

---

## 📂 File structure

```
ApoStudio/
├── __init__.py                      ← Package entry point, node registration
├── requirements.txt                 ← pip dependencies (requests, Pillow)
├── pyproject.toml                   ← ComfyUI Registry metadata
├── README.md                        ← This file
├── CHANGELOG.md                     ← Version history
├── LICENSE                          ← MIT licence
├── .gitignore                       ← Keeps your private api_key.txt out of git
├── assets/
│   └── screenshots/
│       ├── ApoStudio-Nodes.jpg      ← Node collection overview
│       ├── ApoStudio-Chatv1.jpg     ← Chat workflow with context memory
│       ├── ApoStudio-ImageCaption.jpg ← Image captioning workflow
│       └── ApoStudio-Search.jpg     ← How to find nodes in ComfyUI
├── nodes/
│   ├── __init__.py                  ← Package marker
│   ├── apo_chat.py                  ← ApoStudio Chat
│   ├── apo_auth.py                  ← Optional API key loading (api_key.txt / env var)
│   ├── apo_state.py                 ← Remembers which model Chat used (for Unload)
│   ├── apo_history.py               ← ApoStudio History
│   ├── apo_prompts.py               ← ApoStudio User Prompt & System Prompt
│   ├── apo_unload.py                ← ApoStudio Unload Models
│   ├── apo_display.py               ← ApoStudio Display
│   └── apo_load_image.py            ← ApoStudio Load Image
├── prompts/
│   ├── user/
│   │   ├── describe_image.txt       ← Example: image description prompt
│   │   └── enhance_prompt.txt       ← Example: diffusion prompt enhancer
│   └── system/
│       ├── assistant.txt            ← General-purpose assistant
│       ├── vision_captioner.txt     ← Image analysis and captioning
│       └── prompt_enhancer.txt      ← Diffusion model prompt expansion
└── web/
    └── js/
        └── apo_display.js           ← Frontend JS for Display node rendering
```

## 🫱🏻‍🫲🏻 Attribution & Licenses
**ApoStudio** is MIT licensed, see [LICENSE](https://github.com/ApoloniArt/ApoStudio/blob/main/LICENSE). If you use it in a project, a mention of "ApoStudio by ApoloniArt" is very much appreciated 🤗

See [NOTICE](https://github.com/ApoloniArt/ApoStudio/blob/main/NOTICE) for the full attribution request.

---

<div align="center">

**Developed by [ApoloniArt ⚢🌈](https://github.com/ApoloniArt)**

[![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/XDExAUzuZp)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/apoloniart)

</div>

