"""
VIRAL KIDS VIDEO GENERATOR — Headless Edition
Renders a 90-second sea-animals counting video (1-10) directly to MP4
using Pillow + NumPy + OpenCV. No browser or screen recording needed.

Usage:
    python make_viral_video.py
Output:
    viral_kids_video.mp4
"""

import math
import os
import random
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── Config ───────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 405, 720
FPS = 30
DURATION = 90           # seconds
OUTPUT = "viral_kids_video.mp4"
TOTAL_FRAMES = DURATION * FPS

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

# ── Animals ──────────────────────────────────────────────────────────────────
ANIMALS = [
    {"num": 1,  "name": "Giant Whale Shark",  "hook": "BIGGEST FISH!",   "color": (30,  144, 255), "shape": "diamond"},
    {"num": 2,  "name": "Dancing Seahorses",  "hook": "TWIRL TIME!",     "color": (255, 140,   0), "shape": "circle"},
    {"num": 3,  "name": "Sparkle Starfish",   "hook": "GLOWING!",        "color": (255, 215,   0), "shape": "star"},
    {"num": 4,  "name": "Silly Clownfish",    "hook": "HIDE & SEEK!",    "color": (255,  69,   0), "shape": "circle"},
    {"num": 5,  "name": "Glowing Jellyfish",  "hook": "RAVE MODE!",      "color": (186,  85, 211), "shape": "diamond"},
    {"num": 6,  "name": "Super Turtles",      "hook": "NINJA CREW!",     "color": ( 50, 205,  50), "shape": "star"},
    {"num": 7,  "name": "Wavy Octopus",       "hook": "TENTACLE DANCE!", "color": (255, 105, 180), "shape": "circle"},
    {"num": 8,  "name": "Clapping Crabs",     "hook": "SNAP SNAP!",      "color": (220,  20,  60), "shape": "diamond"},
    {"num": 9,  "name": "Happy Dolphins",     "hook": "JUMP SPLASH!",    "color": (100, 200, 255), "shape": "circle"},
    {"num": 10, "name": "Playful Sea Lions",  "hook": "CLAP ALONG!",     "color": (205, 133,  63), "shape": "star"},
]

# Segment timing
INTRO_END   = 5 * FPS           # 0–5 s
OUTRO_START = 85 * FPS          # 85–90 s
NUM_DUR     = 8 * FPS           # 8 s per number

# ── Fonts ────────────────────────────────────────────────────────────────────
def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

fnt_huge  = load_font(FONT_BOLD, 180)
fnt_large = load_font(FONT_BOLD,  52)
fnt_med   = load_font(FONT_BOLD,  34)
fnt_small = load_font(FONT_REG,   26)

# ── Particle system ──────────────────────────────────────────────────────────
random.seed(42)
PARTICLES = [
    {
        "x": random.uniform(0, WIDTH),
        "y": random.uniform(0, HEIGHT),
        "r": random.uniform(3, 9),
        "speed": random.uniform(0.3, 1.2),
        "hue": random.choice([(255, 215, 0), (255, 105, 180), (100, 200, 255), (186, 85, 211)]),
    }
    for _ in range(50)
]

# ── Drawing helpers ───────────────────────────────────────────────────────────

def make_gradient_bg():
    """Deep ocean gradient as numpy array (H, W, 3) uint8."""
    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(26  * (1 - t) + 10 * t)
        g = int(26  * (1 - t) + 60 * t)
        b = int(94  * (1 - t) + 80 * t)
        img[y, :] = (r, g, b)
    return img.astype(np.uint8)

BG_BASE = make_gradient_bg()


def draw_particles(draw, t):
    for p in PARTICLES:
        y = (p["y"] - t * p["speed"] * 60) % (HEIGHT + 20) - 10
        x = p["x"] + math.sin(t * 1.5 + p["speed"]) * 8
        alpha_factor = 0.5 + 0.4 * math.sin(t * 3 + p["speed"] * 10)
        c = tuple(int(v * alpha_factor) for v in p["hue"])
        r = p["r"]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=c)


