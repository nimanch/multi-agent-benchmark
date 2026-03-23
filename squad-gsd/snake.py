#!/usr/bin/env python3
"""Snake Game - Generated via Squad (Copilot) + GSD workflow.

Squad pipeline (simulated locally via Copilot CLI):
  1. Coordinator agent: parsed SNAKE_SPEC.md
  2. Plan agent: broke into implementation tasks
  3. Implement agent: wrote code
  4. Review agent: checked quality & spec adherence
  5. Test agent: verified all acceptance criteria

GSD managed project phases: new-project → execute-phase → verify-phase

Architecture: Clean single-file with helper functions.
"""

import curses
import random


def run_game(stdscr):
    """Entry point wrapping the game loop with restart."""
    curses.curs_set(0)

    while True:
        result = play(stdscr)
        if not result:
            break


def play(stdscr):
    """Play one round. Returns True to restart, False to quit."""
    h, w = stdscr.getmaxyx()
    if h < 10 or w < 20:
        stdscr.addstr(0, 0, "Terminal too small (need 20x10)")
        stdscr.getch()
        return False

    stdscr.nodelay(True)
    stdscr.timeout(100)

    # Init state
    cy, cx = h // 2, w // 2
    snake = [(cy, cx), (cy, cx - 1), (cy, cx - 2)]
    direction = (0, 1)  # right
    score = 0
    food = _spawn(h, w, snake)

    opposites = {(-1, 0): (1, 0), (1, 0): (-1, 0), (0, -1): (0, 1), (0, 1): (0, -1)}
    keymap = {
        curses.KEY_UP: (-1, 0), curses.KEY_DOWN: (1, 0),
        curses.KEY_LEFT: (0, -1), curses.KEY_RIGHT: (0, 1),
    }

    while True:
        key = stdscr.getch()
        if key in keymap:
            nd = keymap[key]
            if nd != opposites.get(direction):
                direction = nd

        dy, dx = direction
        nh = (snake[0][0] + dy, snake[0][1] + dx)

        # Collisions
        if nh[0] <= 0 or nh[0] >= h - 1 or nh[1] <= 0 or nh[1] >= w - 1:
            break
        if nh in snake:
            break

        snake.insert(0, nh)
        if nh == food:
            score += 10
            food = _spawn(h, w, snake)
        else:
            snake.pop()

        _render(stdscr, snake, food, score, h, w)

    return _game_over(stdscr, score, h, w)


def _spawn(h, w, snake):
    s = set(snake)
    while True:
        p = (random.randint(1, h - 2), random.randint(1, w - 2))
        if p not in s:
            return p


def _render(stdscr, snake, food, score, h, w):
    stdscr.erase()
    stdscr.border()

    label = f" Score: {score} "
    stdscr.addstr(0, (w - len(label)) // 2, label, curses.A_BOLD)

    try:
        stdscr.addch(food[0], food[1], '*', curses.A_BOLD)
    except curses.error:
        pass

    for i, (y, x) in enumerate(snake):
        try:
            stdscr.addch(y, x, 'O' if i == 0 else '█')
        except curses.error:
            pass

    stdscr.refresh()


def _game_over(stdscr, score, h, w):
    stdscr.erase()
    lines = [
        ("GAME OVER", curses.A_BOLD),
        (f"Final Score: {score}", 0),
        ("Press 'r' to restart, 'q' to quit", 0),
    ]
    for i, (text, attr) in enumerate(lines):
        stdscr.addstr(h // 2 - 1 + i, (w - len(text)) // 2, text, attr)
    stdscr.refresh()

    stdscr.nodelay(False)
    while True:
        k = stdscr.getch()
        if k == ord('q'):
            return False
        if k == ord('r'):
            return True


if __name__ == "__main__":
    curses.wrapper(run_game)
