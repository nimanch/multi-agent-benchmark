#!/usr/bin/env python3
"""Snake Game - Generated via DeerFlow 2.0 + Spec Kit workflow.

DeerFlow's research agent analyzed terminal game patterns.
Spec Kit structured the requirements as feature specs.
Implementation follows spec-driven scenarios.

Architecture: State machine pattern with enum-based states.
"""

import curses
import random
from enum import Enum, auto


class State(Enum):
    PLAYING = auto()
    GAME_OVER = auto()
    QUIT = auto()


class Vec:
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

    _reverse = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

    @classmethod
    def opposite(cls, d):
        return cls._reverse[d]


class SnakeGame:
    """Complete snake game with state machine control flow."""

    KEY_MAP = {
        curses.KEY_UP: Vec.UP,
        curses.KEY_DOWN: Vec.DOWN,
        curses.KEY_LEFT: Vec.LEFT,
        curses.KEY_RIGHT: Vec.RIGHT,
    }

    def __init__(self, stdscr):
        self.scr = stdscr
        curses.curs_set(0)
        self.h, self.w = stdscr.getmaxyx()

    def run(self):
        """Main entry: run game rounds until quit."""
        while True:
            result = self._round()
            if result == State.QUIT:
                return

    def _round(self):
        """Play one round of snake."""
        self.scr.nodelay(True)
        self.scr.timeout(100)

        h, w = self.h, self.w
        cy, cx = h // 2, w // 2

        snake = [(cy, cx), (cy, cx - 1), (cy, cx - 2)]
        direction = Vec.RIGHT
        score = 0
        food = self._spawn_food(snake)

        while True:
            key = self.scr.getch()
            if key in self.KEY_MAP:
                nd = self.KEY_MAP[key]
                if nd != Vec.opposite(direction):
                    direction = nd

            # Advance
            dy, dx = direction
            new_head = (snake[0][0] + dy, snake[0][1] + dx)

            # Collision checks
            if not (0 < new_head[0] < h - 1 and 0 < new_head[1] < w - 1):
                return self._game_over(score)
            if new_head in snake:
                return self._game_over(score)

            snake.insert(0, new_head)
            if new_head == food:
                score += 10
                food = self._spawn_food(snake)
            else:
                snake.pop()

            self._draw(snake, food, score)

    def _spawn_food(self, snake):
        s = set(snake)
        while True:
            p = (random.randint(1, self.h - 2), random.randint(1, self.w - 2))
            if p not in s:
                return p

    def _draw(self, snake, food, score):
        self.scr.erase()
        h, w = self.h, self.w

        # Border using curses built-in
        self.scr.border()

        # Score
        s = f" Score: {score} "
        self.scr.addstr(0, (w - len(s)) // 2, s, curses.A_BOLD)

        # Food
        try:
            self.scr.addch(food[0], food[1], '*', curses.A_BOLD)
        except curses.error:
            pass

        # Snake
        for i, (y, x) in enumerate(snake):
            try:
                self.scr.addch(y, x, 'O' if i == 0 else '█')
            except curses.error:
                pass

        self.scr.refresh()

    def _game_over(self, score):
        h, w = self.h, self.w
        self.scr.erase()
        lines = ["GAME OVER", f"Final Score: {score}", "r = restart  q = quit"]
        for i, line in enumerate(lines):
            attr = curses.A_BOLD if i == 0 else 0
            self.scr.addstr(h // 2 - 1 + i, (w - len(line)) // 2, line, attr)
        self.scr.refresh()

        self.scr.nodelay(False)
        while True:
            k = self.scr.getch()
            if k == ord('q'):
                return State.QUIT
            if k == ord('r'):
                return State.PLAYING


def main(stdscr):
    SnakeGame(stdscr).run()


if __name__ == "__main__":
    curses.wrapper(main)
