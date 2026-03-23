#!/usr/bin/env python3
"""Snake Game - Generated via DeerFlow 2.0 + GSD workflow.

DeerFlow orchestrated sub-agents with memory:
  - Research agent: analyzed curses best practices
  - Planning agent: broke spec into tasks
  - Coding agent: implemented with sandboxed execution
  - Review agent: verified against spec

GSD managed project lifecycle:
  gsd new-project → plan-milestone → execute-phase → verify-phase

Architecture: Module-style with clear function pipeline.
"""

import curses
import random
import sys

# Game parameters
INITIAL_LENGTH = 3
SPEED_MS = 100
POINTS_PER_FOOD = 10

DIR_UP = (-1, 0)
DIR_DOWN = (1, 0)
DIR_LEFT = (0, -1)
DIR_RIGHT = (0, 1)

BLOCKED = {DIR_UP: DIR_DOWN, DIR_DOWN: DIR_UP, DIR_LEFT: DIR_RIGHT, DIR_RIGHT: DIR_LEFT}

KEY_TO_DIR = {
    curses.KEY_UP: DIR_UP,
    curses.KEY_DOWN: DIR_DOWN,
    curses.KEY_LEFT: DIR_LEFT,
    curses.KEY_RIGHT: DIR_RIGHT,
}


def create_snake(h, w):
    """Create initial snake in center of screen."""
    cy, cx = h // 2, w // 2
    return [(cy, cx - i) for i in range(INITIAL_LENGTH)]


def place_food(h, w, snake):
    """Place food at random unoccupied position."""
    occupied = set(snake)
    attempts = 0
    while attempts < 1000:
        pos = (random.randint(1, h - 2), random.randint(1, w - 2))
        if pos not in occupied:
            return pos
        attempts += 1
    return (1, 1)  # fallback


def update_direction(current, key):
    """Update direction based on key press, preventing reversal."""
    if key in KEY_TO_DIR:
        new = KEY_TO_DIR[key]
        if new != BLOCKED.get(current):
            return new
    return current


def move_snake(snake, direction, food):
    """Move snake one step. Returns (new_snake, ate_food)."""
    head_y, head_x = snake[0]
    dy, dx = direction
    new_head = (head_y + dy, head_x + dx)

    new_snake = [new_head] + snake[:]
    ate = new_head == food
    if not ate:
        new_snake.pop()

    return new_snake, ate


def check_collision(snake, h, w):
    """Check wall and self collision. Returns True if game over."""
    y, x = snake[0]
    if y <= 0 or y >= h - 1 or x <= 0 or x >= w - 1:
        return True
    if snake[0] in snake[1:]:
        return True
    return False


def draw_frame(stdscr, snake, food, score, h, w):
    """Render one frame."""
    stdscr.erase()

    # Draw border
    stdscr.border()

    # Score
    label = f" Score: {score} "
    stdscr.addstr(0, max(1, (w - len(label)) // 2), label, curses.A_BOLD)

    # Food
    fy, fx = food
    try:
        stdscr.addch(fy, fx, '*', curses.A_BOLD)
    except curses.error:
        pass

    # Snake
    for i, (sy, sx) in enumerate(snake):
        try:
            stdscr.addch(sy, sx, 'O' if i == 0 else '█')
        except curses.error:
            pass

    stdscr.refresh()


def show_game_over(stdscr, score, h, w):
    """Display game over and wait for user choice."""
    stdscr.erase()
    center_y = h // 2
    texts = [
        ("╔══════════════════╗", -2),
        ("║    GAME  OVER    ║", -1),
        (f"║  Score: {score:>6}    ║", 0),
        ("║  r=Retry  q=Quit ║", 1),
        ("╚══════════════════╝", 2),
    ]
    for text, offset in texts:
        stdscr.addstr(center_y + offset, (w - len(text)) // 2, text,
                      curses.A_BOLD)
    stdscr.refresh()
    stdscr.nodelay(False)
    while True:
        k = stdscr.getch()
        if k == ord('q'):
            return False
        if k == ord('r'):
            return True


def game_loop(stdscr):
    """Main game loop with restart support."""
    curses.curs_set(0)

    while True:
        h, w = stdscr.getmaxyx()
        if h < 10 or w < 20:
            stdscr.addstr(0, 0, "Terminal too small!")
            stdscr.getch()
            return

        stdscr.nodelay(True)
        stdscr.timeout(SPEED_MS)

        snake = create_snake(h, w)
        direction = DIR_RIGHT
        food = place_food(h, w, snake)
        score = 0

        while True:
            key = stdscr.getch()
            direction = update_direction(direction, key)
            snake, ate = move_snake(snake, direction, food)

            if check_collision(snake, h, w):
                break

            if ate:
                score += POINTS_PER_FOOD
                food = place_food(h, w, snake)

            draw_frame(stdscr, snake, food, score, h, w)

        if not show_game_over(stdscr, score, h, w):
            break


if __name__ == "__main__":
    curses.wrapper(game_loop)
