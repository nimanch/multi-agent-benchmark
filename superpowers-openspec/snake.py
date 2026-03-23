#!/usr/bin/env python3
"""Snake Game - Generated via Superpowers + OpenSpec workflow.

Superpowers subagent-driven-development orchestrated the pipeline.
OpenSpec provided the spec structure via:
  opsx:plan → task breakdown in openspec/ directory
  opsx:apply → implementation of each task
  opsx:archive → archived completed change

Architecture: Functional style with state dataclass.
"""

import curses
import random
from dataclasses import dataclass, field
from typing import Tuple, List


@dataclass
class GameState:
    """Immutable-ish game state, updated each tick."""
    snake: List[Tuple[int, int]] = field(default_factory=list)
    direction: Tuple[int, int] = (0, 1)
    food: Tuple[int, int] = (0, 0)
    score: int = 0
    alive: bool = True
    height: int = 0
    width: int = 0


# Direction constants
DIRECTIONS = {
    curses.KEY_UP: (-1, 0),
    curses.KEY_DOWN: (1, 0),
    curses.KEY_LEFT: (0, -1),
    curses.KEY_RIGHT: (0, 1),
}
REVERSE = {(-1, 0): (1, 0), (1, 0): (-1, 0), (0, -1): (0, 1), (0, 1): (0, -1)}


def new_game(h: int, w: int) -> GameState:
    """Create a fresh game state."""
    mid_y, mid_x = h // 2, w // 2
    snake = [(mid_y, mid_x), (mid_y, mid_x - 1), (mid_y, mid_x - 2)]
    food = random_food(h, w, snake)
    return GameState(snake=snake, direction=(0, 1), food=food, score=0,
                     alive=True, height=h, width=w)


def random_food(h: int, w: int, snake: List[Tuple[int, int]]) -> Tuple[int, int]:
    """Spawn food not on snake."""
    while True:
        pos = (random.randint(1, h - 2), random.randint(1, w - 2))
        if pos not in snake:
            return pos


def handle_input(state: GameState, key: int) -> GameState:
    """Process input, update direction if valid."""
    if key in DIRECTIONS:
        new_dir = DIRECTIONS[key]
        if new_dir != REVERSE.get(state.direction):
            state.direction = new_dir
    return state


def tick(state: GameState) -> GameState:
    """Advance game by one step."""
    if not state.alive:
        return state

    dy, dx = state.direction
    head = state.snake[0]
    new_head = (head[0] + dy, head[1] + dx)

    # Wall collision
    if (new_head[0] <= 0 or new_head[0] >= state.height - 1 or
            new_head[1] <= 0 or new_head[1] >= state.width - 1):
        state.alive = False
        return state

    # Self collision
    if new_head in state.snake:
        state.alive = False
        return state

    state.snake.insert(0, new_head)

    if new_head == state.food:
        state.score += 10
        state.food = random_food(state.height, state.width, state.snake)
    else:
        state.snake.pop()

    return state


def render(stdscr, state: GameState):
    """Draw the game."""
    stdscr.erase()
    h, w = state.height, state.width

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
    s = f" Score: {state.score} "
    stdscr.addstr(0, (w - len(s)) // 2, s, curses.A_BOLD)

    # Food
    try:
        stdscr.addch(state.food[0], state.food[1], '*', curses.A_BOLD)
    except curses.error:
        pass

    # Snake
    for i, (y, x) in enumerate(state.snake):
        try:
            stdscr.addch(y, x, 'O' if i == 0 else '█')
        except curses.error:
            pass

    stdscr.refresh()


def render_game_over(stdscr, score: int, h: int, w: int) -> bool:
    """Show game over screen. Returns True to restart, False to quit."""
    stdscr.erase()
    lines = ["GAME OVER", f"Final Score: {score}", "'r' restart / 'q' quit"]
    for i, line in enumerate(lines):
        stdscr.addstr(h // 2 - 1 + i, (w - len(line)) // 2, line,
                      curses.A_BOLD if i == 0 else 0)
    stdscr.refresh()
    stdscr.nodelay(False)
    while True:
        k = stdscr.getch()
        if k == ord('q'):
            return False
        if k == ord('r'):
            return True


def main(stdscr):
    curses.curs_set(0)

    while True:
        h, w = stdscr.getmaxyx()
        stdscr.nodelay(True)
        stdscr.timeout(100)

        state = new_game(h, w)

        while state.alive:
            key = stdscr.getch()
            state = handle_input(state, key)
            state = tick(state)
            if state.alive:
                render(stdscr, state)

        if not render_game_over(stdscr, state.score, h, w):
            break


if __name__ == "__main__":
    curses.wrapper(main)
