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
    i1 = Image.open(img1_path).convert("RGB")
    i2 = Image.open(img2_path).convert("RGB")
    w = 1080
    h1 = int(i1.height * w / i1.width)
    h2 = int(i2.height * w / i2.width)
    i1 = i1.resize((w, h1), Image.LANCZOS)
    i2 = i2.resize((w, h2), Image.LANCZOS)
    combined = Image.new("RGB", (w, h1 + h2))
    combined.paste(i1, (0, 0))
    combined.paste(i2, (0, h1))
    # Crop to 4:5 Instagram portrait ratio (1080x1350)
    target_h = 1350
    total_h = h1 + h2
    if total_h >= target_h:
        top = (total_h - target_h) // 2
        combined = combined.crop((0, top, w, top + target_h))
    else:
        padded = Image.new("RGB", (w, target_h), (255, 255, 255))
        padded.paste(combined, (0, (target_h - total_h) // 2))
        combined = padded
    combined.save(output_path, quality=95)
    print(f"  🖼️  Saved: {output_path} (1080x1350)")
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
