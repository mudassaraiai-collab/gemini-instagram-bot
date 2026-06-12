"""
VIRAL KIDS VIDEO GENERATOR — Headless with Voice & Emoji Animals
• Animal pictures : NotoColorEmoji (rendered at native 109 px, resized)
• Voice           : espeak-ng (offline TTS, no internet needed)
• Background music: NumPy-synthesised pentatonic melody
• Output          : viral_kids_video.mp4 (video + AAC audio via ffmpeg)

Usage:
    python make_viral_video.py
"""

import math, os, sys, wave, subprocess, random, struct
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── Config ────────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 405, 720
FPS           = 30
DURATION      = 90
TOTAL_FRAMES  = DURATION * FPS
TMP_VIDEO     = "/tmp/viral_silent.mp4"
TMP_AUDIO     = "/tmp/viral_audio.wav"
OUTPUT        = "viral_kids_video.mp4"

FONT_BOLD  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

SR = 44100   # audio sample rate

# ── Animals ───────────────────────────────────────────────────────────────────
ANIMALS = [
    {"num":1,  "name":"Giant Whale Shark",  "hook":"BIGGEST FISH!",   "emoji":"🦈", "color":(30,144,255)},
    {"num":2,  "name":"Dancing Seahorses",  "hook":"TWIRL TIME!",     "emoji":"🐟", "color":(255,140,0)},
    {"num":3,  "name":"Sparkle Starfish",   "hook":"GLOWING!",        "emoji":"⭐", "color":(255,215,0)},
    {"num":4,  "name":"Silly Clownfish",    "hook":"HIDE & SEEK!",    "emoji":"🐠", "color":(255,80,0)},
    {"num":5,  "name":"Glowing Jellyfish",  "hook":"RAVE MODE!",      "emoji":"🪼", "color":(186,85,211)},
    {"num":6,  "name":"Super Turtles",      "hook":"NINJA CREW!",     "emoji":"🐢", "color":(50,205,50)},
    {"num":7,  "name":"Wavy Octopus",       "hook":"TENTACLE DANCE!", "emoji":"🐙", "color":(255,105,180)},
    {"num":8,  "name":"Clapping Crabs",     "hook":"SNAP SNAP!",      "emoji":"🦀", "color":(220,20,60)},
    {"num":9,  "name":"Happy Dolphins",     "hook":"JUMP SPLASH!",    "emoji":"🐬", "color":(100,200,255)},
    {"num":10, "name":"Playful Sea Lions",  "hook":"CLAP ALONG!",     "emoji":"🦭", "color":(205,133,63)},
]

INTRO_END   = 5  * FPS
OUTRO_START = 85 * FPS
NUM_DUR     = 8  * FPS

