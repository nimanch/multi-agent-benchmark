import curses
import random

# Game constants
SNAKE_CHAR = '█'
FOOD_CHAR = '*'
HEAD_CHAR = 'O'
BORDER_CHAR = '#'
SCORE_TEXT = 'Score: '
TICK_RATE = 100  # milliseconds

def main(stdscr):
    # Setup
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(TICK_RATE)

    # Get terminal size
    sh, sw = stdscr.getmaxyx()
    if sh < 10 or sw < 20:
        stdscr.clear()
        stdscr.addstr(0, 0, "Terminal size must be at least 20x10")
        stdscr.refresh()
        stdscr.getch()
        return

    # Initial game state
    snake = [[sh // 2, sw // 4]]
    direction = curses.KEY_RIGHT
    food = [sh // 2, sw // 2]
    score = 0

    # Place initial food
    stdscr.addch(food[0], food[1], FOOD_CHAR)

    while True:
        # Draw border
        stdscr.clear()
        for x in range(sw):
            stdscr.addch(0, x, BORDER_CHAR)
            stdscr.addch(sh - 1, x, BORDER_CHAR)
        for y in range(sh):
            stdscr.addch(y, 0, BORDER_CHAR)
            stdscr.addch(y, sw - 1, BORDER_CHAR)

        # Draw score
        stdscr.addstr(0, 2, f"{SCORE_TEXT}{score}")

        # Capture user input
        try:
            key = stdscr.getch()
            if key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                # Prevent snake from reversing direction
                if (key == curses.KEY_UP and direction != curses.KEY_DOWN) or \
                   (key == curses.KEY_DOWN and direction != curses.KEY_UP) or \
                   (key == curses.KEY_LEFT and direction != curses.KEY_RIGHT) or \
                   (key == curses.KEY_RIGHT and direction != curses.KEY_LEFT):
                    direction = key
        except:
            pass

        # Calculate new head position
        head = snake[0][:]
        if direction == curses.KEY_UP:
            head[0] -= 1
        elif direction == curses.KEY_DOWN:
            head[0] += 1
        elif direction == curses.KEY_LEFT:
            head[1] -= 1
        elif direction == curses.KEY_RIGHT:
            head[1] += 1

        # Check for collisions
        if head in snake or head[0] == 0 or head[0] == sh - 1 or head[1] == 0 or head[1] == sw - 1:
            stdscr.clear()
            stdscr.addstr(sh // 2 - 1, sw // 2 - 5, "GAME OVER")
            stdscr.addstr(sh // 2, sw // 2 - 7, f"Final Score: {score}")
            stdscr.addstr(sh // 2 + 1, sw // 2 - 11, "Press 'r' to restart or 'q' to quit.")
            stdscr.refresh()

            while True:
                key = stdscr.getch()
                if key == ord('q'):
                    return
                elif key == ord('r'):
                    main(stdscr)
                    return

        # Check for food consumption
        if head == food:
            score += 10
            # Spawn new food
            while food in snake:
                food = [random.randint(1, sh - 2), random.randint(1, sw - 2)]
        else:
            # Move snake
            snake.pop()

        # Add new head to snake
        snake.insert(0, head)

        # Draw food and snake
        stdscr.addch(food[0], food[1], FOOD_CHAR)
        stdscr.addch(snake[0][0], snake[0][1], HEAD_CHAR)
        for segment in snake[1:]:
            stdscr.addch(segment[0], segment[1], SNAKE_CHAR)

        stdscr.refresh()

curses.wrapper(main)
