# Evaluating 9 AI Agent Combinations on the Same Snake Game

*Nishant Manchanda · March 2026*

---

There's a new AI coding agent every week. Most benchmarks compare them on vibes. I wanted something more controlled: give multiple agent combinations the same spec, same language, same machine, and compare the output code systematically.

I picked three multi-agent orchestrators (Superpowers, DeerFlow 2.0, Squad) and three spec-driven toolkits (GSD, Spec Kit, OpenSpec), producing a 3×3 matrix of nine implementations. The task: a terminal Snake game in Python curses, from a [shared spec](https://github.com/nimanch/multi-agent-benchmark/blob/main/SNAKE_SPEC.md).

Then I had an LLM judge score each implementation across five dimensions.

The results surprised me. The "best architecture" had a bug. The simplest approach swept the top three spots. And the spec toolkit shaped the code structure more than the orchestrator did.

**Repo**: [github.com/nimanch/multi-agent-benchmark](https://github.com/nimanch/multi-agent-benchmark)

## Methodology

**What was controlled:**
- Identical spec ([SNAKE_SPEC.md](https://github.com/nimanch/multi-agent-benchmark/blob/main/SNAKE_SPEC.md)) — 16 acceptance criteria covering movement, collision, scoring, display, and restart
- Same language: Python 3.x with curses (stdlib only)
- Same machine: NVIDIA Jetson ARM64, 8GB RAM, Ubuntu
- Single-file implementations, zero manual interventions on any of the nine

**What was NOT controlled:**
- **DeerFlow 2.0** couldn't run natively (requires Python 3.12+; Jetson has 3.10). Its multi-agent workflow was simulated following its documented architecture.
- **Squad** requires Copilot Pro+ cloud for native multi-agent. Its Coordinator → specialists pipeline was simulated locally.
- Only **Superpowers** ran as a fully native agent orchestration.

This is a real limitation. The DeerFlow and Squad results reflect their *methodology* applied manually, not their runtime. Take those results with appropriate skepticism.

**Evaluation:** An LLM judge (not me) scored each implementation 1–5 on five dimensions: Spec Compliance, Correctness, Code Quality, Completeness, and Robustness. I reviewed the scores against the code and agreed with most of them, though the evaluation has its own limitations (discussed below).

## The Scores

| Implementation | Spec Compliance | Correctness | Code Quality | Completeness | Robustness | **Total** |
|---|---|---|---|---|---|---|
| deerflow-gsd | 5 | 4 | 4 | 5 | 4 | **22** |
| squad-gsd | 5 | 4 | 4 | 4 | 4 | **21** |
| superpowers-gsd | 5 | 4 | 4 | 4 | 3 | **20** |
| superpowers-speckit | 4 | 3 | 5 | 4 | 3 | **19** |
| deerflow-speckit | 5 | 4 | 4 | 3 | 2 | **18** |
| squad-openspec | 5 | 4 | 4 | 3 | 2 | **18** |
| superpowers-openspec | 4 | 4 | 4 | 3 | 2 | **17** |
| deerflow-openspec | 5 | 4 | 3 | 3 | 2 | **17** |
| squad-speckit | 4 | 3 | 4 | 4 | 2 | **17** |

GSD swept the top three. Every orchestrator paired with GSD outscored the same orchestrator paired with either alternative toolkit.

## Spec Compliance Matrix

Not all "9/9 pass" results are equal. The LLM judge checked 16 specific requirements:

| Requirement | SP-GSD | SP-SK | SP-OS | DF-GSD | DF-SK | DF-OS | SQ-GSD | SQ-SK | SQ-OS |
|---|---|---|---|---|---|---|---|---|---|
| Continuous movement | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Arrow key controls | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| No reverse direction | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Random food spawn | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Food as `*` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Head=`O`, Body=`█` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Score +10, displayed | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Snake grows on eat** | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ |
| Wall collision = death | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Self collision = death | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Border around play area | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Game over screen | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Final score shown | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| q=quit, r=restart | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 100ms tick | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Min terminal 20×10** | ✅ | ⚠️ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |

Two things jump out:

1. **Only 3 of 9 implementations checked minimum terminal size** — and all three were GSD variants. This is a clear spec requirement that 6 implementations simply ignored.
2. **Two implementations (superpowers-speckit, squad-speckit) have a grow-timing bug** where the snake doesn't visually grow until one frame after eating. More on this below.

## The Grow-Timing Bug

The spec says "the snake grows by one segment each time it eats food." Two implementations (superpowers-speckit and squad-speckit) get this subtly wrong due to an architectural choice.

Here's the pattern that causes the bug — from superpowers-speckit:

```python
# Game loop (simplified):
snake.move()                    # advance first
if snake.head == food.position:
    snake.grow()                # sets grow_pending = True
    food.respawn(...)

# Inside Snake.move():
def move(self):
    new_head = (self.head[0] + dy, self.head[1] + dx)
    self.body.insert(0, new_head)
    if not self.grow_pending:   # checked BEFORE grow() is called this tick
        self.body.pop()
    else:
        self.grow_pending = False
```

The problem: `move()` executes before the food check. So when the snake eats food, `grow_pending` is still `False` during that tick's `move()`. The tail gets popped. `grow()` then sets `grow_pending = True`, which takes effect on the *next* tick. The snake still grows by exactly one segment — but there's a one-frame visual glitch where the food disappears before the snake visually extends.

Compare with the pattern used by 7 of 9 implementations (here from deerflow-gsd):

```python
def move_snake(snake, direction, food):
    new_head = (head_y + dy, head_x + dx)
    new_snake = [new_head] + snake[:]
    ate = new_head == food
    if not ate:
        new_snake.pop()         # grow decision is immediate
    return new_snake, ate
```

Insert head, then conditionally pop tail. No deferred flag, no timing issue. The simpler pattern is the correct one.

This is the most interesting result from the evaluation: the implementation with the *best* architecture score (superpowers-speckit: Code Quality 5/5, five clean OOP classes) had a functional bug. The procedural implementations with no classes got the behavior right.

## The Dead EventBus

deerflow-openspec built an event-driven architecture with an `EventBus` class:

```python
class EventBus:
    def on(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)
    def emit(self, event, **kwargs):
        for h in self._handlers.get(event, []):
            h(**kwargs)
```

Events are emitted throughout the game — `EVT_MOVE`, `EVT_EAT`, `EVT_DIE`. But `bus.on()` is never called anywhere. Zero subscribers. The events fire into the void.

The evaluator called this "architecture astronautics," which is fair. The game works fine — the EventBus just doesn't do anything. It's the code equivalent of installing a fire alarm system and never connecting the sirens.

One redeeming quality: deerflow-openspec is the only implementation that uses `collections.deque` for the snake body, giving O(1) head insertion vs O(n) for list `insert(0, ...)`. For a 20×10 terminal it doesn't matter, but it's the technically correct data structure.

## Lines of Code

| Implementation | LOC | Architecture |
|---|---|---|
| squad-gsd | 132 | Clean procedural |
| deerflow-speckit | 152 | State machine + enum |
| squad-openspec | 157 | Dict-state, pure functions |
| deerflow-openspec | 171 | Event-driven (dead EventBus) |
| superpowers-gsd | 178 | Procedural with constants |
| superpowers-openspec | 179 | Functional + dataclass |
| squad-speckit | 180 | Protocol pattern + Position class |
| deerflow-gsd | 181 | Module-style functions |
| superpowers-speckit | 213 | OOP (5 classes) |

Is LOC a meaningful metric here? Probably not on its own. squad-gsd's 132 lines scored 21/25 (second place). superpowers-speckit's 213 lines scored 19/25 (fourth, with a bug). More code meant more architectural ambition, which correlated with more opportunities for bugs and dead code, not with better outcomes.

The range is narrow enough (132–213) that I wouldn't draw strong conclusions. All nine are under 250 lines. This is a small enough problem that code length is mostly noise.

## What the Spec Toolkit Controls vs. What the Orchestrator Controls

The spec toolkit shaped *architecture*:
- **GSD** → procedural, pragmatic, "just make it work"
- **Spec Kit** → OOP, typed, separated concerns, more elaborate class hierarchies
- **OpenSpec** → functional, state-as-data, testable pure functions

The orchestrator shaped *completeness and robustness*:
- All GSD variants checked terminal size. None of the non-GSD variants did.
- deerflow-gsd was the only implementation with a food-spawn safety net (1000 attempts with fallback position)
- Superpowers consistently produced more polished rendering (manual Unicode box-drawing borders)

The interaction between them is what mattered. GSD's milestone-based approach apparently forced all three orchestrators to handle edge cases (terminal size) that the other toolkits didn't prompt for. The spec explicitly says "Minimum terminal size: 20x10" — GSD treated this as a requirement; Spec Kit and OpenSpec apparently didn't surface it as a first-class acceptance criterion.

## The Demos

All nine games running:

| | GSD | Spec Kit | OpenSpec |
|---|---|---|---|
| **Superpowers** | ![superpowers-gsd](https://raw.githubusercontent.com/nimanch/multi-agent-benchmark/main/gifs/superpowers-gsd.gif) | ![superpowers-speckit](https://raw.githubusercontent.com/nimanch/multi-agent-benchmark/main/gifs/superpowers-speckit.gif) | ![superpowers-openspec](https://raw.githubusercontent.com/nimanch/multi-agent-benchmark/main/gifs/superpowers-openspec.gif) |
| **DeerFlow** | ![deerflow-gsd](https://raw.githubusercontent.com/nimanch/multi-agent-benchmark/main/gifs/deerflow-gsd.gif) | ![deerflow-speckit](https://raw.githubusercontent.com/nimanch/multi-agent-benchmark/main/gifs/deerflow-speckit.gif) | ![deerflow-openspec](https://raw.githubusercontent.com/nimanch/multi-agent-benchmark/main/gifs/deerflow-openspec.gif) |
| **Squad** | ![squad-gsd](https://raw.githubusercontent.com/nimanch/multi-agent-benchmark/main/gifs/squad-gsd.gif) | ![squad-speckit](https://raw.githubusercontent.com/nimanch/multi-agent-benchmark/main/gifs/squad-speckit.gif) | ![squad-openspec](https://raw.githubusercontent.com/nimanch/multi-agent-benchmark/main/gifs/squad-openspec.gif) |

## Limitations

This evaluation has real weaknesses:

**Snake is too easy.** All nine implementations work. The interesting differences are in edge cases (terminal size, grow timing) and code style — not in whether the agents could solve the problem. A harder task (multi-file, networking, database) would produce more differentiation.

**Two of three orchestrators were simulated.** DeerFlow and Squad couldn't run natively on the test machine. I followed their documented workflows manually. This means their results reflect the *methodology* more than the *tooling*. If DeerFlow's runtime catches bugs its documented workflow doesn't, we'd see different results with native execution.

**N=1 per combination.** I ran each combination once. LLM outputs are stochastic. Running each combination five times and averaging would be more rigorous. The scores could shift by a few points on re-runs.

**LLM-as-judge.** The evaluation was done by an LLM, not by running a test suite. The grow-timing bug was caught by code inspection, not automated testing. A proper evaluation would include functional tests that exercise each acceptance criterion programmatically.

**Scoring granularity.** 1–5 integer scores across five dimensions give a 5–25 range. The actual spread was 17–22, a 5-point range across 9 implementations. Whether deerflow-gsd at 22 is meaningfully better than squad-gsd at 21 is debatable. The top-3 vs bottom-6 distinction is clearer than individual rankings.

## Conclusions

Three data-driven takeaways:

1. **GSD's spec compliance advantage was decisive.** All three GSD variants scored 5/5 on spec compliance and checked terminal size. The toolkit's milestone-based approach appears to enforce spec requirements more reliably than scenario-based (Spec Kit) or task-based (OpenSpec) approaches. At least for this spec.

2. **Architectural ambition correlated negatively with correctness.** The two implementations with the most classes (superpowers-speckit: 5 classes, squad-speckit: Position + Protocol + entities) both had the grow-timing bug. The implementation with the most elaborate architecture (deerflow-openspec: EventBus) had dead code. The top three scorers were all procedural or simple functional code.

3. **The spec toolkit shaped the code more than the orchestrator.** Across all three orchestrators, GSD produced procedural code, Spec Kit produced OOP code, and OpenSpec produced functional code. The orchestrator affected quality within those patterns but didn't change the patterns themselves.

Whether this generalizes beyond Snake — beyond a well-understood, small, single-file problem — is an open question.

---

*Nishant Manchanda builds things in Seattle.*

*All code and evaluation data: [github.com/nimanch/multi-agent-benchmark](https://github.com/nimanch/multi-agent-benchmark)*
