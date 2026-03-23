# Snake Game Specification

## Overview
A terminal-based Snake game implemented in Python using the `curses` library.

## Requirements

### Core Gameplay
1. **Snake Movement**: The snake moves continuously in one direction. The player controls direction using arrow keys.
2. **Food**: A single piece of food appears at a random position. When eaten, new food spawns.
3. **Growth**: The snake grows by one segment each time it eats food.
4. **Score**: Score increases by 10 points per food eaten. Displayed during gameplay.

### Controls
- Arrow keys (UP, DOWN, LEFT, RIGHT) change snake direction
- Snake cannot reverse direction (e.g., moving right cannot immediately go left)

### Game Over Conditions
- **Wall collision**: Snake head hits any edge of the terminal window
- **Self collision**: Snake head hits any part of its own body

### Display
- Game area bounded by terminal window
- Snake rendered as `█` (body) and `O` (head)
- Food rendered as `*`
- Score displayed at top of screen
- Border drawn around play area

### Game Over Screen
- Display "GAME OVER" message
- Show final score
- Offer option to press 'q' to quit or 'r' to restart

### Technical Requirements
- Language: Python 3.x
- Library: `curses` (standard library, no external deps)
- Single file implementation preferred
- Game speed: 100ms tick (adjustable)
- Minimum terminal size: 20x10

## Acceptance Criteria
- [ ] Snake moves continuously
- [ ] Arrow keys change direction
- [ ] Food spawns randomly
- [ ] Score tracks and displays
- [ ] Wall collision ends game
- [ ] Self collision ends game
- [ ] Snake grows when eating
- [ ] Game over screen with final score
- [ ] Restart option works
