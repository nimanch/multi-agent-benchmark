import curses
import random
import time

# Constants
TICK_RATE = 0.1  # Game tick in seconds
SNAKE_CHAR = '█'
FOOD_CHAR = '*'
BORDER_CHAR = '#'
HEAD_CHAR = 'O'
SCORE_TEXT = " Score: {} "
GAME_OVER_TEXT = "GAME OVER - Press 'r' to restart or 'q' to quit"

# Directions
UP = (-1, 0)
DOWN = (1, 0)
LEFT = (0, -1)
RIGHT = (0, 1)

class SnakeGame:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.running = True
        self.restart = False
        self.init_game()

    def init_game(self):
        # Initialize game state
        self.direction = RIGHT
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.food = self.place_food()
        self.score = 0
        self.height, self.width = self.stdscr.getmaxyx()

    def place_food(self):
        while True:
            food = (random.randint(1, self.height - 2), random.randint(1, self.width - 2))
            if food not in self.snake:
                return food

    def render(self):
        self.stdscr.clear()
        # Draw border
        for x in range(self.width):
            self.stdscr.addch(0, x, BORDER_CHAR)
            self.stdscr.addch(self.height - 1, x, BORDER_CHAR)
        for y in range(self.height):
            self.stdscr.addch(y, 0, BORDER_CHAR)
            self.stdscr.addch(y, self.width - 1, BORDER_CHAR)

        # Draw snake
        for y, x in self.snake[1:]:
            self.stdscr.addch(y, x, SNAKE_CHAR)
        # Draw snake head
        head_y, head_x = self.snake[0]
        self.stdscr.addch(head_y, head_x, HEAD_CHAR)

        # Draw food
        food_y, food_x = self.food
        self.stdscr.addch(food_y, food_x, FOOD_CHAR)

        # Draw score
        self.stdscr.addstr(0, 2, SCORE_TEXT.format(self.score))
        self.stdscr.refresh()

    def update(self):
        head_y, head_x = self.snake[0]
        move_y, move_x = self.direction
        new_head = (head_y + move_y, head_x + move_x)

        # Check collisions
        if (new_head[0] in (0, self.height - 1) or
                new_head[1] in (0, self.width - 1) or
                new_head in self.snake):
            self.game_over()
            return

        # Update snake position
        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            self.food = self.place_food()
        else:
            self.snake.pop()  # Remove tail if no food eaten

    def handle_input(self):
        key = self.stdscr.getch()
        if key == curses.KEY_UP and self.direction != DOWN:
            self.direction = UP
        elif key == curses.KEY_DOWN and self.direction != UP:
            self.direction = DOWN
        elif key == curses.KEY_LEFT and self.direction != RIGHT:
            self.direction = LEFT
        elif key == curses.KEY_RIGHT and self.direction != LEFT:
            self.direction = RIGHT
        elif key == ord('q'):
            self.running = False

    def game_over(self):
        self.stdscr.clear()
        self.stdscr.addstr(self.height // 2 - 1, (self.width - len(GAME_OVER_TEXT)) // 2, GAME_OVER_TEXT)
        self.stdscr.addstr(self.height // 2, (self.width - len(SCORE_TEXT.format(self.score))) // 2, SCORE_TEXT.format(self.score))
        self.stdscr.refresh()
        while True:
            key = self.stdscr.getch()
            if key == ord('q'):
                self.running = False
                break
            elif key == ord('r'):
                self.restart = True
                break

    def run(self):
        while self.running:
            self.render()
            self.handle_input()
            self.update()
            time.sleep(TICK_RATE)

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    while True:
        game = SnakeGame(stdscr)
        game.run()
        if not game.restart:
            break

curses.wrapper(main)
