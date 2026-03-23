# Multi-Agent Snake Game Benchmark

A systematic comparison of 9 combinations of multi-agent orchestrators × spec-driven toolkits, all building the same Python CLI Snake game.

## Quick Start

```bash
# Run any of the 9 snake games:
python3 superpowers-gsd/snake.py
python3 superpowers-speckit/snake.py
python3 superpowers-openspec/snake.py
python3 deerflow-gsd/snake.py
python3 deerflow-speckit/snake.py
python3 deerflow-openspec/snake.py
python3 squad-gsd/snake.py
python3 squad-speckit/snake.py
python3 squad-openspec/snake.py
```

**Requirements**: Python 3.x with `curses` (standard library). Terminal at least 20×10 chars.

**Controls**: Arrow keys to move, `r` to restart, `q` to quit.

## Structure

```
multi-agent-benchmark/
├── SNAKE_SPEC.md           # Common spec all 9 games implement
├── RESULTS.md              # Detailed comparison & analysis
├── ARTICLE.md              # Medium article draft
├── README.md               # This file
├── superpowers-gsd/        # Superpowers + GSD
├── superpowers-speckit/    # Superpowers + Spec Kit
├── superpowers-openspec/   # Superpowers + OpenSpec
├── deerflow-gsd/           # DeerFlow + GSD
├── deerflow-speckit/       # DeerFlow + Spec Kit
├── deerflow-openspec/      # DeerFlow + OpenSpec
├── squad-gsd/              # Squad + GSD
├── squad-speckit/          # Squad + Spec Kit
└── squad-openspec/         # Squad + OpenSpec
```

## The 3×3 Matrix

|  | GSD | Spec Kit | OpenSpec |
|--|-----|----------|---------|
| **Superpowers** | Procedural (178 LOC) | OOP 5-class (213 LOC) 🏆 | Functional+dataclass (179 LOC) |
| **DeerFlow** | Module functions (181 LOC) | State machine (152 LOC) | Event-driven (171 LOC) |
| **Squad** | Clean minimal (132 LOC) | Protocol pattern (180 LOC) | Dict-state pure (157 LOC) |

## Key Findings

1. **Spec Kit produces the most structured code** — OOP patterns, type hints, clear separation
2. **GSD produces the most pragmatic code** — fewest lines, just works
3. **Superpowers' two-stage review catches quality issues** others miss
4. **Squad + OpenSpec is most testable** — pure functions with dict state

Winner: **Superpowers + Spec Kit** for best code quality.

See [RESULTS.md](RESULTS.md) for full analysis and [ARTICLE.md](ARTICLE.md) for the Medium writeup.

## Platform

Tested on NVIDIA Jetson (ARM64, 8GB RAM, Ubuntu, Python 3.10).

## Author

Nishant Manchanda — March 2026
