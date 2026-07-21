"""
backend.py — AI Thumbnail Agent (backend)

Uses Pollinations.ai's LEGACY endpoints — genuinely free, no signup, no API
key, no billing of any kind:
  - https://text.pollinations.ai   (prompt writing)
  - https://image.pollinations.ai  (thumbnail image generation)

These are separate from the newer "Pollen"-metered gen.pollinations.ai
system and don't require any account balance. Anonymous usage is
rate-limited to roughly one request every ~15 seconds, which is plenty for
generating thumbnails one at a time.

This file has NO Streamlit code in it — it's plain Python so it can be
imported by app.py (the frontend) or reused anywhere else (CLI, API, etc).
"""

import urllib.parse
from io import BytesIO

import requests
from PIL import Image

TEXT_URL = "https://text.pollinations.ai"
IMAGE_URL = "https://image.pollinations.ai/prompt"
IMAGE_MODEL = "flux"  # free, high-quality image model

ASPECT_RATIO_DIMENSIONS = {
    "16:9": (1280, 720),
    "9:16": (720, 1280),
    "1:1": (1024, 1024),
}


def build_thumbnail_prompt(topic: str, style: str, overlay_text: str, aspect_ratio: str) -> str:
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
        TEXT_URL,
        json={
            "messages": [{"role": "user", "content": instruction}],
            "model": "openai",
            "private": True,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.text.strip().strip('"')


def generate_thumbnail(prompt: str, width: int, height: int) -> Image.Image:
    """Generate a thumbnail image using Pollinations' free legacy image endpoint."""
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"{IMAGE_URL}/{encoded_prompt}"
    params = {"model": IMAGE_MODEL, "width": width, "height": height, "nologo": "true"}

    response = requests.get(url, params=params, timeout=90)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))


def _simple_prompt(topic: str, style: str, overlay_text: str, aspect_ratio: str) -> str:
    """Fallback prompt builder that needs no extra API call."""
    pieces = [topic.strip(), f"{style} YouTube thumbnail style", f"{aspect_ratio} aspect ratio"]
    if overlay_text.strip():
        pieces.append(f'bold readable text overlay reading "{overlay_text.strip()}"')
    return ", ".join(pieces)


def generate_full_thumbnail(topic: str, style: str = "Bold & Vibrant",
                             overlay_text: str = "", aspect_ratio: str = "16:9",
                             use_prompt_enhancer: bool = True):
    """
    End-to-end pipeline: topic -> (optionally enhanced) prompt -> generated image.

    Returns:
        (PIL.Image.Image, str) -> the generated image and the final prompt used
    """
    if use_prompt_enhancer:
        try:
            final_prompt = build_thumbnail_prompt(topic, style, overlay_text, aspect_ratio)
        except requests.exceptions.RequestException:
            # Prompt-enhancement is a nice-to-have. If it fails for any reason
            # (rate limit, temporary outage, etc.), fall back quietly instead
            # of breaking the whole generation.
            final_prompt = _simple_prompt(topic, style, overlay_text, aspect_ratio)
    else:
        final_prompt = _simple_prompt(topic, style, overlay_text, aspect_ratio)

    width, height = ASPECT_RATIO_DIMENSIONS.get(aspect_ratio, (1280, 720))
    image = generate_thumbnail(final_prompt, width, height)
    return image, final_prompt
