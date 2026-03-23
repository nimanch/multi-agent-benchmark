# Snake Game Implementation Evaluation

## Summary Table

| Implementation | Spec Compliance | Correctness | Code Quality | Completeness | Robustness | **Total** |
|---|---|---|---|---|---|---|
| **superpowers-gsd** | 5 | 4 | 4 | 4 | 3 | **20** |
| **superpowers-speckit** | 4 | 3 | 5 | 4 | 3 | **19** |
| **superpowers-openspec** | 4 | 4 | 4 | 3 | 2 | **17** |
| **deerflow-gsd** | 5 | 4 | 4 | 5 | 4 | **22** |
| **deerflow-speckit** | 5 | 4 | 4 | 3 | 2 | **18** |
| **deerflow-openspec** | 5 | 4 | 3 | 3 | 2 | **17** |
| **squad-gsd** | 5 | 4 | 4 | 4 | 4 | **21** |
| **squad-speckit** | 4 | 3 | 4 | 4 | 2 | **17** |
| **squad-openspec** | 5 | 4 | 4 | 3 | 2 | **18** |

## Spec Requirements Checklist

| Requirement | SP-GSD | SP-SK | SP-OS | DF-GSD | DF-SK | DF-OS | SQ-GSD | SQ-SK | SQ-OS |
|---|---|---|---|---|---|---|---|---|---|
| Continuous movement | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Arrow keys change dir | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| No reverse direction | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Food spawns randomly | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Food rendered as `*` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Head=`O`, Body=`█` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Score +10, displayed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Snake grows on eat | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Wall collision = death | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Self collision = death | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Border around play area | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Game over screen | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Final score shown | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 'q' quit / 'r' restart | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 100ms tick | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Min terminal 20x10 | ✅ | ⚠️ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |

⚠️ = implemented but with issues

---

## Detailed Per-Implementation Analysis

### 1. superpowers-gsd (Score: 20)

**Architecture:** Procedural with clean helper functions. Straightforward and readable.

**Strengths:**
- Every spec requirement implemented correctly
- Manual Unicode box-drawing border (┌─┐│└─┘) — goes beyond `stdscr.border()`
- Clean separation: `init_game`, `spawn_food`, `draw`, `game_over_screen`, `game_loop`
- OPPOSITE dict for direction reversal is clean
- Terminal size check present

**Weaknesses:**
- Terminal size check raises `RuntimeError` inside `curses.wrapper` — will produce ugly traceback instead of graceful message
- No food spawn safety net (infinite loop if board is full, though practically impossible)

**Bugs:** None significant. Growth timing is correct (insert head, conditionally pop tail).

**Spec Compliance: 5** — All requirements met.
**Correctness: 4** — Works correctly; the RuntimeError in curses context is a minor issue.
**Code Quality: 4** — Clean procedural code, well-organized. Not OOP but doesn't need to be.
**Completeness: 4** — Unicode borders are a nice touch, constants well-defined.
**Robustness: 3** — Terminal size check exists but crashes ungracefully. No other error recovery.

---

### 2. superpowers-speckit (Score: 19)

**Architecture:** Full OOP — `GameConfig`, `Direction`, `Snake`, `Food`, `Renderer`, `Game` classes. Best architecture of all 9.

**Strengths:**
- Excellent separation of concerns
- `Snake` class encapsulates movement, collision, growth logic
- `Renderer` is fully static — easy to test or swap
- `Direction.is_valid_change()` classmethod is elegant
- Protocol-like structure without over-engineering

**Weaknesses:**
- **Grow timing bug**: When food is eaten, `snake.grow()` sets `grow_pending = True`, but `snake.move()` already executed for this tick. The snake doesn't actually grow until the *next* tick. The snake still grows by exactly 1 segment (so functionally correct), but there's a 1-frame delay where the food disappears before the snake visually grows. Subtle but real.
- Terminal size uses `assert` — will crash with `AssertionError` and can be disabled with `-O` flag

**Bugs:** Grow-timing delay (see above).

**Spec Compliance: 4** — Growth is technically delayed by one frame.
**Correctness: 3** — The grow delay is a real bug, though it doesn't break gameplay.
**Code Quality: 5** — Best architecture of all implementations. Production-grade OOP.
**Completeness: 4** — Good class design, config constants.
**Robustness: 3** — `assert` for terminal size is fragile. Otherwise decent error handling.

---

### 3. superpowers-openspec (Score: 17)

**Architecture:** Functional with `GameState` dataclass. Clean separation of pure logic and rendering.

**Strengths:**
- Dataclass for state is clean and inspectable
- `handle_input` and `tick` are pure-ish functions (mutate state but conceptually clean)
- Type hints throughout

**Weaknesses:**
- **No terminal size check** — will just run on any size terminal
- Despite using dataclass, state is mutated in-place (not truly immutable as the docstring claims)
- Manual Unicode border drawing (copied pattern from superpowers-gsd)

**Bugs:** None significant.

