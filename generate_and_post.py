"""
Gemini Image Generation + Instagram Auto-Poster
================================================
Author: Mudassar Ansari (@mudassaraiai-collab)
Version: 2.0 — Kids Food Series Edition
Account: @maddy_4589 | FS Ladurée GCC

Series:
    1. Little Chef Lab    🍪  --series chef
    2. What's Inside?     🎭  --series inside
    3. Colour My Food     🌈  --series colour
    4. Food Travels       ✈️  --series travels

Usage:
    python generate_and_post.py               # auto-post next in rotation
    python generate_and_post.py --list        # show all episodes + status
    python generate_and_post.py --series chef --ep 1   # post specific
"""

import os, io, time, base64, argparse, json
import requests
from PIL import Image
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
IG_USER_ID        = os.getenv("IG_USER_ID", "27551421421125823")
IG_ACCESS_TOKEN   = os.getenv("IG_ACCESS_TOKEN")
IMGBB_API_KEY     = os.getenv("IMGBB_API_KEY")
GRAPH_API_VERSION = "v21.0"
GRAPH_BASE_URL    = f"https://graph.facebook.com/{GRAPH_API_VERSION}"
STATE_FILE        = "posted_state.json"

# ─────────────────────────────────────────────────────────
#  CONTENT LIBRARY  — 4 Series, 4 Episodes each
# ─────────────────────────────────────────────────────────

