#!/usr/bin/env python3
"""Capture 10-second gameplay GIFs for all 9 snake games."""
import subprocess
import time
import os
from PIL import Image, ImageDraw, ImageFont

GAMES = [
    ("superpowers-gsd", "Superpowers + GSD"),
    ("superpowers-speckit", "Superpowers + Spec Kit 🏆"),
    ("superpowers-openspec", "Superpowers + OpenSpec"),
    ("deerflow-gsd", "DeerFlow + GSD"),
    ("deerflow-speckit", "DeerFlow + Spec Kit"),
    ("deerflow-openspec", "DeerFlow + OpenSpec"),
    ("squad-gsd", "Squad + GSD ⚡"),
    ("squad-speckit", "Squad + Spec Kit"),
    ("squad-openspec", "Squad + OpenSpec 🧪"),
]

BASE = os.path.dirname(os.path.abspath(__file__))
GIF_DIR = os.path.join(BASE, "gifs")
os.makedirs(GIF_DIR, exist_ok=True)
SESSION = "snakegif"

# Direction changes only (snake moves on its own between changes)
# Snake starts center moving Right. Board ~60x24, borders at edges.
# Each direction change sent, then wait for snake to travel.
# At 800ms tick, each cell takes 0.8s
MOVE_SCRIPT = [
    ("Down", 4.0),    # travel down ~5 cells
    ("Right", 6.0),   # travel right to near edge
    ("Down", 3.0),    # down a bit more
    ("Left", 10.0),   # travel all the way left
    ("Up", 8.0),      # travel up
    ("Right", 10.0),  # travel right across
    ("Down", 6.0),    # travel down
    ("Left", 8.0),    # travel left
    ("Up", 5.0),      # up
    ("Right", 5.0),   # right
]

def send_key(key):
    subprocess.run(["tmux", "send-keys", "-t", SESSION, key], capture_output=True)

def capture_pane():
    r = subprocess.run(["tmux", "capture-pane", "-t", SESSION, "-p"], capture_output=True, text=True)
    return r.stdout

def render_frame(text, label):
    lines = text.split('\n')
    while len(lines) < 24:
        lines.append('')
    lines = lines[:24]

    char_w, char_h = 9, 18
    padding = 16
    title_h = 36
    width = 62 * char_w + padding * 2
    height = 24 * char_h + padding * 2 + title_h

    img = Image.new('RGB', (width, height), (24, 24, 32))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 13)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 14)
    except:
        font = ImageFont.load_default()
        title_font = font

    draw.rectangle([0, 0, width, title_h], fill=(40, 44, 52))
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([padding + i*20, 10, padding + i*20 + 13, 23], fill=color)
    draw.text((padding + 72, 9), label, fill=(220, 220, 220), font=title_font)

    y = title_h + padding
    for line in lines:
        x = padding
        for ch in line[:62]:
            if ch == 'O':
                color = (255, 255, 100)
            elif ch == '\u2588':
                color = (80, 250, 123)
            elif ch in ('#', 'S'):
                color = (0, 200, 83)
            elif ch == '*':
                color = (255, 85, 85)
            elif ch == '@':
                color = (255, 121, 198)
            elif ch in ('┌', '┐', '└', '┘', '─', '│', 'l', 'q', 'k', 'x', 'm', 'j', '+', '-', '|'):
                color = (98, 114, 164)
            elif ch.isdigit():
                color = (241, 250, 140)
            elif 'Score' in line and ch.isalpha():
                color = (189, 147, 249)
            else:
                color = (190, 190, 200)
            draw.text((x, y), ch, fill=color, font=font)
            x += char_w
        y += char_h

    draw.rectangle([0, 0, width-1, height-1], outline=(68, 71, 90), width=2)
    return img


def capture_game_gif(folder, label):
    game_path = os.path.join(BASE, folder, "snake.py")
    if not os.path.exists(game_path):
        print(f"  SKIP {folder}")
        return None

    subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)
    time.sleep(0.3)
    subprocess.run(["tmux", "new-session", "-d", "-s", SESSION, "-x", "60", "-y", "24"], capture_output=True)
    subprocess.run(["tmux", "send-keys", "-t", SESSION, f"TERM=xterm python3 {game_path}", "Enter"], capture_output=True)
    time.sleep(0.8)

    # Immediately send Down to turn away from right wall
    send_key("Down")
    time.sleep(0.2)

    frames = []
    fps = 4  # 4 frames per second
    frame_interval = 1.0 / fps
    move_idx = 0
    move_timer = 0.0
    game_over = False

    start = time.time()
    while time.time() - start < 30 and not game_over:
        # Capture frame
        content = capture_pane()
        lines = content.split('\n')
        filtered = [l for l in lines if 'nimanch@' not in l and 'TERM=' not in l and '$ ' not in l[:3]]
        frame_text = '\n'.join(filtered)
        frame = render_frame(frame_text, label)
        frames.append(frame)

        if 'GAME OVER' in content.upper() or 'Game Over' in content:
            for _ in range(4):
                frames.append(frame)
            game_over = True
            break

        # Check if time to send next direction
        if move_idx < len(MOVE_SCRIPT):
            key, wait = MOVE_SCRIPT[move_idx]
            if move_timer <= 0:
                send_key(key)
                move_timer = wait
                move_idx += 1

        move_timer -= frame_interval
        time.sleep(frame_interval)

    subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)

    if not frames:
        print(f"  NO FRAMES for {folder}")
        return None

    # Save as GIF
    outpath = os.path.join(GIF_DIR, f"{folder}.gif")
    frames[0].save(
        outpath,
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps),
        loop=0,
        optimize=True
    )
    print(f"  ✓ {folder} ({len(frames)} frames, {os.path.getsize(outpath)//1024}KB)")
    return outpath


if __name__ == '__main__':
    # Temporarily slow games down for better captures
    print("Slowing games for capture...")
    for folder, _ in GAMES:
        f = os.path.join(BASE, folder, "snake.py")
        if os.path.exists(f):
            subprocess.run(["cp", f, f + ".bak"], capture_output=True)
            subprocess.run(["sed", "-i", "s/timeout(100)/timeout(800)/g", f], capture_output=True)
            subprocess.run(["sed", "-i", "s/TICK_MS = 100/TICK_MS = 800/g", f], capture_output=True)
            subprocess.run(["sed", "-i", "s/TICK_RATE = 0.1/TICK_RATE = 0.8/g", f], capture_output=True)
            subprocess.run(["sed", "-i", "s/SPEED_MS = 100/SPEED_MS = 800/g", f], capture_output=True)

    print("\nCapturing 10-second gameplay GIFs...\n")
    captured = []
    for folder, label in GAMES:
        print(f"[{label}]")
        path = capture_game_gif(folder, label)
        if path:
            captured.append((label, path))
        time.sleep(0.5)

    # Restore original speeds
    print("\nRestoring original game speeds...")
    for folder, _ in GAMES:
        f = os.path.join(BASE, folder, "snake.py")
        bak = f + ".bak"
        if os.path.exists(bak):
            os.rename(bak, f)

    print(f"\n✅ Done! {len(captured)} GIFs saved to {GIF_DIR}/")
