#!/usr/bin/env python3
"""Capture mid-game screenshots - v3. Slow tick, gentle movements, capture EARLY."""
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
SCREENSHOT_DIR = os.path.join(BASE, "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
SESSION = "snakecap"

def send_key(key, delay=0.4):
    subprocess.run(["tmux", "send-keys", "-t", SESSION, key], capture_output=True)
    time.sleep(delay)

def capture_pane():
    r = subprocess.run(["tmux", "capture-pane", "-t", SESSION, "-p"], capture_output=True, text=True)
    return r.stdout

def capture_game(folder, label):
    game_path = os.path.join(BASE, folder, "snake.py")
    if not os.path.exists(game_path):
        return None

    subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)
    time.sleep(0.5)
    subprocess.run(["tmux", "new-session", "-d", "-s", SESSION, "-x", "60", "-y", "24"], capture_output=True)
    subprocess.run(["tmux", "send-keys", "-t", SESSION, f"TERM=xterm python3 {game_path}", "Enter"], capture_output=True)
    time.sleep(2)

    # Gentle movement - just go down a few then right, capture mid-movement
    # The snake starts roughly center moving right. Go down to avoid walls.
    send_key("Down", 0.5)
    send_key("Down", 0.5)
    send_key("Down", 0.5)

    # Capture NOW - snake should be alive and visible
    content = capture_pane()

    # Check if still alive, if yes do a few more moves
    if 'GAME OVER' not in content.upper():
        send_key("Right", 0.5)
        send_key("Right", 0.5)
        content = capture_pane()

    if 'GAME OVER' not in content.upper():
        send_key("Down", 0.5)
        send_key("Left", 0.5)
        send_key("Left", 0.5)
        content = capture_pane()

    subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)

    # Filter shell artifacts
    lines = content.split('\n')
    filtered = [l for l in lines if 'nimanch@' not in l and '$ ' not in l[:5] and 'TERM=' not in l]

    if not any(l.strip() for l in filtered):
        print(f"  EMPTY {folder}")
        return None

    img = render_terminal('\n'.join(filtered), label)
    outpath = os.path.join(SCREENSHOT_DIR, f"{folder}.png")
    img.save(outpath)
    print(f"  ✓ {folder}")
    return outpath


def render_terminal(text, label):
    lines = text.split('\n')
    while len(lines) < 24:
        lines.append('')
    lines = lines[:24]

    char_w, char_h = 10, 20
    padding = 20
    title_h = 44
    width = 62 * char_w + padding * 2
    height = 24 * char_h + padding * 2 + title_h

    img = Image.new('RGB', (width, height), (24, 24, 32))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 16)
    except:
        font = ImageFont.load_default()
        title_font = font

    # macOS-style title bar
    draw.rectangle([0, 0, width, title_h], fill=(40, 44, 52))
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([padding + i*22, 14, padding + i*22 + 14, 28], fill=color)
    draw.text((padding + 80, 12), label, fill=(220, 220, 220), font=title_font)

    y = title_h + padding
    for line in lines:
        x = padding
        for ch in line[:62]:
            if ch == 'O':
                color = (255, 255, 100)  # bright yellow head
            elif ch == '\u2588':
                color = (80, 250, 123)  # green body
            elif ch == '*':
                color = (255, 85, 85)  # red food
            elif ch == '@':
                color = (255, 121, 198)  # pink food
            elif ch in ('┌', '┐', '└', '┘', '─', '│', 'l', 'q', 'k', 'x', 'm', 'j', '+', '-', '|'):
                color = (98, 114, 164)  # dim blue borders
            elif ch.isdigit():
                color = (241, 250, 140)  # yellow numbers
            elif 'Score' in line and ch.isalpha():
                color = (189, 147, 249)  # purple
            else:
                color = (190, 190, 200)
            draw.text((x, y), ch, fill=color, font=font)
            x += char_w
        y += char_h

    draw.rectangle([0, 0, width-1, height-1], outline=(68, 71, 90), width=2)
    return img


if __name__ == '__main__':
    print("Capturing mid-game screenshots (slowed games)...\n")
    captured = []
    for folder, label in GAMES:
        print(f"[{label}]")
        path = capture_game(folder, label)
        if path:
            captured.append((label, path))
        time.sleep(0.5)

    if captured:
        print(f"\nCreating 3x3 grid...")
        imgs = [Image.open(p) for _, p in captured]
        w, h = imgs[0].size
        cols, rows = 3, 3
        gap = 6
        grid = Image.new('RGB', (w * cols + gap * 4, h * rows + gap * 4), (16, 16, 24))
        for i, img in enumerate(imgs):
            r, c = divmod(i, cols)
            grid.paste(img, (c * w + gap * (c+1), r * h + gap * (r+1)))
        grid_path = os.path.join(SCREENSHOT_DIR, "all-games-grid.png")
        grid.save(grid_path, quality=95)
        print(f"✓ Grid saved")
    print("\nDone!")
