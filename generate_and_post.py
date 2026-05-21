"""
Gemini Image Generation + Instagram Auto-Poster
================================================
Author: Mudassar Ansari (@mudassaraiai-collab)
Description: Generate AI images using Google Gemini (Imagen 3) and
             auto-post them to Instagram via Meta Graph API.

Requirements:
    pip install google-generativeai requests Pillow python-dotenv

Setup:
    1. Add your keys to .env file (see .env.example)
    2. Run: python generate_and_post.py
"""

import os
import io
import time
import base64
import requests
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
IG_USER_ID        = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN   = os.getenv("IG_ACCESS_TOKEN")
IMGBB_API_KEY     = os.getenv("IMGBB_API_KEY")
GRAPH_API_VERSION = "v21.0"
GRAPH_BASE_URL    = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


def generate_image_gemini(prompt, output_path):
    print(f"Generating image: {prompt[:60]}...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(response_modalities=["image","text"])
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            img = Image.open(io.BytesIO(base64.b64decode(part.inline_data.data)))
            img.save(output_path)
            print(f"Saved: {output_path}")
            return output_path
    raise ValueError("Gemini returned no image.")


def combine_images_vertically(img1_path, img2_path, output_path):
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")
    w = 1080
    h1 = int(img1.height * w / img1.width)
    h2 = int(img2.height * w / img2.width)
    img1, img2 = img1.resize((w,h1), Image.LANCZOS), img2.resize((w,h2), Image.LANCZOS)
    combined = Image.new("RGB", (w, h1+h2))
    combined.paste(img1, (0,0))
    combined.paste(img2, (0,h1))
    combined.save(output_path, quality=95)
    print(f"Combined: {output_path}")
    return output_path


def upload_to_imgbb(image_path):
    with open(image_path,"rb") as f:
        data = base64.b64encode(f.read()).decode()
    r = requests.post("https://api.imgbb.com/1/upload",
                      data={"key": IMGBB_API_KEY, "image": data}, timeout=30)
    r.raise_for_status()
    result = r.json()
    if result.get("success"):
        url = result["data"]["url"]
        print(f"Uploaded: {url}")
        return url
    raise ValueError(f"ImgBB upload failed: {result}")


def instagram_create_container(image_url, caption):
    r = requests.post(f"{GRAPH_BASE_URL}/{IG_USER_ID}/media",
                      data={"image_url": image_url, "caption": caption,
                            "access_token": IG_ACCESS_TOKEN}, timeout=30)
    r.raise_for_status()
    cid = r.json()["id"]
    print(f"Container: {cid}")
    return cid


def instagram_publish(container_id, max_wait=60):
    for i in range(max_wait // 3):
        time.sleep(3)
        r = requests.get(f"{GRAPH_BASE_URL}/{container_id}",
                         params={"fields":"status_code","access_token":IG_ACCESS_TOKEN})
        status = r.json().get("status_code","")
        print(f"Status: {status}")
        if status == "FINISHED": break
        if status == "ERROR": raise ValueError("Container failed.")
    r = requests.post(f"{GRAPH_BASE_URL}/{IG_USER_ID}/media_publish",
                      data={"creation_id":container_id,"access_token":IG_ACCESS_TOKEN})
    r.raise_for_status()
    mid = r.json()["id"]
    print(f"Published! ID: {mid}")
    return mid


POSTS = {
    "mom_then_now": {
        "prompt_1": (
            "Cinematic Indian realistic illustration, warm golden hour, "
            "red brick school building, Indian mother in brown salwar kameez "
            "running after school boy with navy blazer, boy with backpack, "
            "ultra detailed, bold white text 2010 bottom right, 1:1 ratio"
        ),
        "prompt_2": (
            "Cinematic Indian realistic illustration, warm evening light, "
            "house entrance with plants, Indian mother in yellow saree smiling, "
            "holding black leather jacket to son on Royal Enfield motorcycle, "
            "ultra detailed, bold white text 2026 bottom right, 1:1 ratio"
        ),
        "caption": (
            "2010 vs 2026 — Some things never change \U0001f97a\u2764\ufe0f\n\n"
            "In 2010, she ran after you with your school blazer.\n"
            "In 2026, she still runs — this time with your leather jacket.\n\n"
            "The bike upgraded. But her love? Not a single horsepower less. \U0001f6f5\u27a1\ufe0f\U0001f3cd\ufe0f\n\n"
            "Drop a \u2764\ufe0f if your mom still does this.\n\n"
            "#MomLove #ThenAndNow #2010vs2026 #RoyalEnfield #IndianMom #Nostalgia #Blessed"
        )
    }
}


def run_pipeline(post_key="mom_then_now"):
    print("=" * 50)
    print("  Gemini -> Instagram Auto-Poster")
    print("=" * 50)
    post = POSTS[post_key]
    os.makedirs("output", exist_ok=True)
    img1 = generate_image_gemini(post["prompt_1"], "output/image_2010.jpg")
    img2 = generate_image_gemini(post["prompt_2"], "output/image_2026.jpg")
    combined = combine_images_vertically(img1, img2, "output/combined_post.jpg")
    url = upload_to_imgbb(combined)
    cid = instagram_create_container(url, post["caption"])
    mid = instagram_publish(cid)
    print(f"\nDone! Media ID: {mid}")


if __name__ == "__main__":
    run_pipeline()