SERIES = {

    "chef": {
        "name": "Little Chef Lab", "emoji": "🍪",
        "episodes": [
            {
                "title": "Can a 6-year-old make a macaron?",
                "prompt_1": (
                    "Cinematic warm pastel kitchen, adorable 6-year-old child wearing tiny white chef hat "
                    "and apron, concentrating hard while piping pink macaron batter onto a baking sheet, "
                    "Ladurée-style backdrop, professional food photography lighting, ultra detailed, 1:1 ratio"
                ),
                "prompt_2": (
                    "Same adorable child holding up a slightly imperfect but cute pink macaron with a huge "
                    "proud smile, pastel kitchen background, Ladurée boxes visible, golden hour lighting, "
                    "ultra detailed, 1:1 ratio"
                ),
                "caption": (
                    "🍪 Can a 6-year-old make a real Ladurée macaron? We tried it — and THIS happened! 👨‍🍳✨\n\n"
                    "Welcome to Little Chef Lab — where tiny hands make BIG food magic! 🎉\n\n"
                    "مرحباً في مختبر الشيف الصغير!\n"
                    "هل يستطيع طفل عمره 6 سنوات صنع ماكارون حقيقي؟ جربنا وهذا ما حدث! 🍪\n\n"
                    "💬 Would YOUR kid try this? Comment below! 👇\n\n"
                    "#LittleChefLab #KidsCooking #Laduree #DubaiKids #UAEKids "
                    "#KidChef #MacaronMagic #BakingWithKids #FoodieKids #KidsOfInstagram"
                )
            },
            {
                "title": "The pinkest cake ever",
                "prompt_1": (
                    "Adorable child in pink apron pouring bright pink batter into cake tin, "
                    "pastel kitchen, flour on nose, laughing expression, warm lighting, "
                    "professional food photography, ultra detailed, 1:1 ratio"
                ),
                "prompt_2": (
                    "Stunning all-pink layered birthday cake on marble counter, rose decorations, "
                    "gold sprinkles, Ladurée-style presentation, pastel backdrop, "
                    "professional food photography, ultra detailed, 1:1 ratio"
                ),
                "caption": (
                    "🎂 We made the PINKEST cake ever — and kids went absolutely wild! 🌸\n\n"
                    "Little Chef Lab EP2 — this week it's all about pink, sugar, and happy faces!\n\n"
                    "صنعنا أكثر كيكة وردية في العالم والأطفال جُنّوا من الفرح! 🌸\n\n"
                    "💬 What colour cake should we make next? 🎨👇\n\n"
                    "#LittleChefLab #PinkCake #KidsBaking #DubaiKids #UAEKids "
                    "#KidChef #CakeBoss #BakingWithKids #FoodieKids #KidsOfInstagram"
                )
            },
            {
                "title": "3 ingredients 5 minutes",
                "prompt_1": (
                    "Child hands carefully measuring three ingredients on clean kitchen counter, "
                    "tiny bowls of flour sugar butter, overhead shot pastel kitchen, "
                    "professional food styling, ultra detailed, 1:1 ratio"
                ),
                "prompt_2": (
                    "Perfectly golden shortbread biscuits cooling on rack, child peeking from background "
                    "with huge smile, pastel kitchen, warm lighting, professional food photography, 1:1 ratio"
                ),
                "caption": (
                    "🥚 3 ingredients. 5 minutes. Kids made MAGIC in the kitchen today! ⏱️✨\n\n"
                    "Little Chef Lab EP3 — the easiest recipe that made the biggest smiles!\n\n"
                    "3 مكونات فقط و5 دقائق — الأطفال صنعوا السحر في المطبخ اليوم! ✨\n\n"
                    "💬 Can YOU guess what we made? Comment your answer! 👇\n\n"
                    "#LittleChefLab #EasyKidsRecipe #KidsCooking #DubaiKids #UAEKids "
                    "#5MinuteRecipe #KidChef #BakingWithKids #FoodieKids #KidsOfInstagram"
                )
            },
            {
                "title": "Chocolate vs vanilla the great debate",
                "prompt_1": (
                    "Two children in aprons facing each other at kitchen counter, one holding chocolate macaron "
                    "one holding vanilla macaron, playful argument expressions, vibrant pastel kitchen, "
                    "professional food photography, 1:1 ratio"
                ),
                "prompt_2": (
                    "Beautiful side by side comparison, dark chocolate macaron vs creamy vanilla macaron "
                    "on marble surface, dramatic studio lighting, ultra detailed, 1:1 ratio"
                ),
                "caption": (
                    "🍫 Chocolate vs vanilla — the great kid debate! 🍦😂\n\n"
                    "Little Chef Lab EP4 had us all laughing AND eating!\n\n"
                    "شوكولاتة أم فانيليا؟ النقاش الكبير بين الأطفال! من فاز؟ 😂\n\n"
                    "💬 Team 🍫 or Team 🍦? Tell us in the comments!\n\n"
                    "#LittleChefLab #ChocolateVsVanilla #KidsCooking #DubaiKids #UAEKids "
                    "#KidChef #FoodieKids #BakingWithKids #KidsOfInstagram #FunFood"
                )
            },
        ]
    },

    "inside": {
        "name": "What's Inside?", "emoji": "🎭",
        "episodes": [
            {
                "title": "Blindfolded taste test",
                "prompt_1": (
                    "Adorable child wearing silk blindfold, sitting at pastel table, mysterious Ladurée "
                    "gift box in front, hands reaching forward, excited expression, warm lighting, "
                    "professional food photography, ultra detailed, 1:1 ratio"
                ),
                "prompt_2": (
                    "Child's face mid-expression tasting macaron for the first time, pure joy and surprise, "
                    "pastel Ladurée macarons scattered beautifully on marble, vibrant colours, "
                    "professional food photography, 1:1 ratio"
                ),
                "caption": (
                    "😱 Blindfolded taste test — can kids guess the Ladurée flavour?!\n\n"
                    "What's Inside? EP1 — the most delicious guessing game your family will ever play! 🎭🍬\n\n"
                    "تجربة تذوق بعيون مغمضة!\n"
                    "هل يستطيع الأطفال تخمين نكهة اللادوريه؟ 😄\n\n"
                    "💬 What flavour do YOU think it was? Guess below! 👇\n\n"
                    "#WhatsInside #KidsTasteTest #Laduree #DubaiKids #UAEKids "
                    "#FoodChallenge #FoodReaction #MacaronLovers #KidsOfInstagram #FoodieFamily"
                )
            },
            {
                "title": "Unboxing the Laduree gift box",
                "prompt_1": (
                    "Iconic Ladurée pale green gift box with gold ribbon on white marble surface, "
                    "soft natural light, elegant Parisian styling, luxury food photography, 1:1 ratio"
                ),
                "prompt_2": (
                    "Child's face with wide eyes and open mouth in pure amazement, rainbow of Ladurée "
                    "macarons revealed in beautiful box, pastel background, warm lighting, 1:1 ratio"
                ),
                "caption": (
                    "📦 We unboxed the most BEAUTIFUL Ladurée gift box — kids lost their minds! 🎁😍\n\n"
                    "What's Inside? EP2 — unboxing luxury French treats in Dubai! 🇫🇷🇦🇪\n\n"
                    "فتحنا أجمل صندوق هدايا من لادوريه — والأطفال لم يصدقوا ما رأوه! 😍\n\n"
                    "💬 What's YOUR favourite thing to unbox? Comment below! 👇\n\n"
                    "#WhatsInside #LadurееUnboxing #Laduree #DubaiKids #UAEKids "
                    "#LuxuryFood #GiftBox #KidsOfInstagram #FoodieFamily #GulfKids"
                )
            },
            {
                "title": "5 flavours 1 blindfold",
                "prompt_1": (
                    "Five different coloured Ladurée macarons lined up on marble, each a distinct vibrant "
                    "colour, numbered tags 1-5, elegant flat lay, professional food photography, 1:1 ratio"
                ),
                "prompt_2": (
                    "Child pulling funny face while tasting surprise macaron flavour blindfolded, "
                    "huge laugh, pastel kitchen, colourful macarons background, 1:1 ratio"
                ),
                "caption": (
                    "🎯 5 flavours. 1 blindfold. Zero wrong answers — only delicious ones! 😂🍪\n\n"
                    "What's Inside? EP3 — our most chaotic taste test yet!\n\n"
                    "5 نكهات، عصابة عيون واحدة، ولا إجابات خاطئة — فقط لذيذة! 😂\n\n"
                    "💬 How many would YOU get right? 1-5 in the comments! 👇\n\n"
                    "#WhatsInside #TasteTest #Laduree #DubaiKids #UAEKids "
                    "#FoodChallenge #KidsTasteTest #MacaronLovers #KidsOfInstagram #FoodieFamily"
                )
            },
            {
                "title": "Mum vs kids taste test",
                "prompt_1": (
                    "Mum and young child sitting opposite each other at kitchen table, both wearing "
                    "blindfolds, Ladurée macarons between them, competitive playful expressions, 1:1 ratio"
                ),
                "prompt_2": (
                    "Child celebrating arms up while mum laughs with wrong answer, macarons on table, "
                    "pastel kitchen, warm family scene, professional photography, 1:1 ratio"
                ),
                "caption": (
                    "👩‍👧 Can mum guess the flavour better than the kids? SPOILER: No. 😂\n\n"
                    "What's Inside? EP4 — Mum vs Kids edition!\n\n"
                    "هل تستطيع الأم تخمين النكهة أفضل من الأطفال؟ الجواب: لا! 😂\n\n"
                    "💬 Tag a mum who thinks she knows better! 👇\n\n"
                    "#WhatsInside #MumVsKids #Laduree #DubaiKids #UAEKids "
                    "#FoodChallenge #FoodReaction #MacaronLovers #KidsOfInstagram #DubaiMoms"
                )
            },
        ]
    },

    "colour": {
        "name": "Colour My Food", "emoji": "🌈",
        "episodes": [
            {
                "title": "Match the macaron to the crayon",
                "prompt_1": (
                    "Flat lay of 8 Ladurée macarons in rainbow colours arranged in perfect arc on marble, "
                    "soft studio lighting, each macaron perfectly distinct colour, "
                    "professional food photography, ultra detailed, 1:1 ratio"
                ),
                "prompt_2": (
                    "Child hand holding coloured crayons next to matching coloured macarons, pastel "
                    "background, overhead shot, perfect colour matching, bright cheerful lighting, "
                    "professional food styling, 1:1 ratio"
                ),
                "caption": (
                    "🌈 Match the macaron to the crayon! Can you guess all 8 colours? 🖍️\n\n"
                    "Welcome to Colour My Food — the most colourful food series for little eyes!\n\n"
                    "طابق الماكارون مع قلم التلوين! 🌈\n"
                    "هل تستطيع تخمين جميع الألوان الـ 8؟\n\n"
                    "💬 Which colour is YOUR favourite? Tell us below! 🎨👇\n\n"
                    "#ColourMyFood #KidsFood #RainbowFood #Laduree #FoodColours "
                    "#DubaiKids #ColourfulFood #UAEKids #FoodArt #KidsFoodFun"
                )
            },
            {
                "title": "Everything yellow",
                "prompt_1": (
                    "Beautiful flat lay of yellow foods — lemon macarons, banana slices, yellow macarons, "
                    "golden honey drizzle, sunflower, all on white marble, bright studio lighting, "
                    "professional food photography, 1:1 ratio"
                ),
                "prompt_2": (
                    "Happy child holding bright yellow macaron up to sunlight, yellow outfit, sunny "
                    "outdoor setting, golden hour, huge smile, professional photography, 1:1 ratio"
                ),
                "caption": (
                    "💛 Everything YELLOW — and it's all delicious! 🌟🍋🌼\n\n"
                    "Colour My Food EP2 — lemon macarons, banana treats, golden pastries!\n\n"
                    "كل شيء أصفر — وكل شيء لذيذ! 💛 ماكارون ليمون، موز، وحلويات ذهبية!\n\n"
                    "💬 What's your favourite yellow food? 🍋 Comment below!\n\n"
                    "#ColourMyFood #YellowFood #KidsFood #Laduree #FoodColours "
                    "#DubaiKids #ColourfulFood #UAEKids #FoodArt #KidsFoodFun"
                )
            },
            {
                "title": "Everything pink",
                "prompt_1": (
                    "Gorgeous flat lay of pink foods — strawberry macarons, rose cream, raspberry tarts, "
                    "pink flowers, all on white marble, soft pink lighting, luxury food photography, 1:1 ratio"
                ),
                "prompt_2": (
                    "Child in pink dress surrounded by pink Ladurée macarons, delighted expression, "
                    "pastel pink background, professional photography, 1:1 ratio"
                ),
                "caption": (
                    "🩷 PINK everything — because life is better in pink! 💗🌸\n\n"
                    "Colour My Food EP3 — strawberry, rose, raspberry!\n\n"
                    "وردي في كل مكان — لأن الحياة أجمل باللون الوردي! 💗\n\n"
                    "💬 Save this if you LOVE pink food! 🌸👇\n\n"
                    "#ColourMyFood #PinkFood #KidsFood #Laduree #StrawberryMacaron "
                    "#DubaiKids #ColourfulFood #UAEKids #FoodArt #KidsFoodFun"
                )
            },
            {
                "title": "The rainbow plate",
                "prompt_1": (
                    "Stunning circular rainbow arrangement of 8 coloured Ladurée macarons on white marble, "
                    "one of each colour of the rainbow, perfectly styled, dramatic studio lighting, 1:1 ratio"
                ),
                "prompt_2": (
                    "Child's face in absolute wonder looking at rainbow macaron plate, eyes wide, "
                    "beautiful colours reflecting on face, magical atmosphere, professional photography, 1:1 ratio"
                ),
                "caption": (
                    "🌈 THE RAINBOW PLATE — all 8 colours together for the first time! 🎊✨\n\n"
                    "Colour My Food EP4 — the most colourful thing on your feed today!\n\n"
                    "طبق قوس قزح — جميع الألوان الـ 8 معاً لأول مرة! 🌈✨\n\n"
                    "💬 Save this post — it's the most colourful thing on your feed! 🎨👇\n\n"
                    "#ColourMyFood #RainbowPlate #KidsFood #Laduree #RainbowFood "
                    "#DubaiKids #ColourfulFood #UAEKids #FoodArt #KidsFoodFun"
                )
            },
        ]
    },

    "travels": {
        "name": "Food Travels", "emoji": "✈️",
        "episodes": [
            {
                "title": "Paris to Dubai the macaron journey",
                "prompt_1": (
                    "Elegant Ladurée patisserie storefront in Paris, golden Eiffel Tower visible behind, "
                    "pastel green facade, warm morning light, cinematic photography, ultra detailed, 1:1 ratio"
                ),
                "prompt_2": (
                    "Ladurée macarons displayed in Dubai luxury boutique, modern glass display case, "
                    "Dubai skyline visible through window, golden light, ultra detailed, 1:1 ratio"
                ),
                "caption": (
                    "✈️ How does a tiny macaron travel 5,500 km from Paris to Dubai?!\n\n"
                    "Welcome to Food Travels — follow your favourite treats on their world journey! 🌍\n\n"
                    "كيف يسافر الماكارون الصغير 5500 كم من باريس إلى دبي؟! ✈️\n\n"
                    "💬 Did you know your food travels this far? Share with a macaron lover! 👇\n\n"
                    "#FoodTravels #KidsEducation #Laduree #FoodJourney #DubaiFood "
                    "#UAEKids #FromParisToDubai #SupplyChain #FoodStories #KidsOfInstagram"
                )
            },
            {
                "title": "The cold chain secret",
                "prompt_1": (
                    "Refrigerated cargo plane loading luxury food boxes, blue cold mist, dramatic lighting, "
                    "macarons visible in temperature-controlled container, ultra detailed, 1:1 ratio"
                ),
                "prompt_2": (
                    "Child-friendly illustrated map showing Paris to Dubai route with snowflake cold chain "
                    "symbols, aeroplane path, clean pastel colours, educational style, 1:1 ratio"
                ),
                "caption": (
                    "🌡️ How do macarons stay PERFECT on a 5,500 km journey? The cold chain secret! ❄️\n\n"
                    "Food Travels EP2 — the science behind keeping luxury food fresh from Paris to Dubai!\n\n"
                    "كيف تبقى الماكارون مثالية خلال الرحلة؟ سر السلسلة الباردة! ❄️\n\n"
                    "💬 Did you know cold chains exist? Drop a 🧊 below!\n\n"
                    "#FoodTravels #ColdChain #Laduree #FoodScience #DubaiFood "
                    "#UAEKids #SupplyChain #FoodJourney #KidsEducation #KidsOfInstagram"
                )
            },
            {
                "title": "Inside the Paris kitchen",
                "prompt_1": (
                    "Elegant Parisian patisserie kitchen, skilled pastry chef piping perfect macaron shells, "
                    "gleaming copper pots, warm golden light, ultra detailed cinematic, 1:1 ratio"
                ),
                "prompt_2": (
                    "Close-up of perfectly formed macaron shells cooling on professional baking trays, "
                    "Ladurée kitchen backdrop, soft lighting, ultra detailed food photography, 1:1 ratio"
                ),
                "caption": (
                    "🇫🇷 It all starts in Paris — inside the legendary Ladurée kitchen! 👨‍🍳🥐\n\n"
                    "Food Travels EP3 — the birthplace of the world's most famous macaron!\n\n"
                    "كل شيء يبدأ في باريس — داخل مطبخ لادوريه الأسطوري! 👨‍🍳\n\n"
                    "💬 Have you ever been to Paris? Drop a 🗼 below!\n\n"
                    "#FoodTravels #Paris #Laduree #FoodJourney #DubaiFood "
                    "#UAEKids #FromParisToDubai #FoodStories #KidsEducation #KidsOfInstagram"
                )
            },
            {
                "title": "6 countries 1 macaron",
                "prompt_1": (
                    "Colourful world map with glowing route from France through Switzerland to UAE, "
                    "macaron icons at key stops, professional infographic style, vibrant colours, 1:1 ratio"
                ),
                "prompt_2": (
                    "Child holding globe looking at map with wonder, Ladurée macarons on world map "
                    "spread, educational fun atmosphere, warm lighting, professional photography, 1:1 ratio"
                ),
                "caption": (
                    "🌍 6 countries, 1 macaron — the most well-travelled treat in the world! 🗺️\n\n"
                    "Food Travels EP4 — the FULL journey from farm to flour to Paris to Dubai!\n\n"
                    "6 دول وماكارون واحد — أكثر الحلويات سفراً في العالم! 🗺️\n\n"
                    "💬 Share with someone who loves geography AND food! 👇\n\n"
                    "#FoodTravels #FoodGeography #Laduree #FoodJourney #DubaiFood "
                    "#UAEKids #SupplyChain #FoodStories #KidsEducation #KidsOfInstagram"
                )
            },
        ]
    }
}


