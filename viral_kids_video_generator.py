"""
VIRAL KIDS VIDEO GENERATOR
Creates a 90-second TikTok/Instagram-style counting video as MP4
"""

import subprocess
import time
import os
import sys
from datetime import datetime
from PIL import ImageGrab
import numpy as np

# ========== CONFIGURATION ==========
VIDEO_WIDTH = 405
VIDEO_HEIGHT = 720
TOTAL_DURATION = 95  # 90 seconds + 5 seconds buffer
OUTPUT_FILE = "viral_kids_video.mp4"
HTML_FILE = "viral_kids_final.html"
FPS = 30

# ========== HTML CONTENT ==========
HTML_CONTENT = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>🔥 VIRAL KIDS COUNTING 1-10 | Sea Animals 🔥</title>
<style>
*{margin:0;padding:0;box-sizing:border-box;user-select:none;-webkit-tap-highlight-color:transparent}
body{background:linear-gradient(135deg,#0a0a2a,#1a0a2a);display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:'Comic Neue','Comic Sans MS',sans-serif;padding:12px}
.video-container{position:relative;width:100%;max-width:405px;aspect-ratio:9/16;border-radius:44px;box-shadow:0 30px 50px rgba(0,0,0,0.6),0 0 0 6px rgba(255,255,255,0.1);overflow:hidden;background:#0b3b4f}
canvas{position:absolute;top:0;left:0;width:100%;height:100%;display:block;cursor:pointer}
.controls{position:absolute;bottom:16px;left:12px;right:12px;display:flex;gap:10px;z-index:40;pointer-events:auto}
button{background:rgba(0,0,0,0.75);backdrop-filter:blur(12px);border:1.5px solid rgba(255,255,255,0.25);font-family:inherit;font-size:0.8rem;font-weight:bold;padding:10px 18px;border-radius:40px;cursor:pointer;color:white}
button:active{transform:scale(0.94)}
.progress-wrapper{flex:1;background:rgba(255,255,255,0.3);border-radius:30px;height:6px;overflow:hidden}
.progress-bar{width:0%;height:100%;background:linear-gradient(90deg,#ff4d6d,#ffb347);border-radius:30px;transition:width 0.05s linear}
.caption-badge{position:absolute;bottom:80px;left:16px;right:80px;background:rgba(0,0,0,0.7);backdrop-filter:blur(16px);padding:12px 18px;border-radius:60px;font-size:0.95rem;font-weight:bold;color:white;text-align:center;border-left:5px solid #ffb347;pointer-events:none;z-index:35}
.viral-badge{position:absolute;top:20px;right:16px;background:linear-gradient(135deg,#ff2d55,#ff6b35);padding:6px 14px;border-radius:40px;font-size:0.7rem;font-weight:bold;color:white;z-index:40;animation:pulse 1.2s infinite}
.music-note{position:absolute;bottom:140px;left:16px;background:rgba(0,0,0,0.6);backdrop-filter:blur(8px);border-radius:30px;padding:5px 12px;font-size:0.65rem;color:#ffb347;z-index:40;pointer-events:none}
.like-animation{position:absolute;right:20px;bottom:140px;font-size:2rem;opacity:0;pointer-events:none;z-index:45}
@keyframes floatUp{0%{opacity:0;transform:translateY(0) scale(0.4)}25%{opacity:1;transform:translateY(-15px) scale(1.2)}100%{opacity:0;transform:translateY(-90px) scale(0.8)}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.85}}
</style>
</head>
<body>
<div class="video-container">
<canvas id="canvas" width="540" height="960"></canvas>
<div class="caption-badge" id="captionText">🎵 AUTOMATED RECORDING MODE 🎵</div>
<div class="viral-badge">🔥 TRENDING 1-10 🔥</div>
<div class="music-note" id="musicNote">🎵 MUSIC ON 🎵</div>
<div class="like-animation" id="likeAnim">❤️</div>
</div>
<script>
(function(){
const canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d');
canvas.width=540;canvas.height=960;
const TOTAL=90;let startTime=null,animId=null,isPlaying=true,voiceMuted=false,musicEnabled=true,audioCtx=null,musicInterval=null,currentNum=0,lastSpoken=-1;
const animals=[
{name:"ONE Giant Whale Shark",emoji:"🐋",hook:"BIGGEST FISH!"},{name:"TWO Dancing Seahorses",emoji:"🐠🐠",hook:"TWIRL TIME!"},{name:"THREE Sparkle Starfish",emoji:"⭐✨⭐",hook:"GLOWING!"},{name:"FOUR Silly Clownfish",emoji:"🐟🐟🐟🐟",hook:"HIDE & SEEK!"},{name:"FIVE Glowing Jellyfish",emoji:"🪼✨🪼",hook:"RAVE MODE!"},{name:"SIX Super Turtles",emoji:"🐢🐢🐢🐢🐢🐢",hook:"NINJA CREW!"},{name:"SEVEN Wavy Octopus",emoji:"🐙🐙🐙🐙🐙🐙🐙",hook:"TENTACLE DANCE!"},{name:"EIGHT Clapping Crabs",emoji:"🦀🦀🦀🦀🦀🦀🦀🦀",hook:"SNAP SNAP!"},{name:"NINE Happy Dolphins",emoji:"🐬🐬🐬🐬🐬🐬🐬🐬🐬",hook:"JUMP SPLASH!"},{name:"TEN Playful Sea Lions",emoji:"🦭🦭🦭🦭🦭🦭🦭🦭🦭🦭",hook:"CLAP ALONG!"}
];
function speak(n,name){if(voiceMuted)return;if(window.speechSynthesis.speaking)window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(n+". "+name+"!");u.lang='en-US';u.rate=0.9;u.pitch=1.28;window.speechSynthesis.speak(u);}
function initAudio(){if(audioCtx)return;audioCtx=new(window.AudioContext||window.webkitAudioContext)();}
function playMelody(){if(!audioCtx||!musicEnabled||voiceMuted)return;const now=audioCtx.currentTime;const m=[{n:523.25,d:0.2,t:0},{n:659.25,d:0.2,t:0.22},{n:783.99,d:0.3,t:0.44},{n:523.25,d:0.2,t:0.8},{n:587.33,d:0.2,t:1.02},{n:659.25,d:0.4,t:1.24},{n:523.25,d:0.3,t:1.8},{n:783.99,d:0.25,t:2.1},{n:880,d:0.3,t:2.35},{n:783.99,d:0.5,t:2.7},{n:659.25,d:0.6,t:3.2}];
m.forEach(x=>{const o=audioCtx.createOscillator(),g=audioCtx.createGain();o.connect(g);g.connect(audioCtx.destination);o.type='square';o.frequency.value=x.n;g.gain.setValueAtTime(0.18,now+x.t);g.gain.exponentialRampToValueAtTime(0.0001,now+x.t+x.d);o.start(now+x.t);o.stop(now+x.t+x.d);});}
function startLoop(){if(musicInterval)clearInterval(musicInterval);playMelody();musicInterval=setInterval(()=>{if(musicEnabled&&!voiceMuted&&isPlaying)playMelody();},4200);}
function enableMusic(){if(musicEnabled)return;initAudio();audioCtx.resume().then(()=>{musicEnabled=true;startLoop();});}
let particles=[];for(let i=0;i<45;i++)particles.push({x:Math.random(),y:Math.random(),size:6+Math.random()*14,speed:0.4+Math.random()*1.3,type:Math.random()>0.6?'⭐':'❤️'});
function drawBg(now){const g=ctx.createLinearGradient(0,0,0,canvas.height);g.addColorStop(0,"#1a1a5e");g.addColorStop(0.4,"#1e3a60");g.addColorStop(1,"#0f5060");ctx.fillStyle=g;ctx.fillRect(0,0,canvas.width,canvas.height);
particles.forEach(p=>{let y=(now*0.07*p.speed+p.y*canvas.height)%(canvas.height+150)-80;ctx.font=Math.floor(p.size)+'px "Segoe UI Emoji"';ctx.fillStyle=p.type==='❤️'?`rgba(255,105,180,0.6)`: `rgba(255,215,0,0.7)`;ctx.fillText(p.type,p.x*canvas.width,y);});
ctx.strokeStyle="#ffb347";ctx.lineWidth=3;ctx.strokeRect(6,6,canvas.width-12,canvas.height-12);}
function drawNum(idx,prog,now){const a=animals[idx],num=idx+1,b=1+Math.sin(now*16)*0.08;ctx.save();ctx.shadowBlur=14;ctx.font=`bold ${Math.floor(158*b)}px "Comic Neue"`;ctx.fillStyle="#FFF5E0";ctx.fillText(num,canvas.width/2-70,canvas.height/3+30);
ctx.font='bold 34px "Comic Neue"';ctx.fillStyle="#FFE484";ctx.fillText(a.hook,canvas.width/2-125,canvas.height/3+120);
ctx.font='30px "Comic Neue"';ctx.fillStyle="white";ctx.fillText(a.name,canvas.width/2-115,canvas.height/3+180);
let sx=canvas.width/2-(num-1)*30;for(let i=0;i<num;i++){let ox=sx+i*58+Math.sin(now*14+i)*12,oy=canvas.height-170+Math.sin(now*8+i)*14;ctx.font='56px "Segoe UI Emoji"';ctx.fillStyle="#ffffffdd";ctx.fillText(a.emoji.split(' ')[0],ox,oy);}
ctx.beginPath();ctx.arc(canvas.width/2-38,canvas.height/3-5,78+prog*58,0,Math.PI*2);ctx.strokeStyle=`rgba(255,200,80,${0.6-prog*0.3})`;ctx.lineWidth=7;ctx.stroke();
for(let s=0;s<35;s++){let angle=now*15+s,rad=110,x=canvas.width/2-38+Math.cos(angle)*rad,y=canvas.height/3+20+Math.sin(angle*1.5)*rad*0.6;ctx.beginPath();ctx.arc(x,y,4+Math.sin(angle*18)*2.5,0,Math.PI*2);ctx.fillStyle="rgba(255,220,90,0.9)";ctx.fill();}
ctx.restore();}
function getSeg(sec){if(sec<5)return{seg:"intro"};if(sec>=85)return{seg:"outro"};for(let i=0;i<10;i++){let s=5+i*8,e=5+(i+1)*8;if(sec>=s&&sec<e)return{seg:"number",idx:i,prog:(sec-s)/8};}return{seg:"trans"};}
function like(){const l=document.getElementById('likeAnim');l.style.animation='none';l.offsetHeight;l.style.animation='floatUp 0.85s ease-out';l.innerText='❤️';setTimeout(()=>{l.innerText='';},750);}
function render(ms){if(!isPlaying&&startTime!==null){animId=requestAnimationFrame(render);return;}
if(startTime===null)startTime=ms/1000;
let now=(ms/1000)-startTime;if(now>=TOTAL){now=TOTAL;if(isPlaying)isPlaying=false;}
drawBg(now);const seg=getSeg(now);let cap="🐙 COUNT WITH ME! 🐠";
if(now<5){ctx.font='bold 46px "Comic Neue"';ctx.fillStyle="#FFE9A7";ctx.fillText("🌊 VIRAL COUNTING!",canvas.width/2-165,canvas.height/2-70);cap="🔥 LET'S GO VIRAL! 🔥";like();}
else if(now>=85){ctx.font='bold 42px "Comic Neue"';ctx.fillStyle="gold";ctx.fillText("🏆 YOU'RE A STAR! 🏆",canvas.width/2-165,canvas.height/2-50);ctx.font='30px cursive';ctx.fillStyle="#FFB347";ctx.fillText("👍 SHARE WITH FRIENDS 👍",canvas.width/2-175,canvas.height/2+65);cap="🎉 YOU DID IT! 🎉";}
else if(seg.seg==="number"){const idxN=seg.idx;currentNum=idxN+1;drawNum(idxN,seg.prog,now);cap=animals[idxN].emoji+"  "+animals[idxN].name;
if(lastSpoken!==idxN&&!voiceMuted&&seg.prog>0.2){lastSpoken=idxN;speak(idxN+1,animals[idxN].name);like();}}
document.getElementById('captionText').innerHTML=cap;
if(now>=TOTAL&&isPlaying)isPlaying=false;
animId=requestAnimationFrame(render);}
function start(){if(animId)cancelAnimationFrame(animId);startTime=null;isPlaying=true;lastSpoken=-1;window.speechSynthesis.cancel();animId=requestAnimationFrame((ms)=>{startTime=ms/1000;render(ms);});}
enableMusic();
start();
setInterval(()=>{if(isPlaying&&currentNum>0)like();},3800);
drawBg(0);
})();
</script>
</body>
</html>'''

def save_html():
    """Save the HTML file"""
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(HTML_CONTENT)
    print(f"✅ HTML file saved: {HTML_FILE}")
    return os.path.abspath(HTML_FILE)

def record_with_ffmpeg():
    """Record the screen using FFmpeg"""
    print("\n🎬 Starting video recording...")
    print("⏱️  Recording for 95 seconds...")
    print("📺 The browser will open automatically")

    # FFmpeg command to record screen
    ffmpeg_cmd = [
        'ffmpeg',
        '-f', 'gdigrab',  # Windows capture
        '-framerate', str(FPS),
        '-offset_x', '0',
        '-offset_y', '0',
        '-video_size', f'{VIDEO_WIDTH}x{VIDEO_HEIGHT}',
        '-i', 'desktop',
        '-t', str(TOTAL_DURATION),
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-y',  # Overwrite output file
        OUTPUT_FILE
    ]

    # For Mac users
    if sys.platform == 'darwin':
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'avfoundation',
            '-framerate', str(FPS),
            '-i', '1',  # Screen index on Mac
            '-t', str(TOTAL_DURATION),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-y',
            OUTPUT_FILE
        ]

    try:
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e}")
        return False

def open_browser_and_record():
    """Open browser with HTML and record"""
    import webbrowser
    import threading

    html_path = save_html()
    file_url = f'file:///{html_path.replace(os.sep, "/")}'

    print("\n🌐 Opening browser...")
    webbrowser.open(file_url)

    print("\n⚠️  IMPORTANT:")
    print("   1. Wait 3 seconds for browser to load")
    print("   2. Position the browser window so ONLY the video is visible")
    print("   3. The video is 405x720 pixels")
    print("   4. Recording will start automatically in 5 seconds...")

    time.sleep(5)

    print("\n🔴 RECORDING NOW... (95 seconds)")
    print("   Do not move the window!")

    # Start recording
    success = record_with_ffmpeg()

    if success:
        print(f"\n✅ VIDEO SAVED: {OUTPUT_FILE}")
        file_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
        print(f"📁 File size: {file_size:.2f} MB")
    else:
        print("\n❌ Recording failed. Trying alternative method...")
        record_with_pil()

def record_with_pil():
    """Fallback method using PIL screenshots"""
    print("\n📸 Using screenshot method (slower but works)...")
    import cv2

    frames = []
    print("Recording 90 seconds...")

    for i in range(TOTAL_DURATION * FPS):
        # Capture screen region
        screenshot = ImageGrab.grab(bbox=(100, 100, 100+VIDEO_WIDTH, 100+VIDEO_HEIGHT))
        frame = np.array(screenshot)
        frames.append(frame)

        if i % 30 == 0:
            print(f"  Frame {i}/{TOTAL_DURATION*FPS}")
        time.sleep(1/FPS)

    # Save as video
    print("Saving video...")
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_FILE, fourcc, FPS, (width, height))

    for frame in frames:
        out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    out.release()
    print(f"✅ Video saved: {OUTPUT_FILE}")

def main():
    print("=" * 50)
    print("🎬 VIRAL KIDS VIDEO GENERATOR")
    print("=" * 50)
    print("\n📋 This script will:")
    print("   1. Create HTML video file")
    print("   2. Open it in your browser")
    print("   3. Record screen for 95 seconds")
    print("   4. Save as MP4")
    print("\n" + "=" * 50)

    # Check if FFmpeg is available
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        has_ffmpeg = True
    except FileNotFoundError:
        has_ffmpeg = False
        print("\n⚠️  FFmpeg not found!")
        print("   Will use alternative recording method (slower).")
        print("   For better quality, install FFmpeg:")
        print("   - Windows: Download from ffmpeg.org")
        print("   - Mac: brew install ffmpeg")
        print("   - Linux: sudo apt install ffmpeg")

    open_browser_and_record()

    print("\n" + "=" * 50)
    print(f"✨ DONE! Your video is ready: {OUTPUT_FILE}")
    print("=" * 50)
    print("\n📤 Next steps:")
    print("   1. Upload to TikTok/Instagram Reels/YouTube Shorts")
    print("   2. Add hashtags: #counting #kidslearning #viral")
    print("   3. Share and watch it go viral!")

if __name__ == "__main__":
    main()
