"""
Kids Food Instagram Bot
================================================
Author: Mudassar Ansari (@mudassaraiai-collab)
Version: 4.0 — No Brand Names Edition
Account: @maddy_4589

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

load_dotenv()

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
                "prompt_1": "Cinematic warm pastel kitchen adorable 6-year-old child tiny white chef hat apron piping pink macaron batter baking sheet ultra detailed professional food photography",
                "prompt_2": "Adorable child holding imperfect but cute pink macaron huge proud smile pastel kitchen golden hour lighting ultra detailed",
                "caption": (
                    "🍪 Can a 6-year-old make a real macaron? We tried it — and THIS happened! 👨‍🍳✨\n\n"
                    "Welcome to Little Chef Lab — where tiny hands make BIG food magic! 🎉\n\n"
                    "مرحباً في مختبر الشيف الصغير!\n"
                    "هل يستطيع طفل عمره 6 سنوات صنع ماكارون حقيقي؟ جربنا وهذا ما حدث! 🍪\n\n"
                    "💬 Would YOUR kid try this? Comment below! 👇\n\n"
                    "#LittleChefLab #KidsCooking #KidChef #MacaronMagic #BakingWithKids "
                    "#FoodieKids #DubaiKids #UAEKids #KidsOfInstagram #FunWithFood"
                )
            },
            {
                "title": "The pinkest cake ever",
                "prompt_1": "Adorable child pink apron pouring bright pink batter cake tin pastel kitchen flour on nose laughing warm lighting professional photography",
                "prompt_2": "Stunning all-pink layered birthday cake marble counter rose decorations gold sprinkles pastel backdrop professional food photography",
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
                "prompt_1": "Child hands measuring three ingredients kitchen counter tiny bowls flour sugar butter overhead shot pastel kitchen professional food styling",
                "prompt_2": "Perfectly golden shortbread biscuits cooling rack child peeking background huge smile pastel kitchen warm lighting professional photography",
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
                "prompt_1": "Two children aprons facing each other kitchen counter one holding chocolate cookie one vanilla cookie playful argument pastel kitchen warm lighting",
                "prompt_2": "Beautiful side by side dark chocolate cookie vs creamy vanilla cookie marble surface dramatic studio lighting ultra detailed",
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
                "prompt_1": "Adorable child wearing silk blindfold sitting pastel table mysterious colourful gift box hands reaching forward excited expression warm lighting",
                "prompt_2": "Child face mid-expression tasting colourful French cookie first time pure joy surprise pastel sweets scattered on marble vibrant colours",
                "caption": (
                    "😱 Blindfolded taste test — can kids guess the flavour?!\n\n"
                    "What's Inside? EP1 — the most delicious guessing game your family will ever play! 🎭🍬\n\n"
                    "تجربة تذوق بعيون مغمضة!\n"
                    "هل يستطيع الأطفال تخمين النكهة؟ 😄\n\n"
                    "💬 What flavour do YOU think it was? Guess below! 👇\n\n"
                    "#WhatsInside #KidsTasteTest #DubaiKids #UAEKids "
                    "#FoodChallenge #FoodReaction #KidsOfInstagram #FoodieFamily #GulfKids #FunFood"
                )
            },
            {
                "title": "Unboxing the mystery gift box",
                "prompt_1": "Beautiful pale green gift box gold ribbon white marble surface soft natural light elegant luxury food photography pastel background",
                "prompt_2": "Child face wide eyes open mouth amazement rainbow colourful French cookies revealed beautiful gift box pastel background warm lighting",
                "caption": (
                    "📦 We unboxed the most BEAUTIFUL mystery food box — kids lost their minds! 🎁😍\n\n"
                    "What's Inside? EP2 — unboxing luxury treats in Dubai! 🇦🇪\n\n"
                    "فتحنا أجمل صندوق هدايا — والأطفال لم يصدقوا ما رأوه! 😍\n\n"
                    "💬 What's YOUR favourite thing to unbox? Comment below! 👇\n\n"
                    "#WhatsInside #Unboxing #DubaiKids #UAEKids "
                    "#LuxuryFood #GiftBox #KidsOfInstagram #FoodieFamily #GulfKids #FunFood"
                )
            },
            {
                "title": "5 flavours 1 blindfold",
                "prompt_1": "Five different coloured French cookies lined up marble numbered tags elegant flat lay professional food photography soft lighting",
                "prompt_2": "Child pulling funny surprised face tasting mystery cookie flavour blindfolded huge laugh pastel kitchen colourful sweets background",
                "caption": (
                    "🎯 5 flavours. 1 blindfold. Zero wrong answers — only delicious ones! 😂🍪\n\n"
                    "What's Inside? EP3 — our most chaotic taste test yet!\n\n"
                    "5 نكهات، عصابة عيون واحدة، ولا إجابات خاطئة — فقط لذيذة! 😂\n\n"
                    "💬 How many would YOU get right? 1-5 in the comments! 👇\n\n"
                    "#WhatsInside #TasteTest #DubaiKids #UAEKids "
                    "#FoodChallenge #KidsTasteTest #KidsOfInstagram #FoodieFamily #GulfKids #FunFood"
                )
            },
            {
                "title": "Mum vs kids taste test",
                "prompt_1": "Mum and young child sitting opposite kitchen table both wearing blindfolds colourful sweets between them competitive playful expressions warm lighting",
                "prompt_2": "Child celebrating arms up while mum laughs at wrong answer sweets on table pastel kitchen warm family scene professional photography",
                "caption": (
                    "👩‍👧 Can mum guess the flavour better than the kids? SPOILER: No. 😂\n\n"
                    "What's Inside? EP4 — Mum vs Kids edition!\n\n"
                    "هل تستطيع الأم تخمين النكهة أفضل من الأطفال؟ الجواب: لا! 😂\n\n"
                    "💬 Tag a mum who thinks she knows better! 👇\n\n"
                    "#WhatsInside #MumVsKids #DubaiKids #UAEKids "
                    "#FoodChallenge #FoodReaction #KidsOfInstagram #DubaiMoms #GulfMoms #FunFood"
                )
            },
        ]
    },

    "colour": {
        "name": "Colour My Food", "emoji": "🌈",
        "episodes": [
            {
                "title": "Match the cookie to the crayon",
                "prompt_1": "Flat lay 8 colourful French cookies rainbow colours perfect arc white marble soft studio lighting professional food photography ultra detailed",
                "prompt_2": "Child hand holding coloured crayons next to matching coloured cookies pastel background overhead shot bright cheerful lighting professional styling",
                "caption": (
                    "🌈 Match the cookie to the crayon! Can you guess all 8 colours? 🖍️\n\n"
                    "Welcome to Colour My Food — the most colourful food series for little eyes!\n\n"
                    "طابق الكوكيز مع قلم التلوين! 🌈\n"
                    "هل تستطيع تخمين جميع الألوان الـ 8؟\n\n"
                    "💬 Which colour is YOUR favourite? Tell us below! 🎨👇\n\n"
                    "#ColourMyFood #KidsFood #RainbowFood #FoodColours "
                    "#DubaiKids #ColourfulFood #UAEKids #FoodArt #KidsFoodFun #LearningColours"
                )
            },
            {
                "title": "Everything yellow",
                "prompt_1": "Beautiful flat lay yellow foods lemon cookies banana slices golden honey drizzle sunflower white marble bright studio lighting professional food photography",
                "prompt_2": "Happy child holding bright yellow cookie up to sunlight yellow outfit sunny outdoor golden hour huge smile professional photography",
                "caption": (
                    "💛 Everything YELLOW — and it's all delicious! 🌟🍋🌼\n\n"
                    "Colour My Food EP2 — lemon cookies, banana treats, golden pastries!\n\n"
                    "كل شيء أصفر — وكل شيء لذيذ! 💛 كوكيز ليمون، موز، وحلويات ذهبية!\n\n"
                    "💬 What's your favourite yellow food? 🍋 Comment below!\n\n"
                    "#ColourMyFood #YellowFood #KidsFood #FoodColours "
                    "#DubaiKids #ColourfulFood #UAEKids #FoodArt #KidsFoodFun #LearningColours"
                )
            },
            {
                "title": "Everything pink",
                "prompt_1": "Gorgeous flat lay pink foods strawberry cookies rose cream raspberry tarts pink flowers white marble soft pink lighting luxury food photography",
                "prompt_2": "Child pink dress surrounded pink colourful cookies delighted expression pastel pink background professional photography warm lighting",
                "caption": (
                    "🩷 PINK everything — because life is better in pink! 💗🌸\n\n"
                    "Colour My Food EP3 — strawberry, rose, raspberry — all in pink!\n\n"
                    "وردي في كل مكان — لأن الحياة أجمل باللون الوردي! 💗\n\n"
                    "💬 Save this if you LOVE pink food! 🌸👇\n\n"
                    "#ColourMyFood #PinkFood #KidsFood #StrawberryCookies "
                    "#DubaiKids #ColourfulFood #UAEKids #FoodArt #KidsFoodFun #LearningColours"
                )
            },
            {
                "title": "The rainbow plate",
                "prompt_1": "Stunning circular rainbow arrangement 8 coloured French cookies white marble one each colour of the rainbow perfectly styled dramatic studio lighting",
                "prompt_2": "Child face absolute wonder looking rainbow cookie plate eyes wide beautiful colours reflecting magical atmosphere professional photography",
                "caption": (
                    "🌈 THE RAINBOW PLATE — all 8 colours together for the first time! 🎊✨\n\n"
                    "Colour My Food EP4 — the most colourful thing on your feed today!\n\n"
                    "طبق قوس قزح — جميع الألوان الـ 8 معاً لأول مرة! 🌈✨\n\n"
                    "💬 Save this — it's the most colourful thing on your feed! 🎨👇\n\n"
                    "#ColourMyFood #RainbowPlate #KidsFood #RainbowFood "
                    "#DubaiKids #ColourfulFood #UAEKids #FoodArt #KidsFoodFun #LearningColours"
                )
            },
        ]
    },

    "travels": {
        "name": "Food Travels", "emoji": "✈️",
        "episodes": [
            {
                "title": "How cookies travel from Europe to Dubai",
                "prompt_1": "Elegant French patisserie storefront Paris Eiffel Tower visible pastel green facade warm morning light cinematic photography ultra detailed",
                "prompt_2": "Colourful French cookies displayed Dubai luxury boutique modern glass display case Dubai skyline window golden light ultra detailed",
                "caption": (
                    "✈️ How do tiny cookies travel 5,500 km from Europe to Dubai?!\n\n"
                    "Welcome to Food Travels — follow your favourite treats on their world journey! 🌍\n\n"
                    "كيف تسافر الكوكيز الصغيرة 5500 كم من أوروبا إلى دبي؟! ✈️\n\n"
                    "💬 Did you know your food travels this far? Share with a foodie friend! 👇\n\n"
                    "#FoodTravels #KidsEducation #FoodJourney #DubaiFood "
                    "#UAEKids #FromEuropeToDubai #SupplyChain #FoodStories #KidsOfInstagram #GulfKids"
                )
            },
            {
                "title": "The cold chain secret",
                "prompt_1": "Refrigerated cargo plane loading luxury food boxes blue cold mist dramatic lighting colourful cookies temperature controlled container ultra detailed",
                "prompt_2": "Child friendly illustrated map Europe to Dubai route snowflake cold chain symbols aeroplane path clean pastel colours educational style",
                "caption": (
                    "🌡️ How do cookies stay PERFECT on a 5,500 km journey? The cold chain secret! ❄️\n\n"
                    "Food Travels EP2 — the science of keeping luxury food fresh from Europe to Dubai!\n\n"
                    "كيف تبقى الكوكيز مثالية خلال الرحلة؟ سر السلسلة الباردة! ❄️\n\n"
                    "💬 Did you know cold chains exist? Drop a 🧊 below!\n\n"
                    "#FoodTravels #ColdChain #FoodScience #DubaiFood "
                    "#UAEKids #SupplyChain #FoodJourney #KidsEducation #KidsOfInstagram #GulfKids"
                )
            },
            {
                "title": "Inside a European pastry kitchen",
                "prompt_1": "Elegant European pastry kitchen skilled pastry chef piping perfect cookie shells gleaming copper pots warm golden light cinematic ultra detailed",
                "prompt_2": "Close-up perfectly formed colourful cookie shells cooling professional baking trays luxury kitchen backdrop soft lighting ultra detailed",
                "caption": (
                    "🇫🇷 It all starts in Europe — inside a legendary pastry kitchen! 👨‍🍳🥐\n\n"
                    "Food Travels EP3 — where the world's most beautiful cookies are born!\n\n"
                    "كل شيء يبدأ في أوروبا — داخل مطبخ المعجنات الأسطوري! 👨‍🍳\n\n"
                    "💬 Have you ever visited a real pastry kitchen? Drop a 🥐 below!\n\n"
                    "#FoodTravels #PastryKitchen #FoodJourney #DubaiFood "
                    "#UAEKids #FoodStories #KidsEducation #KidsOfInstagram #GulfKids #FoodieFamily"
                )
            },
            {
                "title": "6 countries 1 cookie",
                "prompt_1": "Colourful world map glowing route France through Switzerland to UAE cookie icons at key stops professional infographic vibrant colours ultra detailed",
                "prompt_2": "Child holding globe looking at map with wonder colourful cookies on world map spread educational fun atmosphere warm lighting professional photography",
                "caption": (
                    "🌍 6 countries, 1 cookie — the most well-travelled treat in the world! 🗺️\n\n"
                    "Food Travels EP4 — the FULL journey from farm to flour to Dubai!\n\n"
                    "6 دول وكوكيز واحدة — أكثر الحلويات سفراً في العالم! 🗺️\n\n"
                    "💬 Share with someone who loves geography AND food! 👇\n\n"
                    "#FoodTravels #FoodGeography #FoodJourney #DubaiFood "
                    "#UAEKids #SupplyChain #FoodStories #KidsEducation #KidsOfInstagram #GulfKids"
                )
            },
        ]
    }
}


# ─────────────────────────────────────────────────────────
#  IMAGE GENERATION — Free via Pollinations AI
# ─────────────────────────────────────────────────────────

def generate_image(prompt, output_path):
    print(f"  🎨 Generating: {prompt[:60]}...")
    url = (
        f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
        f"?width=1080&height=1080&nologo=true&seed={hash(prompt) % 99999}"
    )
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=120)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
            img.save(output_path, quality=95)
            print(f"  ✅ Saved: {output_path}")
            return output_path
        except Exception as e:
            print(f"  ⚠️ Attempt {attempt+1} failed: {e}. Retrying...")
            time.sleep(5)
    raise ValueError("Image generation failed after 3 attempts.")


# ─────────────────────────────────────────────────────────
#  IMAGE PROCESSING
# ─────────────────────────────────────────────────────────

def combine_and_crop(img1_path, img2_path, output_path):
    """Combine two images into perfect Instagram 4:5 ratio.
    Each image gets exactly half the canvas — no cropping, both fully visible.
    """
    from PIL import ImageDraw, ImageFont
    W = 1080
    HALF_H = 675          # Each image gets 675px — total 1350px = perfect 4:5
    DIVIDER = 6           # Thin divider line between images
    LABEL_H = 60          # Height of year label bar
    CANVAS_H = HALF_H * 2 + DIVIDER  # 1356px total

    # Open and resize both images to exactly W x HALF_H (fill, center crop)
    def fit_image(path, w, h):
        img = Image.open(path).convert("RGB")
        # Scale to fill the target box
        scale = max(w / img.width, h / img.height)
        new_w = int(img.width * scale)
        new_h = int(img.height * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        # Center crop
        left = (new_w - w) // 2
        top  = (new_h - h) // 2
        return img.crop((left, top, left + w, top + h))

    img_top = fit_image(img1_path, W, HALF_H)
    img_bot = fit_image(img2_path, W, HALF_H)

    # Create canvas
    canvas = Image.new("RGB", (W, CANVAS_H), (20, 20, 20))
    canvas.paste(img_top, (0, 0))
    canvas.paste(img_bot, (0, HALF_H + DIVIDER))

    # Add dark overlay strip + year label on each half
    draw = ImageDraw.Draw(canvas)

    # Top label (THEN year) — bottom of top image
    draw.rectangle([(0, HALF_H - LABEL_H), (W, HALF_H)], fill=(0, 0, 0, 180))
    draw.rectangle([(0, HALF_H + DIVIDER), (W, HALF_H + DIVIDER + LABEL_H)], fill=(0, 0, 0, 180))

    # Try to load a font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 42)
        font_sm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font = ImageFont.load_default()
        font_sm = font

    # Year labels
    draw.text((40, HALF_H - LABEL_H + 10), "THEN", font=font, fill=(255, 255, 255))
    draw.text((40, HALF_H + DIVIDER + 10), "NOW  2026", font=font, fill=(255, 215, 0))

    # Divider line
    draw.rectangle([(0, HALF_H), (W, HALF_H + DIVIDER)], fill=(255, 215, 0))

    # Final resize to exact 1080x1350
    final = canvas.resize((1080, 1350), Image.LANCZOS)
    final.save(output_path, quality=95)
    print(f"  🖼️  Saved: {output_path} (1080x1350 — both images fully visible)")
    return output_path


# ─────────────────────────────────────────────────────────
#  IMGBB UPLOAD
# ─────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────
#  INSTAGRAM PUBLISH
# ─────────────────────────────────────────────────────────

def instagram_post(image_url, caption):
    r = requests.post(
        f"{GRAPH_BASE_URL}/{IG_USER_ID}/media",
        data={"image_url": image_url, "caption": caption,
              "access_token": IG_ACCESS_TOKEN}, timeout=30
    )
    r.raise_for_status()
    resp = r.json()
    if "id" not in resp:
        raise ValueError(f"Container failed: {resp}")
    cid = resp["id"]
    print(f"  📦 Container: {cid}")
    print(f"  ⏳ Processing...")
    for _ in range(30):
        time.sleep(3)
        s = requests.get(f"{GRAPH_BASE_URL}/{cid}",
                         params={"fields": "status_code",
                                 "access_token": IG_ACCESS_TOKEN}).json()
        status = s.get("status_code", "")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise ValueError("Container processing failed.")
    r = requests.post(
        f"{GRAPH_BASE_URL}/{IG_USER_ID}/media_publish",
        data={"creation_id": cid, "access_token": IG_ACCESS_TOKEN}
    )
    r.raise_for_status()
    mid = r.json()["id"]
    print(f"  🎉 Published! Instagram ID: {mid}")
    return mid


# ─────────────────────────────────────────────────────────
#  STATE TRACKING
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
    for key in ["chef", "inside", "colour", "travels"]:
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
    img1     = generate_image(ep["prompt_1"], f"output/{series_key}_ep{num}_a.jpg")
    img2     = generate_image(ep["prompt_2"], f"output/{series_key}_ep{num}_b.jpg")
    combined = combine_and_crop(img1, img2, f"output/{series_key}_ep{num}_final.jpg")
    url      = upload_to_imgbb(combined)
    mid      = instagram_post(url, ep["caption"])

    print(f"\n  ✅ LIVE on @maddy_4589! Media ID: {mid}\n")
    return mid


def list_all():
    state = load_state()
    print("\n📋 Kids Food Bot v4.0 — Content Library")
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
        description="Kids Food Instagram Bot v4.0 — @maddy_4589"
    )
    parser.add_argument("--series", choices=["chef", "inside", "colour", "travels"])
    parser.add_argument("--ep", type=int)
    parser.add_argument("--list", action="store_true")
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
            print("🎉 All episodes posted!")
            return

    run_pipeline(series_key, ep_index)
    state[series_key] = ep_index + 1
    save_state(state)


if __name__ == "__main__":
    main()


# ─────────────────────────────────────────────────────────
#  30-DAY THEN VS NOW SERIES
#  Indian Family + Dubai Expat Life
#  English + Arabic Captions
# ─────────────────────────────────────────────────────────

POSTS_30 = [
    {
        "day": 1,
        "title": "Mom & School Blazer",
        "prompt_1": "Cinematic Indian realistic illustration, warm golden hour, red brick school building, Indian mother in brown salwar kameez running after school boy with navy blazer, boy with backpack, ultra detailed, bold white text 2010 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, warm evening light, house entrance with plants, Indian mother in yellow saree smiling, holding black leather jacket to son on Royal Enfield motorcycle, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2010 vs 2026 — Some things never change 🥺❤️\n\nIn 2010, she ran after you with your school blazer.\nIn 2026, she still runs — this time with your leather jacket.\n\nThe bike upgraded. But her love? Not a single horsepower less. 🛵➡️🏍️\n\nDrop a ❤️ if your mom still does this.\n\n٢٠١٠ مقابل ٢٠٢٦ — بعض الأشياء لا تتغير أبداً\nفي ٢٠١٠، كانت تركض خلفك بالبليزر المدرسي.\nفي ٢٠٢٦، لا تزال تركض — هذه المرة بجاكيتك الجلدي. ❤️\n\n#MomLove #ThenAndNow #2010vs2026 #IndianMom #Nostalgia #Blessed #DubaiLife #ExpatLife"
    },
    {
        "day": 2,
        "title": "Dad's Old Car vs New Car",
        "prompt_1": "Cinematic Indian realistic illustration, warm morning light, Indian father in simple shirt teaching teenage son to drive old Maruti 800 car on empty road, both nervous expressions, ultra detailed, bold white text 2005 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, Dubai highway sunset, same son now adult confident driving luxury BMW SUV, father in passenger seat smiling proudly, Dubai skyline visible, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2005 vs 2026 — He taught me everything I know 🚗➡️🚙\n\nIn 2005, he sat next to me in the old Maruti, nervous but proud.\nIn 2026, he sits next to me in Dubai — still nervous. Still proud.\n\nDad, you were right. I did figure it out. 🙏\n\n٢٠٠٥ مقابل ٢٠٢٦ — علّمني كل ما أعرفه\nفي ٢٠٠٥، جلس بجانبي في السيارة القديمة، خائف لكنه فخور.\nفي ٢٠٢٦، يجلس بجانبي في دبي — لا يزال فخوراً. ❤️\n\n#DadGoals #ThenAndNow #IndianDad #DubaiLife #Grateful #FamilyFirst #ExpatLife #Nostalgia"
    },
    {
        "day": 3,
        "title": "First Salary",
        "prompt_1": "Cinematic Indian realistic illustration, small Indian office, young man in formal shirt receiving first salary envelope from boss, huge smile, colleagues clapping, ultra detailed, bold white text 2015 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, modern Dubai office glass tower, same man now senior executive in business suit receiving award on stage, large audience, Dubai skyline behind, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2015 vs 2026 — From first salary to first award 🏆\n\nFirst salary: ₹18,000. Spent it all on family dinner.\nFirst Dubai award: Priceless. Still called mom first.\n\nThe currency changed. The values never did. 🙏\n\n٢٠١٥ مقابل ٢٠٢٦ — من أول راتب إلى أول جائزة\nأول راتب: أنفقته كله على عشاء العائلة.\nأول جائزة في دبي: لا تقدر بثمن. اتصلت بأمي أولاً. ❤️\n\n#FirstSalary #CareerGrowth #DubaiLife #IndianExpat #Hustle #ThenAndNow #Grateful #Success"
    },
    {
        "day": 4,
        "title": "Diwali Then vs Now",
        "prompt_1": "Cinematic Indian realistic illustration, traditional Indian home courtyard, family in colourful traditional clothes lighting diyas together, children playing with sparklers, warm golden light, ultra detailed, bold white text 2010 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, modern Dubai apartment balcony, Indian family in traditional clothes doing video call with relatives back home, small diya setup, Dubai city lights behind, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2010 vs 2026 — Diwali feels different abroad 🪔\n\nIn 2010, the whole family under one roof.\nIn 2026, the whole family on one screen.\n\nSame love. Different timezone. 🥺\n\n٢٠١٠ مقابل ٢٠٢٦ — ديوالي تشعر بشكل مختلف خارج البلاد\nفي ٢٠١٠، العائلة كلها تحت سقف واحد.\nفي ٢٠٢٦، العائلة كلها على شاشة واحدة.\nنفس الحب. منطقة زمنية مختلفة. 🪔\n\n#Diwali #DubaiExpat #IndianAbroad #ThenAndNow #FamilyLove #Nostalgia #DiwaliVibes #HomeAway"
    },
    {
        "day": 5,
        "title": "School Lunch Box",
        "prompt_1": "Cinematic Indian realistic illustration, Indian mother early morning in kitchen, lovingly packing steel tiffin lunchbox with roti and sabzi, steam rising, warm kitchen light, ultra detailed, bold white text 2008 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, modern Dubai kitchen, same mother visiting from India, video calling her son at work while cooking his favourite meal, phone propped on counter, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2008 vs 2026 — She still makes sure you eat 😭❤️\n\nIn 2008, she packed your lunch at 6AM before school.\nIn 2026, she video calls at 1PM to ask if you had lunch.\n\nMom's love needs no timezone. 🙏\n\n٢٠٠٨ مقابل ٢٠٢٦ — لا تزال تتأكد من أنك أكلت\nفي ٢٠٠٨، كانت تحضّر غداءك الساعة السادسة صباحاً.\nفي ٢٠٢٦، تتصل الساعة الواحدة ظهراً لتسأل إذا أكلت. ❤️\n\n#MomLife #ThenAndNow #IndianMom #DubaiExpat #LunchBoxMemories #Nostalgia #MomLove #HomeFood"
    },
    {
        "day": 6,
        "title": "Cricket in the Street vs Dubai Stadium",
        "prompt_1": "Cinematic Indian realistic illustration, narrow Indian street, group of boys playing cricket with tape ball, improvised stumps, kids cheering, golden afternoon light, ultra detailed, bold white text 2005 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, modern Dubai cricket stadium, same man now playing corporate cricket tournament in proper whites, large crowd, Dubai skyline visible, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2005 vs 2026 — The game never left me 🏏\n\nIn 2005, tape ball cricket on the street after school.\nIn 2026, corporate cricket in Dubai under floodlights.\n\nThe bat got lighter. The dreams got bigger. 🌟\n\n٢٠٠٥ مقابل ٢٠٢٦ — اللعبة لم تتركني أبداً\nفي ٢٠٠٥، كريكيت الشارع بعد المدرسة.\nفي ٢٠٢٦، كريكيت في ملعب دبي. 🏏\n\n#Cricket #ThenAndNow #DubaiLife #IndianExpat #SportsDubai #Hustle #NeverGiveUp #StreetToPro"
    },
    {
        "day": 7,
        "title": "Sunday Family Breakfast",
        "prompt_1": "Cinematic Indian realistic illustration, traditional Indian home dining room, joint family Sunday breakfast, grandmother serving hot parathas, everyone talking laughing together, ultra detailed, bold white text 2010 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, modern Dubai cafe, nuclear family Sunday brunch, couple with young children, avocado toast and coffee, cheerful warm ambiance, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2010 vs 2026 — Sunday breakfasts hit different 😄\n\nIn 2010: 20 people, parathas, noise, chai, arguments, laughter.\nIn 2026: 4 people, avocado toast, silence, coffee, peace.\n\nBoth perfect. Both missed. 🥺\n\n٢٠١٠ مقابل ٢٠٢٦ — وجبات الإفطار يوم الأحد مختلفة\nفي ٢٠١٠: ٢٠ شخصاً، برياني، ضجيج، شاي، ضحكات.\nفي ٢٠٢٦: ٤ أشخاص، قهوة، هدوء.\nكلاهما رائع. كلاهما مفقود. ❤️\n\n#SundayBreakfast #ThenAndNow #IndianFamily #DubaiLife #FamilyVibes #Nostalgia #HomeFood #ExpatLife"
    },
    {
        "day": 8,
        "title": "First Phone",
        "prompt_1": "Cinematic Indian realistic illustration, Indian teenager excitedly showing Nokia 3310 phone to friends in school corridor, everyone amazed, ultra detailed, bold white text 2004 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, modern Dubai home, man upgrading to latest iPhone, young child already expertly using iPad next to him, ironic smile, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2004 vs 2026 — Technology humbles you fast 😂📱\n\nIn 2004, Nokia 3310 made you the coolest kid in class.\nIn 2026, your 3-year-old explains your iPhone to you.\n\nCircle of life. 😅\n\n٢٠٠٤ مقابل ٢٠٢٦ — التكنولوجيا تتطور بسرعة\nفي ٢٠٠٤، نوكيا ٣٣١٠ جعلتك أروع طفل في الفصل.\nفي ٢٠٢٦، طفلك البالغ ٣ سنوات يشرح لك الآيفون. 😂\n\n#NokiaVsiPhone #ThenAndNow #TechLife #DubaiLife #IndianExpat #Parenting #FunnyButTrue #Nostalgia"
    },
    {
        "day": 9,
        "title": "First Flight",
        "prompt_1": "Cinematic Indian realistic illustration, busy Indian airport departure hall, young man with large suitcase emotional farewell, mother wiping tears, father strong but emotional, ultra detailed, bold white text 2015 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, Dubai International Airport, same man now confident in business class lounge, video calling parents casually, Dubai duty free visible, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2015 vs 2026 — The airport that changed everything ✈️\n\nIn 2015, first flight. Shaking hands. Tearful goodbyes.\nIn 2026, 47th flight. Business class. Still missing home.\n\nThe ticket class changed. The homesickness never did. 🥺\n\n٢٠١٥ مقابل ٢٠٢٦ — المطار الذي غيّر كل شيء\nفي ٢٠١٥، أول رحلة. يدان ترتجفان. وداع مؤلم.\nفي ٢٠٢٦، الرحلة السابعة والأربعون. درجة أولى. لا يزال الحنين موجوداً. ✈️\n\n#FirstFlight #DubaiExpat #IndianAbroad #ThenAndNow #AirportFeelings #Hustle #MissHome #ExpatLife"
    },
    {
        "day": 10,
        "title": "Wedding Expectations",
        "prompt_1": "Cinematic Indian realistic illustration, traditional Indian wedding with hundreds of guests, elaborate decorations, family chaos, bride and groom overwhelmed, colourful chaos, ultra detailed, bold white text 2018 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, intimate Dubai beach wedding, same couple renewing vows, only close family, simple elegant flowers, Dubai coastline, peaceful smiles, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2018 vs 2026 — We learned what actually matters 💍\n\nIn 2018, 500 guests. 3 days. Chaos. Beautiful chaos.\nIn 2026, 20 people. 1 sunset. Peace. Perfect peace.\n\nBoth days, same person. That's the point. ❤️\n\n٢٠١٨ مقابل ٢٠٢٦ — تعلمنا ما يهم حقاً\nفي ٢٠١٨، ٥٠٠ ضيف. ٣ أيام. فوضى جميلة.\nفي ٢٠٢٦، ٢٠ شخصاً. غروب شمس. سلام تام. ❤️\n\n#WeddingLife #ThenAndNow #DubaiWedding #IndianWedding #LoveStory #Married #DubaiLife #CoupleGoals"
    },
    {
        "day": 11,
        "title": "Homework vs Kids Homework",
        "prompt_1": "Cinematic Indian realistic illustration, Indian boy struggling with maths homework at wooden desk by lamp light, textbooks everywhere, father helping patiently, ultra detailed, bold white text 2005 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, Dubai apartment study room, Indian father now struggling to help his own child with advanced maths homework on iPad, child looking unimpressed, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2005 vs 2026 — Karma is real 😂📚\n\nIn 2005, dad patiently helped you with maths.\nIn 2026, your kid asks YOU for help.\nAnd suddenly... you understand nothing.\n\nDad, I owe you an apology. 😅\n\n٢٠٠٥ مقابل ٢٠٢٦ — الكارما حقيقية\nفي ٢٠٠٥، ساعدك والدك في الرياضيات بصبر.\nفي ٢٠٢٦، ابنك يطلب منك المساعدة.\nوفجأة... لا تفهم شيئاً. 😂\n\n#ParentingLife #ThenAndNow #DubaiDad #IndianDad #Karma #FunnyButTrue #SchoolLife #DadLife"
    },
    {
        "day": 12,
        "title": "Ramadan Then vs Now",
        "prompt_1": "Cinematic Indian realistic illustration, traditional Middle Eastern home, large extended family gathered for iftar, dates, water, traditional food spread, warm lantern light, ultra detailed, bold white text 2010 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, modern Dubai iftar tent, multicultural group of colleagues and friends breaking fast together, Indian expat among them, Dubai skyline, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2010 vs 2026 — Ramadan taught me what home means 🌙\n\nIn 2010, iftar was family. Blood family.\nIn 2026, iftar is family. Chosen family.\n\nDubai gave me a second home. 🥺✨\n\n٢٠١٠ مقابل ٢٠٢٦ — رمضان علّمني معنى البيت\nفي ٢٠١٠، الإفطار كان مع العائلة. العائلة الحقيقية.\nفي ٢٠٢٦، الإفطار مع العائلة. العائلة المختارة.\nدبي أعطتني وطناً ثانياً. 🌙\n\n#Ramadan #Iftar #DubaiLife #MulticulturalDubai #IndianExpat #ThenAndNow #RamadanKareem #Dubai"
    },
    {
        "day": 13,
        "title": "Old Scooter vs Car",
        "prompt_1": "Cinematic Indian realistic illustration, Indian man on old Hero Honda scooter in rain, plastic bag over helmet, holding grocery bags, determined face, ultra detailed, bold white text 2012 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same man now driving air-conditioned SUV in Dubai, ordering groceries on phone app, laughing, Dubai road visible, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2012 vs 2026 — The commute upgraded. The work ethic didn't. 💪\n\nIn 2012, scooter in the rain. Grocery bags as waterproofing.\nIn 2026, AC car. Groceries delivered to the door.\n\nBut that scooter taught me everything. 🛵❤️\n\n٢٠١٢ مقابل ٢٠٢٦ — تطورت وسيلة التنقل. لكن أخلاق العمل بقيت.\nفي ٢٠١٢، دراجة في المطر.\nفي ٢٠٢٦، سيارة مكيفة في دبي. 💪\n\n#Hustle #ThenAndNow #GlowUp #DubaiLife #IndianExpat #WorkEthic #FromScratch #NeverForgetWhere"
    },
    {
        "day": 14,
        "title": "Valentine's Day",
        "prompt_1": "Cinematic Indian realistic illustration, young Indian couple shy and romantic, boy giving single rose outside college gate, nervous expression, friends watching and teasing, ultra detailed, bold white text 2012 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same couple now, Dubai rooftop restaurant anniversary dinner, city lights behind, comfortable confident love, two kids with them, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2012 vs 2026 — From one rose to forever 🌹\n\nIn 2012, one rose. Sweaty palms. Will she say yes?\nIn 2026, one table for four. Same person. She still says yes.\n\nReal love just gets comfortable. ❤️\n\n٢٠١٢ مقابل ٢٠٢٦ — من وردة واحدة إلى الأبد\nفي ٢٠١٢، وردة واحدة. راحتان متعرقتان. هل ستقبل؟\nفي ٢٠٢٦، طاولة لأربعة. نفس الشخص. لا تزال تقبل. ❤️\n\n#ValentinesDay #ThenAndNow #LoveStory #DubaiCouple #IndianCouple #Married #RealLove #Romantic"
    },
    {
        "day": 15,
        "title": "First Job Interview",
        "prompt_1": "Cinematic Indian realistic illustration, nervous young Indian man in oversized suit outside office building, rehearsing answers, ultra detailed, bold white text 2014 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same man now on other side of table as senior interviewer in Dubai glass office, calm confident, reviewing CV, Dubai skyline behind him, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2014 vs 2026 — From interviewee to interviewer 🤝\n\nIn 2014, nervous outside the door. Suit two sizes too big.\nIn 2026, calm behind the desk. Still remembering that feeling.\n\nAlways be kind to the nervous one. You were them once. 🙏\n\n٢٠١٤ مقابل ٢٠٢٦ — من مُقابَل إلى مُقابِل\nفي ٢٠١٤، متوتر أمام الباب. بدلة كبيرة عليه.\nفي ٢٠٢٦، هادئ خلف المكتب. لا يزال يتذكر ذلك الشعور. 🤝\n\n#CareerGrowth #ThenAndNow #DubaiJobs #IndianExpat #Leadership #Hustle #NeverForget #Success"
    },
    {
        "day": 16,
        "title": "Mom's Birthday Call",
        "prompt_1": "Cinematic Indian realistic illustration, Indian family celebrating mom's birthday at home, homemade cake, children singing, father smiling, everyone together, warm light, ultra detailed, bold white text 2009 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, man in Dubai apartment midnight video call, holding store-bought cake to camera, mom on screen laughing and wiping tears, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2009 vs 2026 — Happy Birthday Maa 🎂\n\nIn 2009, homemade cake, everyone together, she pretended to be surprised.\nIn 2026, store cake, video call, she still pretends to be surprised.\n\nSome traditions travel with you. ❤️🥺\n\n٢٠٠٩ مقابل ٢٠٢٦ — عيد ميلاد سعيد يا أماه\nفي ٢٠٠٩، كيكة منزلية، الجميع معاً.\nفي ٢٠٢٦، مكالمة فيديو من دبي، نفس الابتسامة. ❤️\n\n#MomBirthday #ThenAndNow #MomLove #DubaiExpat #IndianMom #FamilyFirst #MissHome #Nostalgia"
    },
    {
        "day": 17,
        "title": "Old Rented Room vs Own Home",
        "prompt_1": "Cinematic Indian realistic illustration, tiny shared rented room in Dubai, 3 men with bunk beds, small window, suitcases under bed, hopeful faces, ultra detailed, bold white text 2015 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same man now in spacious Dubai apartment living room, family around him, own furniture, plants, framed photos, Dubai view from window, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2015 vs 2026 — Every struggle had a purpose 🏠\n\nIn 2015, bunk bed. 3 men. 1 bathroom. Big dreams.\nIn 2026, own apartment. Family. Dubai view. Dreams delivered.\n\nThe room was small. The ambition was not. 💪\n\n٢٠١٥ مقابل ٢٠٢٦ — كل صراع كان له هدف\nفي ٢٠١٥، سرير طابقين. ٣ رجال. حمام واحد. أحلام كبيرة.\nفي ٢٠٢٦، شقة خاصة. عائلة. إطلالة على دبي. الأحلام تحققت. 🏠\n\n#DubaiLife #ThenAndNow #Hustle #GlowUp #IndianExpat #OwnHome #FromScratch #DreamsDoComeTrue"
    },
    {
        "day": 18,
        "title": "Sister's Wedding",
        "prompt_1": "Cinematic Indian realistic illustration, Indian brother escorting sister in red bridal lehenga at traditional wedding ceremony, emotional moment, flower decorations, ultra detailed, bold white text 2019 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same man now video calling sister on her wedding anniversary from Dubai, her with husband and baby, screen glowing in dark room, emotional smile, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2019 vs 2026 — My biggest role was giving you away 💐\n\nIn 2019, I walked you down the aisle. Couldn't look at your face.\nIn 2026, I watch you from a screen. Still can't look at your face.\n\nBig brothers never stop feeling small in these moments. 🥺\n\n٢٠١٩ مقابل ٢٠٢٦ — دوري الأكبر كان تسليمكِ\nفي ٢٠١٩، رافقتكِ في حفل زفافكِ. لم أستطع النظر إلى وجهكِ.\nفي ٢٠٢٦، أشاهدكِ من شاشة. ❤️\n\n#Siblings #ThenAndNow #SisterLove #IndianFamily #BrotherSister #DubaiExpat #FamilyFirst #Nostalgia"
    },
    {
        "day": 19,
        "title": "Street Food vs Fine Dining",
        "prompt_1": "Cinematic Indian realistic illustration, young man happily eating pani puri from street vendor in Indian market, paper plate, standing in crowd, 5 rupees, ultra detailed, bold white text 2010 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same man at upscale Dubai restaurant, elegant plated food, nice clothes, but looking slightly nostalgic staring at the fancy plate, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2010 vs 2026 — Nothing will ever beat ₹5 pani puri 😂🍽️\n\nIn 2010, ₹5 pani puri on the street. Absolute happiness.\nIn 2026, AED 200 dinner in Dubai. Still thinking about pani puri.\n\nThe upgrade is real. The cravings are realer. 😅\n\n٢٠١٠ مقابل ٢٠٢٦ — لا شيء يتفوق على طعام الشارع\nفي ٢٠١٠، طعام شارع بخمس روبيات. سعادة مطلقة.\nفي ٢٠٢٦، عشاء فاخر في دبي. لا يزال يفكر في طعام الشارع. 😂\n\n#StreetFood #ThenAndNow #FoodieLife #DubaiFood #IndianFood #Nostalgia #FineDining #FunnyButTrue"
    },
    {
        "day": 20,
        "title": "First Car in Dubai",
        "prompt_1": "Cinematic Indian realistic illustration, Indian expat nervously test driving second-hand old Toyota in Dubai, dealer watching, sweating, ultra detailed, bold white text 2016 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same man now confidently picking up brand new SUV from Dubai dealership, wife and kids excited beside him, showroom setting, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2016 vs 2026 — Every car told a chapter 🚗\n\nIn 2016, second-hand Toyota. AC barely worked. Proudest day.\nIn 2026, brand new SUV. Family in tow. Still the proudest day.\n\nIt was never about the car. It was about what it meant. 💪\n\n٢٠١٦ مقابل ٢٠٢٦ — كل سيارة حكت فصلاً\nفي ٢٠١٦، تويوتا مستعملة. أفخر يوم في حياته.\nفي ٢٠٢٦، سيارة جديدة. لا يزال أفخر يوم. 🚗\n\n#FirstCar #DubaiLife #ThenAndNow #IndianExpat #Hustle #GlowUp #CarLife #DreamsDoComeTrue"
    },
    {
        "day": 21,
        "title": "Grandmother's Hands",
        "prompt_1": "Cinematic Indian realistic illustration, close-up elderly Indian grandmother's hands lovingly feeding young grandson from her hands, warm kitchen, traditional home, ultra detailed, bold white text 2005 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same grandson now adult man in Dubai kitchen, video calling grandmother, trying to cook her recipe, failing slightly, both laughing, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2005 vs 2026 — Her recipe lives in my heart, not my hands 😭❤️\n\nIn 2005, she fed me with her hands. Best food I ever had.\nIn 2026, I try her recipe from 3,000km away. It never tastes the same.\n\nSome flavours only she can make. 🙏\n\n٢٠٠٥ مقابل ٢٠٢٦ — وصفتها تعيش في قلبي\nفي ٢٠٠٥، أطعمتني بيديها. أفضل طعام أكلته في حياتي.\nفي ٢٠٢٦، أحاول وصفتها من مسافة ٣٠٠٠ كيلومتر. لا تشبه أبداً. 😭\n\n#Grandma #ThenAndNow #IndianFamily #HomeFood #DubaiExpat #FamilyLove #Nostalgia #MissHome"
    },
    {
        "day": 22,
        "title": "Dad's Advice",
        "prompt_1": "Cinematic Indian realistic illustration, Indian father sitting with teenage son on rooftop at night giving serious life advice, stars visible, simple home background, ultra detailed, bold white text 2010 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same son now father in Dubai, sitting with his own young son on apartment balcony at night, Dubai city lights below, passing wisdom forward, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2010 vs 2026 — Now I finally understand what he meant 🌙\n\nIn 2010, dad said: work hard, stay humble, never forget home.\nIn 2026, I tell my son the exact same words.\n\nSome things are worth passing on. 🙏\n\n٢٠١٠ مقابل ٢٠٢٦ — الآن أفهم ما كان يعنيه\nفي ٢٠١٠، قال أبي: اعمل بجد، كن متواضعاً، لا تنسَ البيت.\nفي ٢٠٢٦، أقول لابني نفس الكلمات. 🌙\n\n#DadAdvice #ThenAndNow #IndianDad #DubaiDad #Parenting #Wisdom #FamilyFirst #GenerationToGeneration"
    },
    {
        "day": 23,
        "title": "Eid Celebrations",
        "prompt_1": "Cinematic Indian realistic illustration, colourful Indian Muslim neighbourhood Eid morning, family in new clothes, children getting eidi money, neighbours greeting each other, festive atmosphere, ultra detailed, bold white text 2008 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, Dubai multicultural Eid gathering, same family now with UAE friends and expat community, traditional clothes mix, modern Dubai building behind, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2008 vs 2026 — Eid is bigger when you share it ✨🌙\n\nIn 2008, Eid in the neighbourhood. Everyone knew everyone.\nIn 2026, Eid in Dubai. Everyone is from everywhere. Still the same feeling.\n\nEid Mubarak to the big beautiful family we chose. 🤲\n\nعيد مبارك ٢٠٠٨ vs ٢٠٢٦\nفي ٢٠٠٨، العيد في الحي. الجميع يعرف الجميع.\nفي ٢٠٢٦، العيد في دبي. الجميع من كل مكان. نفس الشعور. 🌙\n\n#EidMubarak #ThenAndNow #DubaiEid #IndianMuslim #MulticulturalDubai #Eid2026 #EidVibes #Dubai"
    },
    {
        "day": 24,
        "title": "Old Salary vs Dubai Salary",
        "prompt_1": "Cinematic Indian realistic illustration, young man carefully counting small salary in Indian rupees on bed, budgeting every rupee, small room, determined face, ultra detailed, bold white text 2014 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same man now making bank transfer on laptop in Dubai home office, sending money to family back home, proud relaxed expression, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2014 vs 2026 — Every rupee counted. Still does. 💰\n\nIn 2014, counting every rupee to survive the month.\nIn 2026, sending money home without checking the balance.\n\nThat's the whole point of the journey. 🙏\n\n٢٠١٤ مقابل ٢٠٢٦ — كل روبية كانت مهمة. لا تزال.\nفي ٢٠١٤، يعدّ كل روبية للبقاء حتى نهاية الشهر.\nفي ٢٠٢٦، يرسل المال إلى المنزل دون التحقق من الرصيد. 💰\n\n#MoneyMindset #ThenAndNow #DubaiLife #IndianExpat #Hustle #Remittance #FamilyFirst #GlowUp"
    },
    {
        "day": 25,
        "title": "Children's School",
        "prompt_1": "Cinematic Indian realistic illustration, Indian government school classroom, crowded benches, chalk blackboard, children in simple uniforms attentive, ultra detailed, bold white text 2000 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, modern Dubai international school, same man dropping his child at premium school entrance, child in smart uniform, tablet in bag, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2000 vs 2026 — I studied so you don't have to struggle 📚\n\nIn 2000, chalk boards, crowded benches, basic textbooks.\nIn 2026, my child has a school I could only dream of.\n\nEvery sacrifice made sense today. 🙏\n\n٢٠٠٠ مقابل ٢٠٢٦ — درست حتى لا تعاني أنت\nفي ٢٠٠٠، سبورة طباشير، مقاعد مزدحمة، كتب بسيطة.\nفي ٢٠٢٦، طفلي في مدرسة كنت أحلم بها. 📚\n\n#Education #ThenAndNow #DubaiSchool #IndianExpat #Parenting #Sacrifice #DreamsDoComeTrue #FamilyFirst"
    },
    {
        "day": 26,
        "title": "Old Friends Reunion",
        "prompt_1": "Cinematic Indian realistic illustration, group of Indian college friends in hostel room, laughing on floor with instant noodles and chai, carefree young faces, ultra detailed, bold white text 2013 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same group of friends now reunited in Dubai rooftop restaurant, business casual, some with grey hair, same laughter, Dubai skyline behind, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2013 vs 2026 — Real friends find their way back 🤝\n\nIn 2013, instant noodles at midnight. Nowhere to be. Nothing to lose.\nIn 2026, Dubai rooftop. Everywhere to be. Everything to be grateful for.\n\nSame chaos. Better shoes. 😂❤️\n\n٢٠١٣ مقابل ٢٠٢٦ — الأصدقاء الحقيقيون يجدون طريقهم دائماً\nفي ٢٠١٣، نودلز فورية في منتصف الليل. لا شيء لنخسره.\nفي ٢٠٢٦، سطح دبي. نفس الضحكات. أحذية أفضل. 😂\n\n#Friendship #ThenAndNow #DubaiLife #CollegeFriends #Reunion #OldFriends #IndianExpat #Nostalgia"
    },
    {
        "day": 27,
        "title": "Cooking Skills",
        "prompt_1": "Cinematic Indian realistic illustration, young Indian bachelor in tiny Dubai kitchen burning simple dal on stove, smoke everywhere, looking helpless, calling mom on phone, ultra detailed, bold white text 2015 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same man now confidently cooking elaborate Indian meal in beautiful Dubai kitchen, wife watching impressed, children excited, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2015 vs 2026 — Necessity is the best teacher 👨‍🍳😂\n\nIn 2015, burnt dal and a panicked call to mom.\nIn 2026, biryani from scratch on a Friday evening.\n\nSurvival taught me things no cooking class could. 😅\n\n٢٠١٥ مقابل ٢٠٢٦ — الحاجة أفضل معلم\nفي ٢٠١٥، عدس محروق ومكالمة مذعورة للأم.\nفي ٢٠٢٦، برياني من الصفر يوم الجمعة. 👨‍🍳\n\n#CookingLife #ThenAndNow #DubaiLife #IndianFood #BatchelorLife #MarriedLife #FunnyButTrue #HomeChef"
    },
    {
        "day": 28,
        "title": "Parents First Visit to Dubai",
        "prompt_1": "Cinematic Indian realistic illustration, Indian parents at Dubai airport arrival, mother in saree looking amazed at the airport, father trying to look calm but equally amazed, son waiting excitedly, ultra detailed, bold white text 2017 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same parents now relaxed on Dubai apartment balcony with tea, watching city view like locals, smiling proudly at their son's home, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2017 vs 2026 — Watching them see my world 🥺\n\nIn 2017, their first time here. Mom gripped my hand at the airport.\nIn 2026, they sit on my balcony with chai like it's their own home.\n\nMaking them proud was always the whole plan. 🙏❤️\n\n٢٠١٧ مقابل ٢٠٢٦ — مشاهدتهم يرون عالمي\nفي ٢٠١٧، زيارتهم الأولى. أمسكت أمي بيدي في المطار.\nفي ٢٠٢٦، يجلسان على شرفتي بالشاي كأنه بيتهم. ❤️\n\n#ParentsVisit #ThenAndNow #DubaiLife #IndianExpat #MomAndDad #FamilyFirst #MakingThemProud #Grateful"
    },
    {
        "day": 29,
        "title": "New Year Celebration",
        "prompt_1": "Cinematic Indian realistic illustration, Indian family watching New Year fireworks on small TV at home, simple celebration, homemade snacks, everyone in pyjamas, happy faces, ultra detailed, bold white text 2010 bottom right, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same family watching spectacular Dubai New Year fireworks live from waterfront, massive crowd, Burj Khalifa lit up, children on shoulders, ultra detailed, bold white text 2026 bottom right, 1:1 ratio",
        "caption": "2010 vs 2026 — We upgraded the fireworks 🎆\n\nIn 2010, New Year on TV. Pyjamas. Homemade snacks. Perfect.\nIn 2026, New Year in Dubai. Burj Khalifa. Thousands around. Also perfect.\n\nHappiness was never about the view. ❤️\n\n٢٠١٠ مقابل ٢٠٢٦ — طورنا الألعاب النارية\nفي ٢٠١٠، رأس السنة على التلفاز. بيجامات. طعام منزلي. مثالي.\nفي ٢٠٢٦، رأس السنة في دبي. برج خليفة. آلاف الناس. مثالي أيضاً. 🎆\n\n#NewYear #ThenAndNow #DubaiNewYear #BurjKhalifa #IndianExpat #FamilyFirst #Grateful #2026"
    },
    {
        "day": 30,
        "title": "The Journey",
        "prompt_1": "Cinematic Indian realistic illustration, young determined Indian man at dawn standing outside small house with one suitcase, looking at horizon with hope, simple neighbourhood, ultra detailed, bold white text THE BEGINNING bottom, 1:1 ratio",
        "prompt_2": "Cinematic Indian realistic illustration, same man now standing on Dubai rooftop at dawn, family behind him, confident relaxed posture, city skyline ahead, peaceful smile, ultra detailed, bold white text THE ARRIVAL bottom, 1:1 ratio",
        "caption": "The Beginning vs The Arrival — 30 days of stories. One truth. 🌅\n\nEvery post this month was one chapter of the same book.\nA boy who left home to build a home.\n\nThank you for being part of the journey. It's far from over. 🙏✨\n\nالبداية vs الوصول — ٣٠ يوماً من القصص. حقيقة واحدة.\nكل منشور هذا الشهر كان فصلاً من نفس الكتاب.\nفتى غادر بيته لبناء بيت.\nشكراً لكونكم جزءاً من الرحلة. ❤️\n\n#TheJourney #DubaiLife #IndianExpat #ThenAndNow #30Days #Grateful #Hustle #HomeAwayFromHome #Dubai"
    }
]


def run_thenvsnow(day_num):
    """Run a specific Then vs Now post by day number (1-30)."""
    if day_num < 1 or day_num > len(POSTS_30):
        print(f"❌ Day must be between 1 and {len(POSTS_30)}")
        return
    post = POSTS_30[day_num - 1]
    print(f"\n{'='*55}")
    print(f"  📅  Day {day_num}: {post['title']}")
    print(f"{'='*55}")
    os.makedirs("output", exist_ok=True)
    img1     = generate_image(post["prompt_1"], f"output/thenvsnow_day{day_num:02d}_a.jpg")
    img2     = generate_image(post["prompt_2"], f"output/thenvsnow_day{day_num:02d}_b.jpg")
    combined = combine_and_crop(img1, img2, f"output/thenvsnow_day{day_num:02d}_final.jpg")
    url      = upload_to_imgbb(combined)
    mid      = instagram_post(url, post["caption"])
    print(f"\n  ✅ Day {day_num} LIVE on @maddy_4589! ID: {mid}\n")
    return mid

