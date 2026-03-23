#!/usr/bin/env python3
"""Capture terminal screenshots of all 9 snake games - v2 with TERM fix."""
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

def capture_game(folder, label):
    game_path = os.path.join(BASE, folder, "snake.py")
    if not os.path.exists(game_path):
        print(f"  SKIP {folder} - no snake.py")
        return None

    subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)
    time.sleep(0.3)

    # Start tmux with TERM set
    subprocess.run(["tmux", "new-session", "-d", "-s", SESSION, "-x", "60", "-y", "24"], capture_output=True)
    subprocess.run(["tmux", "send-keys", "-t", SESSION, f"TERM=xterm python3 {game_path}", "Enter"], capture_output=True)

    time.sleep(2)

    # Move snake around
    for key in ["Down", "Down", "Right", "Right", "Down"]:
        subprocess.run(["tmux", "send-keys", "-t", SESSION, key], capture_output=True)
        time.sleep(0.2)

    time.sleep(0.5)

    result = subprocess.run(["tmux", "capture-pane", "-t", SESSION, "-p"], capture_output=True, text=True)
    terminal_content = result.stdout
    subprocess.run(["tmux", "kill-session", "-t", SESSION], capture_output=True)

    # Filter out shell prompt lines
    lines = terminal_content.split('\n')
    game_lines = [l for l in lines if not l.startswith('nimanch@') and 'python3' not in l and '$' not in l[:3]]

    if not any(l.strip() for l in game_lines):
        print(f"  EMPTY capture for {folder}")
        return None

    img = render_terminal('\n'.join(game_lines), label)
    outpath = os.path.join(SCREENSHOT_DIR, f"{folder}.png")
    img.save(outpath)
    print(f"  ✓ {folder} → {outpath}")
    return outpath


def render_terminal(text, label):
    lines = text.split('\n')
    while len(lines) < 24:
        lines.append('')

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

    # Title bar with gradient feel
    draw.rectangle([0, 0, width, title_h], fill=(40, 44, 52))
    # Fake window buttons
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        draw.ellipse([padding + i*22, 14, padding + i*22 + 14, 28], fill=color)
    draw.text((padding + 80, 12), label, fill=(220, 220, 220), font=title_font)

    y = title_h + padding
    for line in lines[:24]:
        x = padding
        for ch in line[:62]:
            if ch in ('O', 'o'):
                color = (80, 250, 123)  # green head
            elif ch in ('\u2588', '#', 'S'):
                color = (0, 200, 83)  # green body
            elif ch in ('*', '@'):
                color = (255, 85, 85)  # red food
            elif ch in ('l', 'q', 'k', 'x', 'm', 'j', '+', '-', '|', '─', '│', '┌', '┐', '└', '┘'):
                color = (98, 114, 164)  # dim blue borders
            elif ch.isdigit():
                color = (241, 250, 140)  # yellow numbers
            elif 'Score' in line and ch.isalpha():
                color = (189, 147, 249)  # purple for "Score"
            else:
                color = (190, 190, 200)
            draw.text((x, y), ch, fill=color, font=font)
            x += char_w
        y += char_h

    draw.rectangle([0, 0, width-1, height-1], outline=(68, 71, 90), width=2)
    return img


if __name__ == '__main__':
    print("Capturing screenshots of all 9 snake games...\n")
    captured = []
    for folder, label in GAMES:
        print(f"[{label}]")
        path = capture_game(folder, label)
        if path:
            captured.append((label, path))

    if captured:
        print(f"\nCreating 3x3 composite grid ({len(captured)} games)...")
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
        print(f"✓ Grid saved to {grid_path}")

    print("\nDone!")
