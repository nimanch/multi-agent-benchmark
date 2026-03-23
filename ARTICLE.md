# Evaluating 9 AI Agent Combinations on the Same Snake Game

*Nishant Manchanda · March 2026*

---

There's a new AI coding agent every week. Most benchmarks compare them on vibes. I wanted something more controlled: give multiple agent combinations the same spec, same language, same machine, and compare the output code systematically.

I picked three multi-agent orchestrators ([Superpowers](https://github.com/obra/superpowers), [DeerFlow 2.0](https://github.com/bytedance/deer-flow), [Squad](https://github.com/bradygaster/squad)) and three spec-driven toolkits ([GSD](https://github.com/gsd-build/get-shit-done), [Spec Kit](https://github.com/github/spec-kit), [OpenSpec](https://github.com/Fission-AI/openspec)), producing a 3x3 matrix of nine implementations. The task: a terminal Snake game in Python curses, from a [shared spec](https://github.com/nimanch/multi-agent-benchmark/blob/main/SNAKE_SPEC.md).

Then I had an LLM judge score each implementation across five dimensions.

The results surprised me. The "best architecture" had a bug. The simplest approach swept the top three spots. And the spec toolkit shaped the code structure more than the orchestrator did.

**Repo**: [github.com/nimanch/multi-agent-benchmark](https://github.com/nimanch/multi-agent-benchmark)

## The Tools

Before getting into results, here's what each tool actually does. These aren't interchangeable — they solve fundamentally different problems.

### Orchestrators

**Superpowers** ([github.com/obra/superpowers](https://github.com/obra/superpowers), 94K+ stars) is a subagent-driven development framework. When you give it a task, it doesn't just generate code — it dispatches specialized subagents in parallel. A planning agent breaks the problem down. Implementation agents write code concurrently. Then a two-stage review process kicks in: first a spec-compliance check (does the code match the requirements?), then a code-quality review (is the code well-structured?). Superpowers uses a skill-based architecture where agents have defined capabilities and constraints. It ran natively in this experiment — the only orchestrator that did.

**DeerFlow 2.0** ([github.com/bytedance/deer-flow](https://github.com/bytedance/deer-flow), ByteDance) follows a Research → Plan → Code → Review pipeline. What distinguishes it is the research phase: before any code is written, a research agent examines best practices, common patterns, and potential pitfalls for the task at hand. This front-loaded research gets passed to the coding agent as context. DeerFlow also maintains sub-agent memory across tasks within a session, so later tasks can reference decisions made in earlier ones. It requires Python 3.12+ and couldn't run natively on our ARM64 test machine (Jetson runs Python 3.10). Its workflow was simulated following the documented architecture.

**Squad** ([github.com/bradygaster/squad](https://github.com/bradygaster/squad), v0.8.25) is a fundamentally different kind of tool. It's a team management layer for GitHub Copilot that creates persistent specialist roles — frontend developer, backend developer, tester, team lead — stored in `.squad/` directories within your project. Each role has custom instructions that Copilot reads when working on tasks assigned to that specialist. Squad is designed for ongoing GitHub Issues and PR workflows: you assign an issue to the "backend" specialist, and Copilot picks up that role's context and constraints.

This matters for interpreting the results. We installed Squad v0.8.25, ran `squad init` to generate the team structure, but discovered that `--agent squad` doesn't register as a Copilot agent in the way you'd expect. The Squad experiments in this benchmark were effectively single-agent Copilot sessions where Copilot had access to Squad's `.squad/` context files (role definitions, project conventions). No multi-agent orchestration occurred. Squad is built for persistent team coordination across many PRs over time, not single-prompt code generation from a spec. Comparing it head-to-head with Superpowers or DeerFlow as an "orchestrator" is somewhat apples-to-oranges.

### Spec Toolkits

**GSD (Get Shit Done)** ([github.com/gsd-build/get-shit-done](https://github.com/gsd-build/get-shit-done), 35K+ stars) takes a milestone/phase approach to project management for AI agents. Its philosophy is shipping fast with accountability. You run `new-project` to scaffold milestones from a spec, then `execute-phase` to have an agent work through each phase, then `verify-phase` to check the output. Each phase gets a fresh context window, which prevents context pollution across tasks. GSD enforces atomic git commits per phase, creating a clear audit trail. The fresh-context-per-phase pattern may explain why GSD variants consistently handled edge cases like terminal size checks — each phase is independently verified against the spec.

**Spec Kit** ([github.com/github/spec-kit](https://github.com/github/spec-kit), 72.7K stars) is GitHub's approach to spec-driven development. It generates structured requirement documents: feature scenarios (given/when/then), acceptance criteria, and architectural specifications. These documents are designed to be consumed by AI agents as context. Spec Kit emphasizes separation of concerns — the spec describes *what*, not *how* — and produces documents that read like detailed product requirements. In practice, this led agents to build more elaborate class hierarchies and typed interfaces, mirroring the structured nature of the specs themselves.

**OpenSpec** ([github.com/Fission-AI/openspec](https://github.com/Fission-AI/openspec)) is the most lightweight of the three. Its workflow is `plan → apply → archive`: generate a plan.md with task breakdowns, apply the plan to produce code, then archive the completed plan. Minimal ceremony, minimal scaffolding. The task breakdowns in plan.md files tend to be flat lists rather than hierarchical milestones, which gives agents more freedom in how they organize the code. This freedom showed in the results — OpenSpec variants had the most diverse architectures across the three orchestrators.

## Methodology

**What was controlled:**
- Identical spec ([SNAKE_SPEC.md](https://github.com/nimanch/multi-agent-benchmark/blob/main/SNAKE_SPEC.md)) — 16 acceptance criteria covering movement, collision, scoring, display, and restart
- Same language: Python 3.x with curses (stdlib only)
- Same machine: NVIDIA Jetson ARM64, 8GB RAM, Ubuntu
- Single-file implementations, zero manual interventions on any of the nine

**What was NOT controlled — and this matters:**

- **Superpowers** ran natively as a fully multi-agent system. Subagents were dispatched, parallel work occurred, two-stage review happened automatically. This is the only orchestrator that operated as designed.

- **DeerFlow 2.0** couldn't run natively. It requires Python 3.12+; the Jetson runs Python 3.10. Its Research → Plan → Code → Review pipeline was simulated by following the documented workflow manually. The results reflect DeerFlow's *methodology* applied by hand, not its runtime behavior.

- **Squad** was installed as the actual CLI (v0.8.25). We ran `squad init` to generate the `.squad/` team structure. But `--agent squad` doesn't register as a Copilot agent for single-prompt generation. The three Squad experiments used single-agent Copilot with Squad's `.squad/` project context files (role definitions, conventions) available in the working directory. No multi-agent orchestration occurred. This is an important distinction: Squad is designed for persistent team roles across GitHub Issues and PR workflows over time. The single-prompt generation task we tested is not its intended use case. The Squad results tell us something about how Copilot performs with structured project context, not about Squad's multi-agent capabilities.

Take the DeerFlow and Squad results with appropriate skepticism. The Superpowers results are the most representative of what a native multi-agent orchestration actually produces.

**Evaluation:** An LLM judge (not me) scored each implementation 1-5 on five dimensions: Spec Compliance, Correctness, Code Quality, Completeness, and Robustness. I reviewed the scores against the code and agreed with most of them, though the evaluation has its own limitations (discussed below).

## The Scores

| Implementation | Spec Compliance | Correctness | Code Quality | Completeness | Robustness | **Total** |
|---|---|---|---|---|---|---|
| deerflow-gsd | 5 | 4 | 4 | 5 | 4 | **22** |
| squad-gsd | 5 | 4 | 4 | 4 | 4 | **21** |
| squad-openspec | 5 | 4 | 4 | 4 | 4 | **21** |
| superpowers-gsd | 5 | 4 | 4 | 4 | 3 | **20** |
| superpowers-speckit | 4 | 3 | 5 | 4 | 3 | **19** |
| deerflow-speckit | 5 | 4 | 4 | 3 | 2 | **18** |
| superpowers-openspec | 4 | 4 | 4 | 3 | 2 | **17** |
| deerflow-openspec | 5 | 4 | 3 | 3 | 2 | **17** |
| squad-speckit | 4 | 3 | 4 | 4 | 2 | **17** |

GSD swept the top three positions. Every orchestrator paired with GSD outscored the same orchestrator paired with either alternative toolkit. deerflow-gsd led at 22/25; squad-gsd and squad-openspec tied for second at 21/25.

squad-openspec is the notable mover — it's the only non-GSD implementation to crack the top three, scoring 21/25 with an interactive terminal-size resize loop and smart self-collision handling that accounts for tail movement.

## Spec Compliance Matrix

Not all "pass" results are equal. The LLM judge checked 16 specific requirements:

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
| **Min terminal 20x10** | ✅ | ⚠️ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |

Two things jump out:

1. **Only 4 of 9 implementations checked minimum terminal size** — three GSD variants plus squad-openspec. This is a clear spec requirement that 5 implementations simply ignored.
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

One redeeming quality: deerflow-openspec is the only implementation that uses `collections.deque` for the snake body, giving O(1) head insertion vs O(n) for list `insert(0, ...)`. For a 20x10 terminal it doesn't matter, but it's the technically correct data structure.

## Lines of Code

| Implementation | LOC | Architecture |
|---|---|---|
| squad-gsd | 132 | Clean procedural |
| deerflow-speckit | 152 | State machine + enum |
| deerflow-openspec | 171 | Event-driven (dead EventBus) |
| superpowers-gsd | 178 | Procedural with constants |
| superpowers-openspec | 179 | Functional + dataclass |
| squad-speckit | 180 | Protocol pattern + Position class |
| deerflow-gsd | 181 | Module-style functions |
| squad-openspec | 203 | Dict-state, pure functions |
| superpowers-speckit | 213 | OOP (5 classes) |

squad-gsd's 132 lines scored 21/25 (tied second). superpowers-speckit's 213 lines scored 19/25 (fifth, with a bug). squad-openspec is the interesting outlier: at 203 lines it tied for second at 21/25, but those extra lines went to useful features (interactive terminal resize loop, smart collision handling, robust rendering) rather than architectural overhead. More code correlated with more architectural ambition, which correlated with more opportunities for bugs and dead code — except when the extra code was defensive rather than structural.

## What the Spec Toolkit Controls vs. What the Orchestrator Controls

The spec toolkit shaped *architecture*:
- **GSD** → procedural, pragmatic, "just make it work"
- **Spec Kit** → OOP, typed, separated concerns, more elaborate class hierarchies
- **OpenSpec** → functional, state-as-data, testable pure functions

The orchestrator shaped *completeness and robustness*:
- All three GSD variants checked terminal size. Of the non-GSD variants, only squad-openspec did.
- deerflow-gsd was the only implementation with a food-spawn safety net (1000 attempts with fallback position)
- Superpowers consistently produced more polished rendering (manual Unicode box-drawing borders)

The interaction between them is what mattered. GSD's milestone-based approach apparently forced all three orchestrators to handle edge cases (terminal size) that the other toolkits didn't prompt for. The spec explicitly says "Minimum terminal size: 20x10" — GSD treated this as a requirement; Spec Kit and OpenSpec (with the exception of squad-openspec) apparently didn't surface it as a first-class acceptance criterion.

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

**Only one orchestrator ran natively.** DeerFlow was simulated due to Python version requirements. Squad was installed but doesn't function as a multi-agent system for single-prompt generation — the experiments used single-agent Copilot with Squad's context files. Only Superpowers operated as a true multi-agent orchestration. This makes cross-orchestrator comparisons uneven. The DeerFlow and Squad results are more about their *methodology and context* than their *runtime behavior*.

**N=1 per combination.** I ran each combination once. LLM outputs are stochastic. Running each combination five times and averaging would be more rigorous. The scores could shift by a few points on re-runs.

**LLM-as-judge.** The evaluation was done by an LLM, not by running a test suite. The grow-timing bug was caught by code inspection, not automated testing. A proper evaluation would include functional tests that exercise each acceptance criterion programmatically.

**Scoring granularity.** 1-5 integer scores across five dimensions give a 5-25 range. The actual spread was 17-22, a 5-point range across 9 implementations. Whether deerflow-gsd at 22 is meaningfully better than squad-gsd at 21 is debatable. The top-4 vs bottom-5 distinction is clearer than individual rankings.

## Conclusions

Three data-driven takeaways:

1. **GSD's spec compliance advantage was decisive.** All three GSD variants scored 5/5 on spec compliance and checked terminal size. The toolkit's milestone-based approach — fresh context per phase, explicit verification steps — appears to enforce spec requirements more reliably than scenario-based (Spec Kit) or task-based (OpenSpec) approaches. deerflow-gsd (22/25) led the field; squad-gsd and superpowers-gsd scored 21 and 20 respectively. At least for this spec, GSD's "verify each phase" pattern caught requirements that other toolkits missed.

2. **Architectural ambition correlated negatively with correctness.** The two implementations with the most classes (superpowers-speckit: 5 classes, squad-speckit: Position + Protocol + entities) both had the grow-timing bug (Correctness: 3/5 each). The implementation with the most elaborate architecture (deerflow-openspec: EventBus) had dead code (Code Quality: 3/5). The top four scorers (22, 21, 21, 20) were all procedural or simple functional code. squad-openspec (21/25) is instructive: its 203 lines are longer than average, but the extra code is defensive (try/except, resize loop) rather than structural (classes, protocols).

3. **The spec toolkit shaped the code more than the orchestrator.** Across all three orchestrators, GSD produced procedural code, Spec Kit produced OOP code, and OpenSpec produced functional code. The orchestrator affected quality within those patterns but didn't change the patterns themselves. The one exception: squad-openspec broke the pattern of OpenSpec variants lacking robustness, scoring 4/5 on Robustness with an interactive terminal-size resize loop — the best terminal-size UX of all nine implementations.

Whether this generalizes beyond Snake — beyond a well-understood, small, single-file problem — is an open question.

---

*Nishant Manchanda builds things in Seattle.*

*All code and evaluation data: [github.com/nimanch/multi-agent-benchmark](https://github.com/nimanch/multi-agent-benchmark)*

## References

**Orchestrators:**
- [Superpowers](https://github.com/obra/superpowers) — Subagent-driven development framework with two-stage review (94K+ stars)
- [DeerFlow 2.0](https://github.com/bytedance/deer-flow) — ByteDance's Research → Plan → Code → Review pipeline
- [Squad](https://github.com/bradygaster/squad) — Team management layer for GitHub Copilot with persistent specialist roles (v0.8.25)

**Spec Toolkits:**
- [GSD (Get Shit Done)](https://github.com/gsd-build/get-shit-done) — Milestone/phase project management with fresh context windows (35K+ stars)
- [Spec Kit](https://github.com/github/spec-kit) — GitHub's spec-driven development with feature scenarios and acceptance criteria (72.7K stars)
- [OpenSpec](https://github.com/Fission-AI/openspec) — Lightweight plan → apply → archive workflow

**Evaluation:**
- [SNAKE_SPEC.md](https://github.com/nimanch/multi-agent-benchmark/blob/main/SNAKE_SPEC.md) — Shared spec used across all 9 experiments
- [EVALUATION.md](https://github.com/nimanch/multi-agent-benchmark/blob/main/EVALUATION.md) — Full LLM-as-Judge scoring with per-implementation analysis
- [RESULTS.md](https://github.com/nimanch/multi-agent-benchmark/blob/main/RESULTS.md) — Raw benchmark results
