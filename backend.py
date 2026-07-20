"""
backend.py — AI Thumbnail Agent (backend)

Handles all AI logic using Pollinations.ai — a free, open-source generation
API (https://pollinations.ai). No billing account required.

  1. Turns a raw video topic into a detailed, thumbnail-optimized image prompt
     using a free text model.
  2. Generates the actual thumbnail image using a free image model (flux).

This file has NO Streamlit code in it — it's plain Python so it can be
imported by app.py (the frontend) or reused anywhere else (CLI, API, etc).
"""

import urllib.parse
from io import BytesIO

import requests
from PIL import Image

BASE_URL = "https://gen.pollinations.ai"
TEXT_MODEL = "openai"   # free text model, used to write the image prompt
IMAGE_MODEL = "flux"    # free image model (0 Pollen cost)

ASPECT_RATIO_DIMENSIONS = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "1:1": (1024, 1024),
}


def _headers(api_key: str) -> dict:
    """Build request headers. API key is optional (works anonymously too,
    but a free key from https://enter.pollinations.ai gives higher rate limits)."""
    if api_key and api_key.strip():
        return {"Authorization": f"Bearer {api_key.strip()}"}
    return {}


def build_thumbnail_prompt(api_key: str, topic: str, style: str,
                            overlay_text: str, aspect_ratio: str) -> str:
    """
    Ask a free text model to turn a raw topic into a rich, detailed
    image-generation prompt optimized for a high-CTR YouTube thumbnail.
    """
    instruction = f"""You are an expert YouTube thumbnail designer.
Write ONE detailed image-generation prompt (max 80 words, no preamble, no markdown, no quotes)
for a scroll-stopping YouTube thumbnail about: "{topic}"

Style: {style}
Aspect ratio: {aspect_ratio}
{f'The image must clearly render this exact text on it: "{overlay_text}"' if overlay_text.strip() else 'Do not put any text in the image.'}

Requirements:
- Bold, high-contrast colors, dramatic lighting, one strong focal subject
- Emotion or curiosity-driven composition (shock, excitement, intrigue)
- Leave clean visual space for text if text is required
- Describe subject, background, colors, lighting and camera angle
- Output ONLY the final image prompt text, nothing else"""

    response = requests.post(
        f"{BASE_URL}/text",
        headers={**_headers(api_key), "Content-Type": "application/json"},
        json={
            "messages": [{"role": "user", "content": instruction}],
            "model": TEXT_MODEL,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.text.strip().strip('"')


def generate_thumbnail(api_key: str, prompt: str, width: int, height: int) -> Image.Image:
    """Generate a thumbnail image from a prompt using a free Pollinations image model."""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{BASE_URL}/image/{encoded_prompt}"
    params = {"model": IMAGE_MODEL, "width": width, "height": height}

    response = requests.get(url, headers=_headers(api_key), params=params, timeout=90)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


def generate_full_thumbnail(api_key: str, topic: str, style: str = "Bold & Vibrant",
                             overlay_text: str = "", aspect_ratio: str = "16:9",
                             use_prompt_enhancer: bool = True):
    """
    End-to-end pipeline: topic -> (optionally enhanced) prompt -> generated image.

    Returns:
        (PIL.Image.Image, str) -> the generated image and the final prompt used
    """
    if use_prompt_enhancer:
        final_prompt = build_thumbnail_prompt(api_key, topic, style, overlay_text, aspect_ratio)
    else:
        pieces = [topic.strip(), f"{style} YouTube thumbnail style", f"{aspect_ratio} aspect ratio"]
        if overlay_text.strip():
            pieces.append(f'bold readable text overlay reading "{overlay_text.strip()}"')
        final_prompt = ", ".join(pieces)

    width, height = ASPECT_RATIO_DIMENSIONS.get(aspect_ratio, (1280, 720))
    image = generate_thumbnail(api_key, final_prompt, width, height)
    return image, final_prompt
