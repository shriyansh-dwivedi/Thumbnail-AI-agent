# 🎬 AI Thumbnail Agent (100% Free, No Sign-up)

Video ka topic/title dijiye — AI ek scroll-stopping YouTube thumbnail generate kar dega.
Backend Pollinations.ai ke **legacy free endpoints** use karta hai — koi API key, koi
sign-up, koi billing, kuch nahi chahiye.

## Files
- `backend.py` → saara AI logic (prompt engineering + image generation). Streamlit ka koi code nahi.
- `app.py` → sirf Streamlit UI, jo backend.py ko import karta hai.
- `requirements.txt` → dependencies.

## GitHub par upload
```bash
git init
git add app.py backend.py requirements.txt README.md
git commit -m "AI thumbnail agent (free, keyless)"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## Streamlit Cloud par deploy
1. [share.streamlit.io](https://share.streamlit.io) par login karo (GitHub se).
2. **"New app"** → apna repo select karo.
3. **Main file path:** `app.py`
4. **Deploy** button dabao — 1-2 min me app live ho jayega.

Bas! Koi key, koi signup, koi card — kuch bhi setup nahi karna. App turant kaam karega.

> Note: Anonymous usage ~15 second ka gap maangta hai lagatar requests ke beech —
> agar bahut jaldi-jaldi generate karoge to ek chhota rate-limit error aa sakta hai,
> bas thoda ruk ke dubara try karo.

## Local testing (optional)
```bash
pip install -r requirements.txt
streamlit run app.py
```