# ─────────────────────────────────────────────────────────
#  CORE FUNCTIONS
# ─────────────────────────────────────────────────────────

def generate_image_gemini(prompt, output_path):
    print(f"  🎨 Generating: {prompt[:70]}...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(response_modalities=["image", "text"])
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            img = Image.open(io.BytesIO(base64.b64decode(part.inline_data.data)))
            img.save(output_path)
            print(f"  ✅ Saved: {output_path}")
            return output_path
    raise ValueError("Gemini returned no image.")


def combine_images_vertically(img1_path, img2_path, output_path):
    img1 = Image.open(img1_path).convert("RGB")
    img2 = Image.open(img2_path).convert("RGB")
    w = 1080
    h1 = int(img1.height * w / img1.width)
    h2 = int(img2.height * w / img2.width)
    img1 = img1.resize((w, h1), Image.LANCZOS)
    img2 = img2.resize((w, h2), Image.LANCZOS)
    combined = Image.new("RGB", (w, h1 + h2))
    combined.paste(img1, (0, 0))
    combined.paste(img2, (0, h1))
    combined.save(output_path, quality=95)
    print(f"  🖼️  Combined: {output_path}")
    return output_path


def upload_to_imgbb(image_path):
    print(f"  📤 Uploading to ImgBB...")
    with open(image_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    r = requests.post("https://api.imgbb.com/1/upload",
                      data={"key": IMGBB_API_KEY, "image": data}, timeout=30)
    r.raise_for_status()
    result = r.json()
    if result.get("success"):
        url = result["data"]["url"]
        print(f"  ✅ URL: {url}")
        return url
    raise ValueError(f"ImgBB upload failed: {result}")


def instagram_create_container(image_url, caption):
    r = requests.post(
        f"{GRAPH_BASE_URL}/{IG_USER_ID}/media",
        data={"image_url": image_url, "caption": caption,
              "access_token": IG_ACCESS_TOKEN}, timeout=30
    )
    r.raise_for_status()
    cid = r.json()["id"]
    print(f"  📦 Container: {cid}")
    return cid


def instagram_publish(container_id, max_wait=90):
    print(f"  ⏳ Processing...")
    for _ in range(max_wait // 3):
        time.sleep(3)
        r = requests.get(f"{GRAPH_BASE_URL}/{container_id}",
                         params={"fields": "status_code", "access_token": IG_ACCESS_TOKEN})
        status = r.json().get("status_code", "")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise ValueError("Container processing failed.")
    r = requests.post(f"{GRAPH_BASE_URL}/{IG_USER_ID}/media_publish",
                      data={"creation_id": container_id, "access_token": IG_ACCESS_TOKEN})
    r.raise_for_status()
    mid = r.json()["id"]
    print(f"  🎉 Published! Instagram ID: {mid}")
    return mid


# ─────────────────────────────────────────────────────────
#  STATE — track what has been posted
# ─────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {s: 0 for s in SERIES}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_next_post(state):
    """Round-robin: pick series with fewest posted episodes."""
    order = ["chef", "inside", "colour", "travels"]
    for key in order:
        idx = state.get(key, 0)
        if idx < len(SERIES[key]["episodes"]):
            return key, idx
    return None, None


# ─────────────────────────────────────────────────────────
#  PIPELINE
# ─────────────────────────────────────────────────────────

def run_pipeline(series_key, ep_index):
    s   = SERIES[series_key]
    ep  = s["episodes"][ep_index]
    num = ep_index + 1

    print("\n" + "=" * 55)
    print(f"  {s['emoji']}  {s['name']} — EP{num}")
    print(f"  📝  {ep['title']}")
    print("=" * 55)

    os.makedirs("output", exist_ok=True)
    img1     = generate_image_gemini(ep["prompt_1"], f"output/{series_key}_ep{num}_a.jpg")
    img2     = generate_image_gemini(ep["prompt_2"], f"output/{series_key}_ep{num}_b.jpg")
    combined = combine_images_vertically(img1, img2, f"output/{series_key}_ep{num}_combined.jpg")
    url      = upload_to_imgbb(combined)
    cid      = instagram_create_container(url, ep["caption"])
    mid      = instagram_publish(cid)

    print(f"\n  ✅ LIVE on @maddy_4589! Media ID: {mid}\n")
    return mid


def list_all():
    state = load_state()
    print("\n📋 gemini-instagram-bot v2.0 — Content Library")
    print("=" * 55)
    for key, s in SERIES.items():
        posted = state.get(key, 0)
        print(f"\n{s['emoji']}  {s['name']}")
        for i, ep in enumerate(s["episodes"]):
            icon = "✅" if i < posted else "⏳"
            print(f"   {icon} EP{i+1}: {ep['title']}")
    print()


# ─────────────────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Gemini Instagram Bot v2.0 — Kids Food Series @maddy_4589"
    )
    parser.add_argument("--series", choices=["chef", "inside", "colour", "travels"],
                        help="Which series to post")
    parser.add_argument("--ep", type=int, help="Episode number (1-based)")
    parser.add_argument("--list", action="store_true", help="List all episodes and status")
    args = parser.parse_args()

    if args.list:
        list_all()
        return

    state = load_state()

    if args.series and args.ep:
        series_key = args.series
        ep_index   = args.ep - 1
    else:
        series_key, ep_index = get_next_post(state)
        if series_key is None:
            print("🎉 All episodes posted! Add more content to SERIES.")
            return

    run_pipeline(series_key, ep_index)
    state[series_key] = ep_index + 1
    save_state(state)


if __name__ == "__main__":
    main()
