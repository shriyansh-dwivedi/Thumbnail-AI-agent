# 🎬 AI Thumbnail Agent (100% Free)

Video ka topic/title dijiye — AI ek scroll-stopping YouTube thumbnail generate kar dega.
Backend **Pollinations.ai** use karta hai — free, open-source image generation, **koi card/billing nahi chahiye**.

## Files
- `backend.py` → saara AI logic (prompt engineering + image generation). Streamlit ka koi code nahi.
- `app.py` → sirf Streamlit UI, jo backend.py ko import karta hai.
- `requirements.txt` → dependencies.

## 1. (Optional) Free API key lena
App bina key ke bhi kaam karta hai. Agar zyada reliable/fast chahiye:
1. [enter.pollinations.ai](https://enter.pollinations.ai) pe jao
2. Free sign up karo (GitHub se, **koi credit card nahi chahiye**)
3. Ek free key mil jayegi — app ke sidebar me daal dena (yeh bhi optional hai)

## 2. GitHub par upload
```bash
git init
git add app.py backend.py requirements.txt README.md
git commit -m "AI thumbnail agent (free version)"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

## 3. Streamlit Cloud par deploy
1. [share.streamlit.io](https://share.streamlit.io) par login karo (GitHub se).
2. **"New app"** → apna repo select karo.
3. **Main file path:** `app.py`
4. **Deploy** button dabao — 1-2 min me app live ho jayega.

Bas! Koi billing setup, koi paid tier, koi card — kuch nahi chahiye.

## Local testing (optional)
```bash
pip install -r requirements.txt
streamlit run app.py
```
