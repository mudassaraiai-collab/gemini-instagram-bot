# Gemini Instagram Auto-Poster

Generate AI images with **Google Gemini** and auto-post to **Instagram**.

Built by [@mudassaraiai-collab](https://github.com/mudassaraiai-collab)

## Quick Start
```bash
git clone https://github.com/mudassaraiai-collab/gemini-instagram-bot
cd gemini-instagram-bot
pip install -r requirements.txt
cp .env.example .env   # fill in your keys
python generate_and_post.py
```

## API Keys Needed
| Key | Where to Get | Cost |
|-----|-------------|------|
| GEMINI_API_KEY | [aistudio.google.com](https://aistudio.google.com/app/apikey) | Free |
| IG_ACCESS_TOKEN | [Meta Developer Portal](https://developers.facebook.com) | Free |
| IG_USER_ID | Meta Graph API Explorer | Free |
| IMGBB_API_KEY | [api.imgbb.com](https://api.imgbb.com) | Free |

## How It Works
1. Generates 2 AI images via Gemini prompts
2. Combines them vertically (2010 on top, 2026 below)
3. Uploads to ImgBB for a clean public URL
4. Posts directly to Instagram via Meta Graph API
