"""
app.py — AI Thumbnail Agent (frontend)

Streamlit UI only. All AI logic lives in backend.py and is imported here.
Deploy this file as the "main file path" on Streamlit Community Cloud.
"""

from io import BytesIO

import streamlit as st

from backend import generate_full_thumbnail

st.set_page_config(page_title="AI Thumbnail Agent", page_icon="🎬", layout="centered")

st.title("🎬 AI Thumbnail Agent")
st.caption("Generate scroll-stopping YouTube thumbnails from a simple idea — powered by Pollinations.ai (100% free, no signup).")

# ---------------- Sidebar: settings ----------------
with st.sidebar:
    st.header("⚙️ Settings")
    use_enhancer = st.checkbox(
        "Auto-enhance my prompt with AI",
        value=True,
        help="Turns your simple video idea into a detailed, thumbnail-optimized prompt before generating the image.",
    )
    st.caption("No API key or sign-up needed. If you generate a lot in a row, you may hit a short rate limit — just wait ~15 seconds and try again.")

# ---------------- Main form ----------------
topic = st.text_area(
    "Video title / topic",
    placeholder="e.g. I survived 24 hours alone in the desert",
    height=90,
)

col1, col2 = st.columns(2)
with col1:
    style = st.selectbox(
        "Style",
        ["Bold & Vibrant", "Cinematic", "Minimal / Clean", "Gaming",
         "Tech / Futuristic", "Vlog / Lifestyle", "Shocking / Reaction"],
    )
with col2:
    aspect_ratio = st.selectbox("Aspect ratio", ["16:9", "9:16", "1:1"])

overlay_text = st.text_input(
    "Text to show on the thumbnail (optional)",
    placeholder="e.g. 24 HOURS ALONE",
)

generate_clicked = st.button("✨ Generate Thumbnail", type="primary", use_container_width=True)

# ---------------- Session state ----------------
if "thumbnail" not in st.session_state:
    st.session_state.thumbnail = None
    st.session_state.prompt_used = None

# ---------------- Generate ----------------
if generate_clicked:
    if not topic.strip():
        st.error("Please enter a video title or topic.")
    else:
        with st.spinner("Designing your thumbnail..."):
            try:
                image, final_prompt = generate_full_thumbnail(
                    topic=topic,
                    style=style,
                    overlay_text=overlay_text,
                    aspect_ratio=aspect_ratio,
                    use_prompt_enhancer=use_enhancer,
                )
                st.session_state.thumbnail = image
                st.session_state.prompt_used = final_prompt
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# ---------------- Output ----------------
if st.session_state.thumbnail is not None:
    st.image(st.session_state.thumbnail, caption="Generated Thumbnail", use_container_width=True)

    with st.expander("View the prompt that was used"):
        st.write(st.session_state.prompt_used)

    buf = BytesIO()
    st.session_state.thumbnail.save(buf, format="PNG")
    st.download_button(
        "⬇️ Download Thumbnail",
        data=buf.getvalue(),
        file_name="thumbnail.png",
        mime="image/png",
        use_container_width=True,
    )
