import io
import json
import os

from PIL import Image, ImageDraw, ImageFont, ImageOps

# ---------- Config ----------
W, H = 1280, 720
ASSETS = os.path.join(os.path.dirname(__file__), "assets")

MOODS = {
    "Shocking": {"bg": ["#2B0A0A", "#7A1616"], "text": "#FFF4E3", "stroke": "#0E0403", "accent": "#FF3D6E"},
    "Tutorial": {"bg": ["#071A2B", "#0F4C75"], "text": "#F5F1EA", "stroke": "#04101B", "accent": "#3DD6FF"},
    "Vlog": {"bg": ["#2B1B05", "#7A4E10"], "text": "#FFF4E3", "stroke": "#1A0F02", "accent": "#FFB020"},
    "Gaming": {"bg": ["#180229", "#4B0F7A"], "text": "#F5F1EA", "stroke": "#0D0116", "accent": "#B24DFF"},
    "Luxury": {"bg": ["#0E0D0B", "#2A2216"], "text": "#FFB020", "stroke": "#000000", "accent": "#FFB020"},
}

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def gradient_bg(color1, color2):
    img = Image.new("RGB", (W, H))
    px = img.load()
    c1, c2 = hex2rgb(color1), hex2rgb(color2)
    for y in range(H):
        t = y / H
        col = lerp_color(c1, c2, t)
        for x in range(0, W, 4):
            for dx in range(4):
                if x + dx < W:
                    px[x + dx, y] = col
    return img


def fit_cover(img, w, h):
    return ImageOps.fit(img, (w, h), method=Image.LANCZOS, centering=(0.5, 0.5))


def wrap_lines(draw, text, font, max_width):
    words = text.upper().split()
    lines, current = [], ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textlength(test, font=font) > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def round_rect(draw, xy, radius, fill):
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def render_thumbnail(title, tag, mood_name, position, overlay, bg_image_bytes):
    mood = MOODS[mood_name]

    if bg_image_bytes:
        base = Image.open(io.BytesIO(bg_image_bytes)).convert("RGB")
        canvas = fit_cover(base, W, H)
    else:
        canvas = gradient_bg(mood["bg"][0], mood["bg"][1])

    canvas = canvas.convert("RGBA")

    if overlay:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ov_px = ov.load()
        start_y = int(H * 0.35)
        for y in range(start_y, H):
            t = (y - start_y) / (H - start_y)
            alpha = int(184 * t)
            for x in range(0, W, 4):
                for dx in range(4):
                    if x + dx < W:
                        ov_px[x + dx, y] = (10, 8, 6, alpha)
        canvas = Image.alpha_composite(canvas, ov)

    draw = ImageDraw.Draw(canvas)

    # corner accent bar
    draw.rectangle([0, 0, 18, H], fill=hex2rgb(mood["accent"]))

    # tag pill
    if tag.strip():
        font_path = os.path.join(ASSETS, "Outfit-Bold.ttf")

try:
    tag_font = ImageFont.truetype(font_path, 30)
except OSError:
    tag_font = ImageFont.load_default()
        pad_x = 26
        tw = draw.textlength(tag.upper(), font=tag_font)
        pill_w, pill_h = tw + pad_x * 2, 58
        px, py = 56, 56
        round_rect(draw, [px, py, px + pill_w, py + pill_h], 12, hex2rgb(mood["accent"]))
        bbox = draw.textbbox((0, 0), tag.upper(), font=tag_font)
        th = bbox[3] - bbox[1]
        draw.text((px + pad_x, py + pill_h / 2 - th / 2 - bbox[1]), tag.upper(), font=tag_font, fill=hex2rgb(mood["stroke"]))

    # main title, shrink-to-fit
    max_width = W - 140
    font_size = 150
    display_font_path = os.path.join(ASSETS, "BebasNeue-Regular.ttf")
    title_text = title if title.strip() else "YOUR TITLE HERE"
    while font_size > 48:
        font = ImageFont.truetype(display_font_path, font_size)
        lines = wrap_lines(draw, title_text, font, max_width)
        widths_ok = all(draw.textlength(l, font=font) <= max_width for l in lines)
        if len(lines) <= 3 and widths_ok:
            break
        font_size -= 4
    try:
    font = ImageFont.truetype(display_font_path, font_size)
except OSError:
    font = ImageFont.load_default()
    lines = wrap_lines(draw, title_text, font, max_width)

    line_height = int(font_size * 1.05)
    block_height = len(lines) * line_height

    if position == "Top":
        start_y = 140
    elif position == "Center":
        start_y = H / 2 - block_height / 2
    else:
        start_y = H - 70 - block_height

    x = 70
    stroke_w = max(2, int(font_size * 0.09))
    for i, line in enumerate(lines):
        y = start_y + i * line_height
        draw.text(
            (x, y),
            line,
            font=font,
            fill=hex2rgb(mood["text"]),
            stroke_width=stroke_w,
            stroke_fill=hex2rgb(mood["stroke"]),
        )

    return canvas.convert("RGB")


def generate_hooks(topic, api_key):
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[
            {
                "role": "user",
                "content": (
                    f'You write punchy YouTube thumbnail text. Topic: "{topic}". '
                    "Give exactly 3 short thumbnail phrases, each 2-6 words, ALL CAPS, "
                    "high curiosity/hook energy, no hashtags, no quotes, no numbering. "
                    "Respond ONLY with a JSON array of 3 strings, nothing else, no markdown fences."
                ),
            }
        ],
    )
    raw = "".join(block.text for block in msg.content if hasattr(block, "text")).strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


