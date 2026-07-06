import io
import json
import os

import streamlit as st

from render import MOODS, render_thumbnail

st.set_page_config(page_title="Thumbnail Agent", page_icon="🎬", layout="wide")


def generate_hooks(topic, api_key):
    from groq import Groq

    client = anthropic.Anthropic(api_key='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') 
    msg = client.messages.create(
        model="llama-3.3-70b-versatile",
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


# ---------- UI ----------
st.markdown(
    """
    <style>
    .stApp { background-color: #141210; color: #F5F1EA; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎬 Thumbnail Agent")
st.caption("YouTube thumbnail banao, seconds mein")

col1, col2 = st.columns([1, 1.4], gap="large")

with col1:
    st.subheader("✨ AI Hook Generator")
    api_key = st.secrets.get("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", os.environ.get("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",))
    topic = st.text_area("Video kis baare mein hai?", placeholder="e.g. maine 30 din sirf maggi khai")

    if "hooks" not in st.session_state:
        st.session_state.hooks = []
    if "title" not in st.session_state:
        st.session_state.title = "I TRIED THE VIRAL RECIPE"

    if st.button("Hook ideas banao", use_container_width=True):
        if not api_key:
            st.error('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' set nahi hai. Streamlit secrets mein add karo.")
        elif not topic.strip():
            st.warning("Pehle topic likho.")
        else:
            with st.spinner("Soch raha hoon..."):
                try:
                    st.session_state.hooks = generate_hooks(topic, api_key)
                except Exception:
                    st.error("Suggestions nahi ban paaye, dobara try karo.")

    for h in st.session_state.hooks:
        if st.button(h, key=f"hook-{h}", use_container_width=True):
            st.session_state.title = h

    st.divider()
    st.subheader("Text")
    title = st.text_input("Title text", value=st.session_state.title, key="title_input")
    st.session_state.title = title
    tag = st.text_input("Tag / corner label", value="EP. 12")

    st.subheader("Style")
    mood_name = st.selectbox("Mood / palette", list(MOODS.keys()))
    position = st.radio("Text position", ["Top", "Center", "Bottom"], index=2, horizontal=True)
    overlay = st.checkbox("Dark overlay (text legibility)", value=True)

    st.subheader("Background")
    uploaded = st.file_uploader("Photo upload karo (optional)", type=["png", "jpg", "jpeg"])
    bg_bytes = uploaded.read() if uploaded else None

with col2:
    st.subheader("Preview (1280×720)")
    thumb = render_thumbnail(title, tag, mood_name, position, overlay, bg_bytes)
    st.image(thumb, use_container_width=True)

    buf = io.BytesIO()
    thumb.save(buf, format="PNG")
    st.download_button(
        "⬇️ PNG download karo",
        data=buf.getvalue(),
        file_name="thumbnail.png",
        mime="image/png",
        use_container_width=True,
    )
