import torch
import numpy as np
import os
import hashlib
import folder_paths
from PIL import Image, ImageOps


class ApoStudioLoadImage:
    CATEGORY = "ApoStudio"
    FUNCTION = "run"

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = sorted([
            f for f in os.listdir(input_dir)
            if os.path.isfile(os.path.join(input_dir, f))
            and f.lower().split(".")[-1] in {"jpg", "jpeg", "png", "webp", "bmp", "tiff", "tif", "gif"}
        ])
        return {
            "required": {
                # Tuple of files + {"image_upload": True} gives the native
                # ComfyUI "choose file to upload" button + dropdown
                "image": (sorted(files), {"image_upload": True}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK", "INT", "INT", "STRING")
    RETURN_NAMES = ("image", "mask", "width", "height", "filename")

    @classmethod
    def IS_CHANGED(cls, image):
        path = folder_paths.get_annotated_filepath(image)
        if os.path.exists(path):
            with open(path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        return float("nan")

    @classmethod
    def VALIDATE_INPUTS(cls, image):
        if not folder_paths.exists_annotated_filepath(image):
            return f"Invalid image file: {image}"
        return True

    def run(self, image):
        path = folder_paths.get_annotated_filepath(image)

        pil = Image.open(path)
        pil = ImageOps.exif_transpose(pil)

        # Extract alpha as mask
        if pil.mode == "RGBA":
            alpha = np.array(pil.getchannel("A")).astype(np.float32) / 255.0
            mask  = torch.from_numpy(alpha).unsqueeze(0)
        else:
            mask = torch.ones((1, pil.height, pil.width), dtype=torch.float32)

        pil_rgb = pil.convert("RGB")
        arr     = np.array(pil_rgb).astype(np.float32) / 255.0
        tensor  = torch.from_numpy(arr).unsqueeze(0)  # (1, H, W, C)

        w, h   = pil.size
        fname  = os.path.basename(path)
        print(f"[ApoStudio Load Image] {fname}  {w}×{h}")
        return (tensor, mask, w, h, fname)
