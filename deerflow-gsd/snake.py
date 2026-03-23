import curses
import random

# Constants
SNAKE_HEAD = 'O'
SNAKE_BODY = '█'
FOOD = '*'
TICK_RATE = 100  # milliseconds
SCORE_DISPLAY = "Score: {}"

# Directions
UP = -1, 0
DOWN = 1, 0
LEFT = 0, -1
RIGHT = 0, 1

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(TICK_RATE)

    # Initialize game state
    sh, sw = stdscr.getmaxyx()
    if sh < 10 or sw < 20:
        stdscr.addstr(0, 0, "Terminal too small! Resize to at least 20x10.")
        stdscr.refresh()
        stdscr.getch()
        return

    snake = [[sh // 2, sw // 2]]
    direction = RIGHT
    food = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
    score = 0

    while True:
        stdscr.clear()

        # Draw border
        for i in range(sw):
            stdscr.addch(0, i, '#')
            stdscr.addch(sh - 1, i, '#')
        for i in range(sh):
            stdscr.addch(i, 0, '#')
            stdscr.addch(i, sw - 1, '#')

        # Draw food
        stdscr.addch(food[0], food[1], FOOD)

        # Draw snake
        for y, x in snake[:-1]:
            stdscr.addch(y, x, SNAKE_BODY)
        stdscr.addch(snake[-1][0], snake[-1][1], SNAKE_HEAD)

        # Display score
        stdscr.addstr(0, 2, SCORE_DISPLAY.format(score))

        # Get user input
        key = stdscr.getch()
        if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
            new_direction = {curses.KEY_UP: UP, curses.KEY_DOWN: DOWN, curses.KEY_LEFT: LEFT, curses.KEY_RIGHT: RIGHT}[key]
            if (new_direction[0] != -direction[0]) or (new_direction[1] != -direction[1]):
                direction = new_direction

        # Update snake position
        new_head = [snake[-1][0] + direction[0], snake[-1][1] + direction[1]]
        if new_head in snake or new_head[0] in [0, sh - 1] or new_head[1] in [0, sw - 1]:
            # Game over
            stdscr.clear()
            msg = "GAME OVER"
            stdscr.addstr(sh // 2, sw // 2 - len(msg) // 2, msg)
            final_score = f"Final Score: {score}"
            stdscr.addstr(sh // 2 + 1, sw // 2 - len(final_score) // 2, final_score)
            stdscr.addstr(sh // 2 + 3, sw // 2 - 7, "Press 'r' to Restart or 'q' to Quit")
            stdscr.refresh()

            while True:
                key = stdscr.getch()
                if key == ord('q'):
                    return
                elif key == ord('r'):
                    return main(stdscr)
        else:
            snake.append(new_head)
            if new_head == food:
                score += 10
                while food in snake:
                    food = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
            else:
                snake.pop(0)

curses.wrapper(main)