def draw_border(draw, pulse):
    w = 3 + int(pulse * 2)
    color = (255, 179, 71)
    draw.rectangle([w//2, w//2, WIDTH - w//2, HEIGHT - w//2],
                   outline=color, width=w)


def centered_text(draw, text, y, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)


def draw_animal_icon(draw, cx, cy, r, shape, color):
    """Draw a small icon (circle / diamond / star) for each animal unit."""
    if shape == "circle":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    elif shape == "diamond":
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        draw.polygon(pts, fill=color)
    elif shape == "star":
        pts = []
        for i in range(10):
            angle = math.radians(-90 + i * 36)
            rad = r if i % 2 == 0 else r * 0.45
            pts.append((cx + rad * math.cos(angle), cy + rad * math.sin(angle)))
        draw.polygon(pts, fill=color)


def draw_animal_row(draw, count, color, shape, t):
    """Row of animal icons near the bottom, bobbing with sin."""
    icon_r = 14
    spacing = min(36, (WIDTH - 40) // max(count, 1))
    total_w = spacing * (count - 1) + icon_r * 2
    start_x = (WIDTH - total_w) // 2 + icon_r
    base_y = HEIGHT - 90
    for i in range(count):
        bob = math.sin(t * 6 + i * 0.8) * 6
        cx = start_x + i * spacing
        cy = base_y + bob
        # subtle glow ring
        glow = tuple(min(255, int(v * 0.4)) for v in color)
        draw.ellipse([cx - icon_r - 4, cy - icon_r - 4,
                      cx + icon_r + 4, cy + icon_r + 4], fill=glow)
        draw_animal_icon(draw, cx, int(cy), icon_r, shape, color)


def draw_orbit_ring(draw, cx, cy, base_r, prog, t):
    """Expanding ring + small orbiting dots around the big number."""
    r = int(base_r + prog * 40)
    alpha = max(0, int(200 * (1 - prog * 0.6)))
    ring_col = (255, 200, 80, alpha)
    draw.arc([cx - r, cy - r, cx + r, cy + r], 0, 360,
             fill=(255, 200, 80), width=4)
    # orbiting dots
    for i in range(6):
        angle = t * 90 + i * 60
        ox = cx + r * math.cos(math.radians(angle))
        oy = cy + r * math.sin(math.radians(angle)) * 0.55
        dr = 5
        draw.ellipse([ox - dr, oy - dr, ox + dr, oy + dr],
                     fill=(255, 220, 90))


def draw_number_segment(draw, animal, prog, t):
    """Render one number card (8-second slot)."""
    num   = animal["num"]
    color = animal["color"]
    shape = animal["shape"]

    # bounce scale via sin
    bob = math.sin(t * 10) * 0.06
    scale = 1.0 + bob

    # ── Orbit ring ──
    cx, cy = WIDTH // 2, HEIGHT // 3
    draw_orbit_ring(draw, cx, cy - 20, 85, prog, t)

    # ── Big number ──
    num_str = str(num)
    bbox = draw.textbbox((0, 0), num_str, font=fnt_huge)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    nx = cx - tw // 2
    ny = cy - th // 2 - 20 + int(math.sin(t * 8) * 8)

    # shadow
    draw.text((nx + 4, ny + 4), num_str, font=fnt_huge, fill=(0, 0, 0, 120))
    # main number — color tinted white
    num_col = tuple(min(255, 180 + c // 3) for c in color)
    draw.text((nx, ny), num_str, font=fnt_huge, fill=num_col)

    # ── Hook text ──
    hook_y = cy + th // 2 + 14
    centered_text(draw, animal["hook"], hook_y, fnt_large, (255, 228, 132))

    # ── Animal name ──
    name_y = hook_y + 62
    centered_text(draw, animal["name"], name_y, fnt_med, (220, 220, 255))

    # ── Animal row ──
    draw_animal_row(draw, num, color, shape, t)


def draw_intro(draw, t):
    pulse = 0.5 + 0.5 * math.sin(t * 6)
    y1 = HEIGHT // 2 - 110
    centered_text(draw, "COUNTING", y1,       fnt_huge,  (255, 228, 100))
    centered_text(draw, "1  to  10", y1 + 175, fnt_large, (180, 230, 255))
    centered_text(draw, "SEA  ANIMALS", y1 + 245, fnt_med, (255, 160, 80))

    # pulsing dots row
    for i in range(10):
        x = 30 + i * (WIDTH - 60) // 9
        y = HEIGHT - 130
        r = int(8 + pulse * 5)
        c = ANIMALS[i]["color"]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=c)


def draw_outro(draw, t):
    pulse = 0.5 + 0.5 * math.sin(t * 8)
    y1 = HEIGHT // 2 - 100
    centered_text(draw, "YOU'RE A", y1,        fnt_large, (255, 215, 0))
    centered_text(draw, "STAR!",    y1 + 70,   fnt_huge,  (255, 215, 0))
    centered_text(draw, "Share with friends!", y1 + 255, fnt_small,
                  (200, 200, 255))
    centered_text(draw, "#KidsLearning #Counting", y1 + 295, fnt_small,
                  (160, 160, 220))

    # celebration dots
    for i in range(15):
        angle = t * 80 + i * 24
        rad = 120 + pulse * 30
        x = WIDTH // 2 + rad * math.cos(math.radians(angle))
        y = HEIGHT // 2 - 20 + rad * 0.5 * math.sin(math.radians(angle))
        r = int(6 + pulse * 3)
        c = ANIMALS[i % len(ANIMALS)]["color"]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=c)


def draw_viral_badge(draw):
    bw, bh = 160, 30
    bx, by = WIDTH - bw - 10, 14
    draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=14,
                            fill=(220, 30, 60))
    centered_at = bx + bw // 2
    bbox = draw.textbbox((0, 0), "TRENDING 1-10", font=fnt_small)
    tw = bbox[2] - bbox[0]
    draw.text((centered_at - tw // 2, by + 4), "TRENDING 1-10",
              font=fnt_small, fill=(255, 255, 255))


def draw_progress_bar(draw, frame_idx):
    prog = frame_idx / TOTAL_FRAMES
    bar_w = int((WIDTH - 20) * prog)
    draw.rectangle([10, HEIGHT - 12, WIDTH - 10, HEIGHT - 6],
                   fill=(60, 60, 80))
    if bar_w > 0:
        draw.rectangle([10, HEIGHT - 12, 10 + bar_w, HEIGHT - 6],
                       fill=(255, 100, 100))


# ── Main render loop ──────────────────────────────────────────────────────────

def render_frame(frame_idx):
    t = frame_idx / FPS          # time in seconds
    t_rad = t                    # same, used for trig (radians per second)

    # Base gradient
    bg = BG_BASE.copy()
    img = Image.fromarray(bg, "RGB")
    draw = ImageDraw.Draw(img, "RGBA")

    # Particles
    draw_particles(draw, t_rad)

    # Content
    if frame_idx < INTRO_END:
        draw_intro(draw, t_rad)
    elif frame_idx >= OUTRO_START:
        draw_outro(draw, t_rad)
    else:
        slot = (frame_idx - INTRO_END) // NUM_DUR
        slot = min(slot, 9)
        prog = ((frame_idx - INTRO_END) % NUM_DUR) / NUM_DUR
        draw_number_segment(draw, ANIMALS[slot], prog, t_rad)

    # Overlays
    draw_border(draw, 0.5 + 0.5 * math.sin(t_rad * 3))
    draw_viral_badge(draw)
    draw_progress_bar(draw, frame_idx)

    # Convert PIL → BGR numpy for OpenCV
    return cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def main():
    print("=" * 52)
    print("  VIRAL KIDS VIDEO GENERATOR — Headless Edition")
    print("=" * 52)
    print(f"  Resolution : {WIDTH}x{HEIGHT} @ {FPS} fps")
    print(f"  Duration   : {DURATION}s  ({TOTAL_FRAMES} frames)")
    print(f"  Output     : {OUTPUT}")
    print("=" * 52)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(OUTPUT, fourcc, FPS, (WIDTH, HEIGHT))

    if not writer.isOpened():
        print("ERROR: Could not open VideoWriter. Check OpenCV build.")
        sys.exit(1)

    for i in range(TOTAL_FRAMES):
        frame = render_frame(i)
        writer.write(frame)

        if i % FPS == 0:
            pct = 100 * i // TOTAL_FRAMES
            bar = "#" * (pct // 4) + "-" * (25 - pct // 4)
            print(f"  [{bar}] {pct:3d}%  frame {i}/{TOTAL_FRAMES}", end="\r")

    writer.release()
    print(f"\n\n  Done! Saved: {OUTPUT}")
    size_mb = os.path.getsize(OUTPUT) / (1024 * 1024)
    print(f"  File size  : {size_mb:.1f} MB")
    print("\n  Upload to TikTok / Instagram Reels / YouTube Shorts")
    print("  Hashtags   : #counting #kidslearning #seaanimals #viral")


if __name__ == "__main__":
    main()
