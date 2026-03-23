#!/usr/bin/env python3
"""Snake Game - Generated via Superpowers + Spec Kit workflow.

Superpowers orchestrated the multi-agent pipeline.
Spec Kit provided spec-driven development structure:
  - specify init → created openspec/ directory
  - Scenarios defined in feature specs
  - Implementation driven by acceptance criteria
  - Architecture: modular with clear separation of concerns
"""

import curses
import random


class GameConfig:
    """Game configuration constants (from spec)."""
    TICK_MS = 100
    FOOD_CHAR = '*'
    HEAD_CHAR = 'O'
    BODY_CHAR = '█'
    SCORE_INCREMENT = 10
    MIN_WIDTH = 20
    MIN_HEIGHT = 10


class Direction:
    """Direction vectors with reverse-prevention."""
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

    OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}

    @classmethod
    def is_valid_change(cls, current, new):
        return new != cls.OPPOSITES.get(current)


class Snake:
    """Snake entity with movement and collision logic."""

    def __init__(self, start_y, start_x):
        self.body = [(start_y, start_x), (start_y, start_x - 1), (start_y, start_x - 2)]
        self.direction = Direction.RIGHT
        self.grow_pending = False

    @property
    def head(self):
        return self.body[0]

    def change_direction(self, new_dir):
        if Direction.is_valid_change(self.direction, new_dir):
            self.direction = new_dir

    def move(self):
        dy, dx = self.direction
        new_head = (self.head[0] + dy, self.head[1] + dx)
        self.body.insert(0, new_head)
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False

    def grow(self):
        self.grow_pending = True

    def collides_with_self(self):
        return self.head in self.body[1:]

    def collides_with_wall(self, h, w):
        y, x = self.head
        return y <= 0 or y >= h - 1 or x <= 0 or x >= w - 1


class Food:
    """Food spawning logic."""

    def __init__(self, h, w, snake_body):
        self.position = self._spawn(h, w, snake_body)

    def _spawn(self, h, w, snake_body):
        while True:
            y = random.randint(1, h - 2)
            x = random.randint(1, w - 2)
            if (y, x) not in snake_body:
                return (y, x)

    def respawn(self, h, w, snake_body):
        self.position = self._spawn(h, w, snake_body)


class Renderer:
    """Handles all screen drawing."""

    @staticmethod
    def draw_border(stdscr, h, w):
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

    @staticmethod
    def draw_score(stdscr, score, w):
        s = f" Score: {score} "
        stdscr.addstr(0, (w - len(s)) // 2, s, curses.A_BOLD)

    @staticmethod
    def draw_snake(stdscr, snake):
        for i, (y, x) in enumerate(snake.body):
            try:
                ch = GameConfig.HEAD_CHAR if i == 0 else GameConfig.BODY_CHAR
                stdscr.addch(y, x, ch)
            except curses.error:
                pass

    @staticmethod
    def draw_food(stdscr, food):
        try:
            stdscr.addch(food.position[0], food.position[1], GameConfig.FOOD_CHAR, curses.A_BOLD)
        except curses.error:
            pass

    @staticmethod
    def draw_game_over(stdscr, score, h, w):
        stdscr.erase()
        msgs = ["GAME OVER", f"Final Score: {score}", "Press 'r' to restart or 'q' to quit"]
        for i, msg in enumerate(msgs):
            stdscr.addstr(h // 2 - 1 + i, (w - len(msg)) // 2, msg,
                          curses.A_BOLD if i == 0 else 0)
        stdscr.refresh()


class Game:
    """Main game controller."""

    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)

    def run(self):
        while True:
            if not self._play_round():
                break

    def _play_round(self):
        h, w = self.stdscr.getmaxyx()
        assert h >= GameConfig.MIN_HEIGHT and w >= GameConfig.MIN_WIDTH, "Terminal too small"

        self.stdscr.nodelay(True)
        self.stdscr.timeout(GameConfig.TICK_MS)

        snake = Snake(h // 2, w // 2)
        food = Food(h, w, snake.body)
        score = 0

        key_map = {
            curses.KEY_UP: Direction.UP,
            curses.KEY_DOWN: Direction.DOWN,
            curses.KEY_LEFT: Direction.LEFT,
            curses.KEY_RIGHT: Direction.RIGHT,
        }

        while True:
            key = self.stdscr.getch()
            if key in key_map:
                snake.change_direction(key_map[key])

            snake.move()

            if snake.collides_with_wall(h, w) or snake.collides_with_self():
                break

            if snake.head == food.position:
                score += GameConfig.SCORE_INCREMENT
                snake.grow()
                food.respawn(h, w, snake.body)

            self.stdscr.erase()
            Renderer.draw_border(self.stdscr, h, w)
            Renderer.draw_score(self.stdscr, score, w)
            Renderer.draw_food(self.stdscr, food)
            Renderer.draw_snake(self.stdscr, snake)
            self.stdscr.refresh()

        Renderer.draw_game_over(self.stdscr, score, h, w)
        self.stdscr.nodelay(False)
        while True:
            key = self.stdscr.getch()
            if key == ord('q'):
                return False
            elif key == ord('r'):
                return True


def main():
    curses.wrapper(lambda stdscr: Game(stdscr).run())


if __name__ == "__main__":
    main()
