body = {
    # ===== Required =====
    "mode": "text-to-image",          # "text-to-image" | "image-to-image" | "inpainting"
    "prompt": "<YOUR_PROMPT_HERE>",

    # ===== Negative Prompting =====
    "negative_prompt": "<WHAT_YOU_DO_NOT_WANT>",

    # ===== Image Size / Aspect =====
    "width": 1024,                    # Typical: 512 | 768 | 1024
    "height": 1024,

    # ===== Sampling / Diffusion =====
    "steps": 40,                      # Typical: 20–50
    "cfg_scale": 7.5,                 # Prompt adherence (aka guidance scale)
    "sampler": "dpmpp_2m",            # e.g. "euler", "euler_a", "dpmpp_2m", "dpmpp_sde"
    "scheduler": "karras",            # e.g. "karras", "normal"

    # ===== Seed Control =====
    "seed": 123456789,                # Use -1 or omit for random
    "subseed": 987654321,
    "subseed_strength": 0.2,

    # ===== Batch / Variations =====
    "n_images": 1,                    # Number of images returned
    "variation_strength": 0.0,        # >0 for prompt-based variation

    # ===== Style / Aesthetics =====
    "style_preset": "photographic",   # e.g. photographic, cinematic, anime, 3d-model
    "clip_skip": 1,                   # Advanced prompt behavior

    # ===== Advanced Prompt Weights =====
    "prompt_weights": {
        "enabled": False,
        "weights": {}
    },

    # ===== Image-to-Image / Inpainting =====
    # (Only used if mode != text-to-image)
    "init_image": "<BASE64_IMAGE>",    # Base64-encoded input image
    # How much to transform input image (0–1)
    "strength": 0.6,

    # ===== Masking (Inpainting) =====
    "mask_image": "<BASE64_MASK>",     # White = replace, black = keep
    "mask_blur": 4,

    # ===== Safety / Filtering =====
    "safety_check": True,

    # ===== Metadata / Debug =====
    "output_format": "png",            # png | jpeg | webp
    "return_metadata": False
}