**Spec Compliance: 4** — Missing minimum terminal size check.
**Correctness: 4** — Works correctly, no gameplay bugs.
**Code Quality: 4** — Good functional approach, type hints. The "immutable-ish" comment is misleading.
**Completeness: 3** — Implements spec, nothing extra.
**Robustness: 2** — No terminal size check, no error recovery.

---

### 4. deerflow-gsd (Score: 22) ⭐ BEST

**Architecture:** Clean procedural with well-named functions. Module-style pipeline.

**Strengths:**
- **Food placement has attempt limit** (1000 attempts with fallback) — only implementation to handle this edge case
- Terminal size check with user-friendly message (displays "Terminal too small!" and waits)
- `move_snake` returns `(new_snake, ate_food)` tuple — clean functional interface
- `check_collision` is a separate, testable function
- Game over screen uses a decorative box (╔══╗ etc.) — nice touch
- `sys` import suggests awareness of system-level concerns

**Weaknesses:**
- The food fallback position `(1, 1)` could overlap with snake (though the scenario is nearly impossible)
- Decorative game-over box has fixed width — won't scale if score is very large

**Bugs:** None.

**Spec Compliance: 5** — All requirements met.
**Correctness: 4** — Works correctly. Fallback food position is imperfect but practically irrelevant.
**Code Quality: 4** — Clean, well-structured, good naming. Not OOP but well-organized.
**Completeness: 5** — Food spawn safety, decorative game-over, terminal size check with graceful handling, attempt limit.
**Robustness: 4** — Best error handling of all: terminal size message, food spawn safety, graceful patterns.

---

### 5. deerflow-speckit (Score: 18)

**Architecture:** OOP with `State` enum and `Vec` direction class. State machine pattern.

**Strengths:**
- `State` enum (PLAYING, GAME_OVER, QUIT) is a clean control flow pattern
- `_round()` returns `State` enum values — expressive
- `Vec.opposite()` classmethod is clean
- Compact and readable

**Weaknesses:**
- **No terminal size check**
- `self.h, self.w` set once in `__init__` — won't adapt if terminal is resized during play
- The State enum is declared but PLAYING is never really used as a state check (just returned to signal restart)

**Bugs:** None.

**Spec Compliance: 5** — All gameplay requirements met.
**Correctness: 4** — Works correctly. Terminal resize not handled.
**Code Quality: 4** — Good OOP, state machine pattern is appropriate.
**Completeness: 3** — Implements spec, no extras.
**Robustness: 2** — No terminal size check, terminal dimensions cached at init.

---

### 6. deerflow-openspec (Score: 17)

**Architecture:** Event-driven with `EventBus` and `SnakeEngine`. Most complex architecture.

**Strengths:**
- Uses `deque` for snake — `appendleft`/`pop` is O(1) vs list `insert(0,...)` which is O(n). Only implementation to get this right performance-wise.
- Event bus is a real pattern, properly implemented
- Engine/Display separation is clean

**Weaknesses:**
- **Over-engineered**: EventBus is defined and events are emitted, but nothing subscribes to them! The events (`EVT_MOVE`, `EVT_EAT`, `EVT_DIE`) are fired into the void. This is architecture astronautics.
- **No terminal size check**
- String-based direction names add unnecessary indirection
- `EventBus` adds complexity without benefit in a single-file game

**Bugs:** None gameplay-related. The unused event system is a design issue, not a bug.

**Spec Compliance: 5** — All requirements met.
**Correctness: 4** — Works correctly despite the unused event system.
**Code Quality: 3** — Over-engineered. EventBus with no subscribers is dead code. `deque` usage is good though.
**Completeness: 3** — Spec met, but the "extras" (EventBus) add nothing useful.
**Robustness: 2** — No terminal size check, no error handling.

---

### 7. squad-gsd (Score: 21)

**Architecture:** Clean procedural. Simplest and most readable implementation.

**Strengths:**
- **Terminal size check with friendly message** and graceful exit
- Cleanest code of all — easy to read, well-named functions
- `_spawn`, `_render`, `_game_over` use underscore convention for internal helpers
- `play()` returns bool — simple restart mechanism
- No over-engineering, no under-engineering

**Weaknesses:**
- Nothing significant. It's just... simple and correct.

**Bugs:** None.

**Spec Compliance: 5** — All requirements met.
**Correctness: 4** — Works correctly throughout.
**Code Quality: 4** — Clean, readable, well-organized. Could benefit from constants for directions.
**Completeness: 4** — Terminal size check, clean error handling.
**Robustness: 4** — Terminal size check with user-friendly message, graceful exit.

---

### 8. squad-speckit (Score: 17)

**Architecture:** OOP with `Position` class, `Protocol` type hint, `SnakeEntity`, `FoodEntity`. Most type-heavy.

**Strengths:**
- `Position` class with `__add__`, `__eq__`, `__hash__` is well-implemented
- `__slots__` on Position for memory efficiency
- `Renderable` Protocol defined (though unused in practice)
- Type hints throughout

