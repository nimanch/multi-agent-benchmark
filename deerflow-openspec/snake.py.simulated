#!/usr/bin/env python3
"""Snake Game - Generated via DeerFlow 2.0 + OpenSpec workflow.

DeerFlow orchestrated research → plan → code → review sub-agents.
OpenSpec structured the spec with opsx:plan → opsx:apply workflow.

Architecture: Event-driven with callback pattern.
"""

import curses
import random
from collections import deque

# Events
EVT_MOVE = "move"
EVT_EAT = "eat"
EVT_DIE = "die"
EVT_RESTART = "restart"

# Directions
DIRS = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}
OPPOSITES = {"up": "down", "down": "up", "left": "right", "right": "left"}

KEY_DIR = {
    curses.KEY_UP: "up", curses.KEY_DOWN: "down",
    curses.KEY_LEFT: "left", curses.KEY_RIGHT: "right",
}


class EventBus:
    """Simple event system for game decoupling."""
    def __init__(self):
        self._handlers = {}

    def on(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)

    def emit(self, event, **kwargs):
        for h in self._handlers.get(event, []):
            h(**kwargs)


class SnakeEngine:
    """Core game logic, event-driven."""

    def __init__(self, h, w, bus):
        self.h = h
        self.w = w
        self.bus = bus
        self.reset()

    def reset(self):
        cy, cx = self.h // 2, self.w // 2
        self.snake = deque([(cy, cx), (cy, cx - 1), (cy, cx - 2)])
        self.dir_name = "right"
        self.score = 0
        self.alive = True
        self.food = self._place_food()

    def _place_food(self):
        occupied = set(self.snake)
        while True:
            p = (random.randint(1, self.h - 2), random.randint(1, self.w - 2))
            if p not in occupied:
                return p

    def set_direction(self, dir_name):
        if dir_name and dir_name != OPPOSITES.get(self.dir_name):
            self.dir_name = dir_name

    def step(self):
        if not self.alive:
            return

        dy, dx = DIRS[self.dir_name]
        head = self.snake[0]
        nh = (head[0] + dy, head[1] + dx)

        # Wall check
        if not (0 < nh[0] < self.h - 1 and 0 < nh[1] < self.w - 1):
            self.alive = False
            self.bus.emit(EVT_DIE, score=self.score)
            return

        # Self check
        if nh in self.snake:
            self.alive = False
            self.bus.emit(EVT_DIE, score=self.score)
            return

        self.snake.appendleft(nh)

        if nh == self.food:
            self.score += 10
            self.food = self._place_food()
            self.bus.emit(EVT_EAT, score=self.score)
        else:
            self.snake.pop()

        self.bus.emit(EVT_MOVE)


class Display:
    """Curses renderer."""

    def __init__(self, stdscr):
        self.scr = stdscr
        curses.curs_set(0)

    def render(self, engine):
        self.scr.erase()
        h, w = engine.h, engine.w

        self.scr.border()

        s = f" Score: {engine.score} "
        self.scr.addstr(0, (w - len(s)) // 2, s, curses.A_BOLD)

        try:
            self.scr.addch(engine.food[0], engine.food[1], '*', curses.A_BOLD)
        except curses.error:
            pass

        for i, (y, x) in enumerate(engine.snake):
            try:
                self.scr.addch(y, x, 'O' if i == 0 else '█')
            except curses.error:
                pass

        self.scr.refresh()

    def game_over(self, score, h, w):
        self.scr.erase()
        msgs = ["GAME OVER", f"Final Score: {score}", "r=restart  q=quit"]
        for i, msg in enumerate(msgs):
            self.scr.addstr(h // 2 - 1 + i, (w - len(msg)) // 2, msg,
                            curses.A_BOLD if i == 0 else 0)
        self.scr.refresh()


def main(stdscr):
    h, w = stdscr.getmaxyx()
    display = Display(stdscr)

    while True:
        bus = EventBus()
        engine = SnakeEngine(h, w, bus)

        stdscr.nodelay(True)
        stdscr.timeout(100)

        while engine.alive:
            key = stdscr.getch()
            if key in KEY_DIR:
                engine.set_direction(KEY_DIR[key])
            engine.step()
            if engine.alive:
                display.render(engine)

        display.game_over(engine.score, h, w)
        stdscr.nodelay(False)
        while True:
            k = stdscr.getch()
            if k == ord('q'):
                return
            if k == ord('r'):
                break


if __name__ == "__main__":
    curses.wrapper(main)
