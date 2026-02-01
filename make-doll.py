import requests
from PIL import Image, ImageSequence
from io import BytesIO

# -------- URLs --------
static_layers = [
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/01backgroundfull/0018.gif",
    # "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/02acc/0011.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/05hair/0175.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/06base/0001.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/08shoes/0084.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/09bottom/0621.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/10top/0278.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/11head/0058.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/12mouth/0008.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/13nose/0024.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/15eyebrows/0020.gif",
    "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/20hair/0175.gif"
]

animated_layers = {
    # "wings": "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/04wings/0018.gif",
    "eyes": "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/14eyes/0236.gif",
    "pet": "https://web.archive.org/web/20220508202711im_/http://elouai.com/valentine/img/25pets/0024.gif"
}

# -------- Loader --------
def load_gif_frames_safe(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        gif = Image.open(BytesIO(r.content))
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(gif):
            frames.append(frame.convert("RGBA"))
            durations.append(frame.info.get("duration", 100))
        return frames, durations
    except Exception as e:
        print(f"⚠️ Skipping {url}: {e}")
        return None, None

# -------- Load static layers --------
static_images = []
for url in static_layers:
    frames, _ = load_gif_frames_safe(url)
    if frames:
        static_images.append(frames[0])  # only first frame (static)

# -------- Load animated layers --------
animated_frames = {}
animated_durations = {}

for key, url in animated_layers.items():
    frames, durations = load_gif_frames_safe(url)
    if frames:
        animated_frames[key] = frames
        animated_durations[key] = durations

# -------- Determine animation length --------
max_frames = max(len(frames) for frames in animated_frames.values())

def get_frame(frames, i):
    return frames[i % len(frames)]

# -------- Build frames --------
final_frames = []
final_durations = []

for i in range(max_frames):
    base = static_images[0].copy()
    for img in static_images[1:]:
        base.paste(img, (0, 0), img)

    # Paste animated layers
    if "wings" in animated_frames:
        frame = get_frame(animated_frames["wings"], i)
        base.paste(frame, (0, 0), frame)

    if "eyes" in animated_frames:
        frame = get_frame(animated_frames["eyes"], i)
        base.paste(frame, (0, 0), frame)

    if "pet" in animated_frames:
        frame = get_frame(animated_frames["pet"], i)
        base.paste(frame, (0, 0), frame)

    final_frames.append(base)
    final_durations.append(100)
    
# -------- Resize frames (make GIF bigger) --------
scale = 3  # change this to 2, 4, etc.
w, h = final_frames[0].size
final_frames = [frame.resize((w * scale, h * scale), Image.NEAREST) for frame in final_frames]


# -------- Save GIF --------
final_frames[0].save(
    "doll_partial_animation.gif",
    save_all=True,
    append_images=final_frames[1:],
    duration=final_durations,
    loop=0,
    disposal=2,
)

print("✅ Saved doll_partial_animation.gif (eyes, wings, pet animated only)")
