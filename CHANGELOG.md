# Changelog

---

## [1.1.0] — 2026-05-26

### Added
- **ApoStudio Display** — universal display node using AnyType input and ComfyUI's native `ComfyWidgets["STRING"]` renderer. Accepts any input type (STRING, FLOAT, INT, APO_HISTORY, list, dict). Renders text directly in the node body after each run. Uses `/scripts/app.js` and `/scripts/widgets.js` via a frontend JS extension (`web/js/apo_display.js`). Returns text as STRING output for downstream chaining.
- **ApoStudio Load Image** — image loader using ComfyUI's native `folder_paths` and `image_upload` widget. Shows "choose file to upload" button with dropdown of all images in the ComfyUI input directory. Supports jpg, jpeg, png, webp, bmp, tiff, gif (first frame). EXIF orientation auto-corrected. Outputs IMAGE tensor, MASK (alpha or solid white), width, height, filename. MD5 hash used for IS_CHANGED so ComfyUI detects file swaps even with the same filename.
- **`web/` directory** — frontend JS served via `WEB_DIRECTORY = "web"` in `__init__.py`
- **`assets/screenshots/`** — workflow and node reference screenshots for documentation

### Changed
- `__init__.py` updated to register 7 nodes and serve the web directory
- `CHANGELOG.md` and `README.md` fully rewritten to reflect all 7 nodes with thorough explanations, wiring diagrams, and screenshot placeholders

---

## [1.0.0] — 2026-05-19

### Initial release — 5 nodes

**ApoStudio Chat**
- Core LLM node supporting text, vision, and multi-turn conversation
- Full parameter control: temperature, max_tokens, top_p, top_k, min_p, repeat_penalty, seed
- Optional inputs: user_prompt_in, system_prompt_in, history_in (APO_HISTORY), image (IMAGE)
- Outputs: response, full_context, history_out, elapsed_seconds, token_usage
- Handles all input combinations: text only, system only, both, image only, image + text, image + system, all three
- Works with any OpenAI-compatible server (LM Studio, Ollama, OpenAI, LiteLLM, vLLM)

**ApoStudio User Prompt**
- File picker reading .txt, .md, .json from `prompts/user/`
- IS_CHANGED forces refresh every run — new files appear without restart
- JSON files: extracts value of first matching key (prompt, user_prompt, content, text, message)

**ApoStudio System Prompt**
- Identical to User Prompt, reads from `prompts/system/`
- Ships with: assistant.txt, vision_captioner.txt, prompt_enhancer.txt

**ApoStudio History**
- File-based conversation persistence across workflow runs
- Actions: load, load & append, clear, save
- Outputs: history_out (APO_HISTORY), history_json (STRING), history_md (STRING), turn_count (INT)
- Markdown output formats conversation as readable ### User / ### Assistant sections
- IS_CHANGED forces re-read from disk every run so history accumulates correctly

**ApoStudio Unload Models**
- Uses LM Studio CLI: `lms unload --all`
- execute toggle (Unload on Run / Skip) for quick on/off without rewiring
- trigger_in / trigger_out passthrough enforces execution after Chat completes
- OUTPUT_NODE = True ensures it always executes when present in the graph

---

## GitHub Actions publish workflow

Add this file as `.github/workflows/publish.yml` to auto-publish to the ComfyUI Registry when you bump the version in `pyproject.toml`:

```yaml
name: Publish to Comfy Registry

on:
  workflow_dispatch:
  push:
    branches:
      - main
    paths:
      - "pyproject.toml"

jobs:
  publish-node:
    name: Publish Custom Node to registry
    runs-on: ubuntu-latest
    steps:
      - name: Check out code
        uses: actions/checkout@v4
      - name: Publish Custom Node
        uses: Comfy-Org/publish-node-action@main
        with:
          personal_access_token: ${{ secrets.REGISTRY_ACCESS_TOKEN }}
```
