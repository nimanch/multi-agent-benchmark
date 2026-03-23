#!/usr/bin/env python3
"""Snake Game - Generated via Squad (Copilot) + OpenSpec workflow.

Squad simulated (Coordinator → Plan → Implement → Review → Test).
OpenSpec structured with opsx:plan task breakdown.

Architecture: Minimal, clean, well-documented. TDD-inspired structure.
"""

import curses
import random


# === Domain Types ===

DIRECTIONS = {
    'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)
}
OPPOSITES = {'UP': 'DOWN', 'DOWN': 'UP', 'LEFT': 'RIGHT', 'RIGHT': 'LEFT'}
KEYS = {
    curses.KEY_UP: 'UP', curses.KEY_DOWN: 'DOWN',
    curses.KEY_LEFT: 'LEFT', curses.KEY_RIGHT: 'RIGHT',
}


# === Pure Logic (testable) ===

def initial_state(h, w):
    """Create initial game state dict."""
    cy, cx = h // 2, w // 2
    snake = [(cy, cx), (cy, cx - 1), (cy, cx - 2)]
    return {
        'snake': snake,
        'dir': 'RIGHT',
        'score': 0,
        'food': _place_food(h, w, snake),
        'alive': True,
        'h': h, 'w': w,
    }


def _place_food(h, w, snake):
    occ = set(snake)
    while True:
        p = (random.randint(1, h - 2), random.randint(1, w - 2))
        if p not in occ:
            return p


def process_input(state, key):
    """Process key input, return updated state."""
    if key in KEYS:
        new_dir = KEYS[key]
        if new_dir != OPPOSITES.get(state['dir']):
            state['dir'] = new_dir
    return state


def step(state):
    """Advance game one tick. Returns updated state."""
    if not state['alive']:
        return state

    dy, dx = DIRECTIONS[state['dir']]
    hy, hx = state['snake'][0]
    nh = (hy + dy, hx + dx)
    h, w = state['h'], state['w']

    # Wall
    if not (0 < nh[0] < h - 1 and 0 < nh[1] < w - 1):
        state['alive'] = False
        return state

    # Self
    if nh in state['snake']:
        state['alive'] = False
        return state

    state['snake'].insert(0, nh)
    if nh == state['food']:
        state['score'] += 10
        state['food'] = _place_food(h, w, state['snake'])
    else:
        state['snake'].pop()

    return state


# === Rendering ===

def render(stdscr, state):
    stdscr.erase()
    h, w = state['h'], state['w']

    stdscr.border()

    s = f" Score: {state['score']} "
    stdscr.addstr(0, (w - len(s)) // 2, s, curses.A_BOLD)

    fy, fx = state['food']
    try:
        stdscr.addch(fy, fx, '*', curses.A_BOLD)
    except curses.error:
        pass

    for i, (y, x) in enumerate(state['snake']):
        try:
            stdscr.addch(y, x, 'O' if i == 0 else '█')
        except curses.error:
            pass

    stdscr.refresh()


def render_game_over(stdscr, score, h, w):
    stdscr.erase()
    for i, (text, bold) in enumerate([
        ("GAME OVER", True),
        (f"Final Score: {score}", False),
        ("r = restart / q = quit", False),
    ]):
        stdscr.addstr(h // 2 - 1 + i, (w - len(text)) // 2, text,
                      curses.A_BOLD if bold else 0)
    stdscr.refresh()

    stdscr.nodelay(False)
    while True:
        k = stdscr.getch()
        if k == ord('q'): return False
        if k == ord('r'): return True


# === Main Loop ===

def main(stdscr):
    curses.curs_set(0)

    while True:
        h, w = stdscr.getmaxyx()
        stdscr.nodelay(True)
        stdscr.timeout(100)

        state = initial_state(h, w)

        while state['alive']:
            key = stdscr.getch()
            state = process_input(state, key)
            state = step(state)
            if state['alive']:
                render(stdscr, state)

        if not render_game_over(stdscr, state['score'], h, w):
            break


if __name__ == "__main__":
    curses.wrapper(main)