**Weaknesses:**
- **Same grow-timing bug as superpowers-speckit**: `snake.eat()` is called after `snake.advance()`, so growth is delayed by one tick
- **`Renderable` Protocol is declared but never used** — dead code
- `FoodEntity._place()` has awkward handling to convert `Position` to tuple for set membership
- **No terminal size check**
- Over-engineered for what it does

**Bugs:** Grow-timing delay (same as superpowers-speckit).

**Spec Compliance: 4** — Growth delayed by one frame.
**Correctness: 3** — Grow-timing bug is real. Also Position conversion in FoodEntity is clunky.
**Code Quality: 4** — Good OOP, but unused Protocol and awkward Position/tuple conversion hurt.
**Completeness: 4** — Type system, Protocol, Position class show effort.
**Robustness: 2** — No terminal size check, no error recovery.

---

### 9. squad-openspec (Score: 18)

**Architecture:** Dict-based state, functional style. "TDD-inspired" with pure logic functions.

**Strengths:**
- `initial_state`, `process_input`, `step` are genuinely testable pure functions
- Dict-based state is simple and inspectable
- String-based direction names with lookup dicts are clear
- Separation of logic and rendering is the cleanest of any implementation
- Most testable architecture

**Weaknesses:**
- **No terminal size check**
- Dict-based state lacks type safety (easy to typo a key)
- No extras beyond spec

**Bugs:** None.

**Spec Compliance: 5** — All requirements met.
**Correctness: 4** — Works correctly.
**Code Quality: 4** — Clean functional design. Dict state is a tradeoff (testable but not type-safe).
**Completeness: 3** — Spec only, no extras.
**Robustness: 2** — No terminal size check, no error handling.

---

## Final Ranking

| Rank | Implementation | Score | Commentary |
|---|---|---|---|
| 🥇 1 | **deerflow-gsd** | 22 | Best overall. Only one with food-spawn safety net. Graceful terminal size check. Decorative game-over box. No bugs. |
| 🥈 2 | **squad-gsd** | 21 | Cleanest, most readable code. Does everything right with zero over-engineering. Terminal size check. |
| 🥉 3 | **superpowers-gsd** | 20 | Solid all-around. Unicode borders. Terminal size check (though crashes ungracefully). |
| 4 | **superpowers-speckit** | 19 | Best architecture/OOP, but grow-timing bug costs it. |
| 5 | **squad-openspec** | 18 | Most testable design. Clean but bare-bones. |
| 5 | **deerflow-speckit** | 18 | Good state machine pattern. Caches terminal size (fragile). |
| 7 | **superpowers-openspec** | 17 | Decent functional approach. Misleading "immutable" claim. |
| 7 | **deerflow-openspec** | 17 | EventBus with zero subscribers = architecture astronautics. `deque` is nice though. |
| 7 | **squad-speckit** | 17 | Over-typed. Unused Protocol. Grow-timing bug. |

---

## Observations

### GSD consistently wins
All three GSD implementations (deerflow, squad, superpowers) ranked in the top 3. GSD's project scaffolding approach appears to produce more pragmatic, complete implementations than spec-driven or open-spec workflows.

### Spec requirements ALL implementations got right
- Continuous movement with arrow keys
- Food as `*`, head as `O`, body as `█`
- Score +10, displayed at top
- Direction reversal prevention
- Wall and self collision
- Game over screen with restart/quit
- 100ms tick rate

### Spec requirements commonly missed
- **Minimum terminal size check (20×10)**: Only 3 of 9 implemented this (superpowers-gsd, deerflow-gsd, squad-gsd)

### Ambiguous spec requirements
1. **"Border drawn around play area"** — The spec doesn't specify whether to use `stdscr.border()` (simple ASCII) or manual Unicode box-drawing characters. Both are valid interpretations. Three implementations (superpowers-gsd, superpowers-speckit, superpowers-openspec) drew manual Unicode borders; the rest used `stdscr.border()`.
2. **"Game speed: 100ms tick (adjustable)"** — "Adjustable" is mentioned but no mechanism specified. All implementations hardcode 100ms. None provide runtime speed adjustment. This requirement is ambiguous — does "adjustable" mean configurable constant, or runtime control?
3. **Score display location** — "Score displayed at top of screen" is met by all, but some overlay it on the border while others use separate space. The spec doesn't clarify.

### The grow-timing bug
Two implementations (superpowers-speckit, squad-speckit) share the same architectural pattern where `snake.advance()` is called before `snake.eat()`, causing growth to be delayed by one tick. This is a direct consequence of the "advance then check food" pattern combined with a `grow_pending` flag. The other 7 implementations use the simpler "insert head, conditionally pop tail" pattern which avoids this entirely.

### Over-engineering correlation
The more architecturally ambitious implementations (deerflow-openspec's EventBus, squad-speckit's Protocol/Position) scored lower overall. The EventBus has zero subscribers. The Protocol is never used for dispatch. These are patterns looking for a problem in a ~100-line game. Pragmatism won.