# ── Fonts ─────────────────────────────────────────────────────────────────────
def _font(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

fnt_huge  = _font(FONT_BOLD, 160)
fnt_large = _font(FONT_BOLD,  52)
fnt_med   = _font(FONT_BOLD,  34)
fnt_small = _font(FONT_REG,   26)

# NotoColorEmoji only ships bitmaps at size 109; render there, then resize.
_emoji_font = ImageFont.truetype(EMOJI_FONT, 109)

def render_emoji(char: str, size: int) -> Image.Image:
    """Return a square RGBA image of `char` resized to `size`×`size`."""
    canvas = Image.new("RGBA", (140, 140), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)
    bb = d.textbbox((0, 0), char, font=_emoji_font)
    ox = (140 - (bb[2]-bb[0])) // 2 - bb[0]
    oy = (140 - (bb[3]-bb[1])) // 2 - bb[1]
    d.text((ox, oy), char, font=_emoji_font, embedded_color=True)
    return canvas.resize((size, size), Image.LANCZOS)


def paste_emoji(pil_img: Image.Image, char: str, cx: int, cy: int, size: int):
    """Paste emoji centred at (cx, cy)."""
    em = render_emoji(char, size)
    pil_img.paste(em, (cx - size//2, cy - size//2), em)


# ── Pre-render emoji cache ────────────────────────────────────────────────────
_CACHE: dict = {}

def get_emoji(char, size):
    key = (char, size)
    if key not in _CACHE:
        _CACHE[key] = render_emoji(char, size)
    return _CACHE[key]

def paste_cached(pil_img, char, cx, cy, size):
    em = get_emoji(char, size)
    pil_img.paste(em, (cx - size//2, cy - size//2), em)


# ── Background + particles ────────────────────────────────────────────────────
random.seed(42)
_PARTICLES = [
    {"x": random.uniform(0, WIDTH), "y": random.uniform(0, HEIGHT),
     "r": random.uniform(3, 9),     "speed": random.uniform(0.3, 1.2),
     "hue": random.choice([(255,215,0),(255,105,180),(100,200,255),(186,85,211)])}
    for _ in range(50)
]

def _make_bg():
    arr = np.zeros((HEIGHT, WIDTH, 3), np.float32)
    for y in range(HEIGHT):
        t = y / HEIGHT
        arr[y] = (26*(1-t)+10*t, 26*(1-t)+60*t, 94*(1-t)+80*t)
    return arr.astype(np.uint8)

_BG = _make_bg()


def draw_particles(draw, t):
    for p in _PARTICLES:
        y = (p["y"] - t * p["speed"] * 60) % (HEIGHT + 20) - 10
        x = p["x"] + math.sin(t * 1.5 + p["speed"]) * 8
        a = 0.5 + 0.4 * math.sin(t * 3 + p["speed"] * 10)
        c = tuple(int(v * a) for v in p["hue"])
        r = p["r"]
        draw.ellipse([x-r, y-r, x+r, y+r], fill=c)


# ── Text helpers ──────────────────────────────────────────────────────────────
def center_x(draw, text, font):
    bb = draw.textbbox((0, 0), text, font=font)
    return (WIDTH - (bb[2]-bb[0])) // 2

def ctext(draw, text, y, font, fill):
    draw.text((center_x(draw, text, font), y), text, font=font, fill=fill)


# ── Number card ───────────────────────────────────────────────────────────────
def draw_number_card(pil_img, draw, animal, prog, t):
    num   = animal["num"]
    color = animal["color"]
    emoji = animal["emoji"]

    cx = WIDTH // 2
    ring_cy = 185

    # Orbit ring
    r = int(88 + prog * 38)
    draw.arc([cx-r, ring_cy-r, cx+r, ring_cy+r], 0, 360,
             fill=(255, 200, 80), width=4)
    for i in range(6):
        angle = t * 90 + i * 60
        ox = cx + r * math.cos(math.radians(angle))
        oy = ring_cy + r * 0.55 * math.sin(math.radians(angle))
        draw.ellipse([ox-5, oy-5, ox+5, oy+5], fill=(255, 220, 90))

    # Big number
    num_str = str(num)
    bb = draw.textbbox((0, 0), num_str, font=fnt_huge)
    tw, th = bb[2]-bb[0], bb[3]-bb[1]
    bob = int(math.sin(t * 8) * 7)
    nx = (WIDTH - tw) // 2
    ny = ring_cy - th//2 - 15 + bob
    draw.text((nx+4, ny+4), num_str, font=fnt_huge, fill=(0, 0, 0, 110))
    nc = tuple(min(255, 180 + c//3) for c in color)
    draw.text((nx, ny), num_str, font=fnt_huge, fill=nc)

    # Hook text
    hook_y = ring_cy + th//2 + 14
    ctext(draw, animal["hook"], hook_y, fnt_large, (255, 228, 132))

    # Featured animal emoji (large, animated bob)
    emoji_cy = hook_y + 90
    bob_e = int(math.sin(t * 7 + 1) * 7)
    paste_cached(pil_img, emoji, cx, emoji_cy + bob_e, 80)

    # Animal name
    name_y = emoji_cy + 55
    ctext(draw, animal["name"], name_y, fnt_med, (220, 220, 255))

    # Counting emoji grid
    grid_cy = name_y + 58
    _draw_grid(pil_img, emoji, num, grid_cy, t)


def _draw_grid(pil_img, emoji, count, cy, t):
    """Draw count × emoji in a centred row (or 2 rows if count > 5)."""
    if count <= 5:
        cols, rows_n = count, 1
    else:
        cols = math.ceil(count / 2)
        rows_n = 2

    size = 52 if count <= 3 else 42 if count <= 6 else 34 if count <= 9 else 28
    cell = size + 8
    row_h = size + 10

    total_w = cols * cell
    x0 = (WIDTH - total_w) // 2 + cell // 2
    y0 = cy - (rows_n - 1) * row_h // 2

    for i in range(count):
        col = i % cols
        row = i // cols
        bob = int(math.sin(t * 6 + i * 0.8) * 4)
        cx = x0 + col * cell
        cy_i = y0 + row * row_h + bob
        paste_cached(pil_img, emoji, cx, cy_i, size)


# ── Intro / Outro ─────────────────────────────────────────────────────────────
def draw_intro(pil_img, draw, t):
    ctext(draw, "COUNTING",   HEIGHT//2 - 110, fnt_huge,  (255, 228, 100))
    ctext(draw, "1  to  10",  HEIGHT//2 +  60, fnt_large, (180, 230, 255))
    ctext(draw, "SEA ANIMALS",HEIGHT//2 + 125, fnt_med,   (255, 160,  80))
    cell = (WIDTH - 20) // 10
    for i, a in enumerate(ANIMALS):
        cx = 10 + cell * i + cell // 2
        bob = int(math.sin(t * 5 + i * 0.7) * 6)
        paste_cached(pil_img, a["emoji"], cx, HEIGHT - 80 + bob, 28)


def draw_outro(pil_img, draw, t):
    pulse = 0.5 + 0.5 * math.sin(t * 8)
    ctext(draw, "YOU'RE A",          HEIGHT//2 - 105, fnt_large, (255, 215, 0))
    ctext(draw, "STAR!",             HEIGHT//2 -  30, fnt_huge,  (255, 215, 0))
    ctext(draw, "Share with friends!", HEIGHT//2 + 150, fnt_small, (200, 200, 255))
    for i in range(20):
        angle = t * 80 + i * 18
        rad = 110 + pulse * 30
        x = int(WIDTH//2 + rad * math.cos(math.radians(angle)))
        y = int(HEIGHT//2 + 20 + rad * 0.5 * math.sin(math.radians(angle)))
        r = int(5 + pulse * 3)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=ANIMALS[i % 10]["color"])


# ── Overlays ──────────────────────────────────────────────────────────────────
def draw_badge(draw):
    bw, bh = 160, 30
    bx, by = WIDTH - bw - 10, 14
    draw.rounded_rectangle([bx, by, bx+bw, by+bh], radius=14, fill=(220, 30, 60))
    bb = draw.textbbox((0, 0), "TRENDING 1-10", font=fnt_small)
    draw.text((bx + (bw - (bb[2]-bb[0]))//2, by+4),
              "TRENDING 1-10", font=fnt_small, fill=(255, 255, 255))

def draw_progress(draw, fi):
    bw = int((WIDTH - 20) * fi / TOTAL_FRAMES)
    draw.rectangle([10, HEIGHT-12, WIDTH-10, HEIGHT-6], fill=(60, 60, 80))
    if bw > 0:
        draw.rectangle([10, HEIGHT-12, 10+bw, HEIGHT-6], fill=(255, 100, 100))

def draw_border(draw, t):
    w = 3 + int((0.5 + 0.5*math.sin(t*3)) * 2)
    draw.rectangle([w//2, w//2, WIDTH-w//2, HEIGHT-w//2],
                   outline=(255, 179, 71), width=w)


# ── Frame renderer ────────────────────────────────────────────────────────────
def render_frame(fi: int) -> np.ndarray:
    t = fi / FPS
    img  = Image.fromarray(_BG.copy(), "RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    draw_particles(draw, t)

    if fi < INTRO_END:
        draw_intro(img, draw, t)
    elif fi >= OUTRO_START:
        draw_outro(img, draw, t)
    else:
        slot = min((fi - INTRO_END) // NUM_DUR, 9)
        prog = ((fi - INTRO_END) % NUM_DUR) / NUM_DUR
        draw_number_card(img, draw, ANIMALS[slot], prog, t)

    draw_border(draw, t)
    draw_badge(draw)
    draw_progress(draw, fi)

    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


# ── Audio ─────────────────────────────────────────────────────────────────────
def _espeak(text: str, wav_path: str):
    subprocess.run(
        ["espeak-ng", "-v", "en+f3", "-s", "145", "-p", "65", "-w", wav_path, text],
        check=True, capture_output=True
    )

def _load_wav_mono(path: str, target_sr: int = SR) -> np.ndarray:
    """Load WAV → float32 array resampled to target_sr."""
    with wave.open(path, "rb") as wf:
        src_sr = wf.getframerate()
        raw    = wf.readframes(wf.getnframes())
        arr    = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    # Simple linear resample if needed
    if src_sr != target_sr:
        ratio   = target_sr / src_sr
        new_len = int(len(arr) * ratio)
        arr     = np.interp(
            np.linspace(0, len(arr)-1, new_len),
            np.arange(len(arr)), arr
        )
    return arr

def _background_music(n: int) -> np.ndarray:
    notes = [261.63, 329.63, 392.00, 440.00, 523.25,
             440.00, 392.00, 329.63, 261.63, 392.00]
    beat  = 0.35
    audio = np.zeros(n, dtype=np.float32)
    i, t0 = 0, 0.0
    while t0 < DURATION:
        freq  = notes[i % len(notes)]
        s     = int(t0 * SR)
        e     = min(int((t0 + beat) * SR), n)
        if s >= n:
            break
        tt    = np.linspace(0, beat, e - s)
        env   = np.exp(-tt * 9) * 0.35
        audio[s:e] += env * np.sin(2 * np.pi * freq * tt)
        audio[s:e] += env * 0.25 * np.sin(2 * np.pi * freq * 2 * tt)
        t0 += beat
        i  += 1
    return audio

def build_audio(tmp_dir: str = "/tmp") -> np.ndarray:
    n     = int(DURATION * SR)
    track = _background_music(n) * 0.3

    for a in ANIMALS:
        wav = os.path.join(tmp_dir, f"speech_{a['num']}.wav")
        if not os.path.exists(wav):
            num_word = ["", "One","Two","Three","Four","Five",
                        "Six","Seven","Eight","Nine","Ten"][a["num"]]
            _espeak(f"{num_word}! {a['name']}!", wav)
            print(f"    voice: {num_word}...")

        speech = _load_wav_mono(wav)
        seg_start   = 5 + (a["num"] - 1) * 8
        insert_at   = int((seg_start + 0.35) * SR)
        end_at      = min(insert_at + len(speech), n)
        track[insert_at:end_at] += speech[:end_at - insert_at] * 1.8

    peak = np.max(np.abs(track))
    if peak > 0:
        track = track / peak * 0.88
    return track

def _save_wav(audio: np.ndarray, path: str):
    data = (audio * 32767).astype(np.int16)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(data.tobytes())

def mux(video: str, audio: str, out: str):
    subprocess.run(
        ["ffmpeg", "-y", "-i", video, "-i", audio,
         "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", out],
        check=True, capture_output=True
    )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 56)
    print("  VIRAL KIDS VIDEO — Voice + Emoji Animals (Headless)")
    print("=" * 56)
    print(f"  {WIDTH}×{HEIGHT}  {FPS}fps  {DURATION}s  →  {OUTPUT}")
    print("=" * 56)

    # Pre-warm emoji cache for all animals at sizes used
    print("\n  Pre-rendering emoji cache...")
    for a in ANIMALS:
        for sz in [80, 52, 42, 34, 28]:
            get_emoji(a["emoji"], sz)
    print("  Cache ready.")

    # ── Video ──────────────────────────────────────────────
    print("\n  Rendering video frames...")
    writer = cv2.VideoWriter(
        TMP_VIDEO, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT)
    )
    if not writer.isOpened():
        sys.exit("ERROR: Cannot open VideoWriter")

    for fi in range(TOTAL_FRAMES):
        writer.write(render_frame(fi))
        if fi % FPS == 0:
            pct = 100 * fi // TOTAL_FRAMES
            bar = "#" * (pct // 4) + "-" * (25 - pct // 4)
            print(f"  [{bar}] {pct:3d}%", end="\r")
    writer.release()
    print(f"\n  Video frames done: {TMP_VIDEO}")

    # ── Audio ──────────────────────────────────────────────
    print("\n  Generating audio (music + voice)...")
    audio = build_audio()
    _save_wav(audio, TMP_AUDIO)
    print(f"  Audio saved: {TMP_AUDIO}")

    # ── Mux ────────────────────────────────────────────────
    print(f"\n  Muxing → {OUTPUT}...")
    mux(TMP_VIDEO, TMP_AUDIO, OUTPUT)
    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"  Done!  {OUTPUT}  ({size_mb:.1f} MB)")
    print("\n  Hashtags: #counting #kidslearning #seaanimals #viral")


if __name__ == "__main__":
    main()
