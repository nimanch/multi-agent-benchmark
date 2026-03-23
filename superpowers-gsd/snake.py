#!/usr/bin/env python3
"""Snake Game - Generated via Superpowers + GSD workflow.

Superpowers orchestrated via subagent-driven-development skill:
  1. Planning subagent wrote the implementation plan
  2. Implementation subagent built the game
  3. Spec-review subagent verified against SNAKE_SPEC.md
  4. Code-quality-review subagent cleaned up

GSD (Get Shit Done) provided the project scaffolding via:
  gsd new-project → gsd plan-milestone → gsd execute-phase
"""

import curses
import random
import time

# Constants
TICK_RATE = 0.1
FOOD_CHAR = '*'
HEAD_CHAR = 'O'
BODY_CHAR = '█'
SCORE_PER_FOOD = 10

# Direction vectors
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

OPPOSITE = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


def init_game(stdscr):
    """Initialize game state."""
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(int(TICK_RATE * 1000))

    h, w = stdscr.getmaxyx()
    if h < 10 or w < 20:
        raise RuntimeError("Terminal too small. Need at least 20x10.")

    mid_y, mid_x = h // 2, w // 2
    snake = [(mid_y, mid_x), (mid_y, mid_x - 1), (mid_y, mid_x - 2)]
    direction = RIGHT
    score = 0
    food = spawn_food(h, w, snake)

    return snake, direction, score, food, h, w


def spawn_food(h, w, snake):
    """Spawn food at random position not on snake."""
    while True:
        y = random.randint(1, h - 2)
        x = random.randint(1, w - 2)
        if (y, x) not in snake:
            return (y, x)


def draw(stdscr, snake, food, score, h, w):
    """Render the game state."""
    stdscr.erase()

    # Border
    for x in range(w):
        stdscr.addch(0, x, '─')
        if x < w - 1:
            stdscr.addch(h - 1, x, '─')
    for y in range(h):
        stdscr.addch(y, 0, '│')
        if y < h - 1:
            stdscr.addch(y, w - 1, '│')
    stdscr.addch(0, 0, '┌')
    stdscr.addch(0, w - 1, '┐')
    stdscr.addch(h - 1, 0, '└')
    try:
        stdscr.addch(h - 1, w - 1, '┘')
    except curses.error:
        pass

    # Score
    score_str = f" Score: {score} "
    stdscr.addstr(0, (w - len(score_str)) // 2, score_str, curses.A_BOLD)

    # Food
    try:
        stdscr.addch(food[0], food[1], FOOD_CHAR, curses.A_BOLD)
    except curses.error:
        pass

    # Snake
    for i, (y, x) in enumerate(snake):
        try:
            ch = HEAD_CHAR if i == 0 else BODY_CHAR
            stdscr.addch(y, x, ch)
        except curses.error:
            pass

    stdscr.refresh()


def game_over_screen(stdscr, score, h, w):
    """Display game over screen."""
    stdscr.erase()
    msg1 = "GAME OVER"
    msg2 = f"Final Score: {score}"
    msg3 = "Press 'r' to restart or 'q' to quit"
    stdscr.addstr(h // 2 - 1, (w - len(msg1)) // 2, msg1, curses.A_BOLD)
    stdscr.addstr(h // 2, (w - len(msg2)) // 2, msg2)
    stdscr.addstr(h // 2 + 1, (w - len(msg3)) // 2, msg3)
    stdscr.refresh()

    stdscr.nodelay(False)
    while True:
        key = stdscr.getch()
        if key == ord('q'):
            return False
        elif key == ord('r'):
            return True


def game_loop(stdscr):
    """Main game loop."""
    while True:
        snake, direction, score, food, h, w = init_game(stdscr)

        while True:
            key = stdscr.getch()

            key_map = {
                curses.KEY_UP: UP,
                curses.KEY_DOWN: DOWN,
                curses.KEY_LEFT: LEFT,
                curses.KEY_RIGHT: RIGHT,
            }

            if key in key_map:
                new_dir = key_map[key]
                if new_dir != OPPOSITE.get(direction):
                    direction = new_dir

            # Move snake
            head_y, head_x = snake[0]
            dy, dx = direction
            new_head = (head_y + dy, head_x + dx)

            # Wall collision
            if (new_head[0] <= 0 or new_head[0] >= h - 1 or
                    new_head[1] <= 0 or new_head[1] >= w - 1):
                break

            # Self collision
            if new_head in snake:
                break

            snake.insert(0, new_head)

            # Food check
            if new_head == food:
                score += SCORE_PER_FOOD
                food = spawn_food(h, w, snake)
            else:
                snake.pop()

            draw(stdscr, snake, food, score, h, w)

        if not game_over_screen(stdscr, score, h, w):
            break


def main():
    curses.wrapper(game_loop)


if __name__ == "__main__":
    main()
