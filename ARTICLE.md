# I Built the Same Snake Game 9 Times with Different AI Agent Combos. Here's What Actually Won.

*By Nishant Manchanda | March 2026*

---

It's March 2026, and every week brings a new AI coding agent that promises to "10x your development." Superpowers from obra. DeerFlow 2.0 from ByteDance (fresh off claiming #1 on GitHub Trending). GitHub's Squad multi-agent orchestration. Spec Kit. GSD. OpenSpec.

Everyone's benchmarking these tools on toy problems and declaring winners based on vibes.

I wanted data.

So I built the same game — a terminal Snake game in Python — using every combination of three multi-agent orchestrators and three spec-driven toolkits. That's a 3×3 matrix. Nine experiments. Same spec, same language, same machine. Here's what I found.

## The Setup

**The Orchestrators** (how the AI agents coordinate):
- **Superpowers** (obra) — Subagent-driven development with two-stage review
- **DeerFlow 2.0** (ByteDance) — Research → Plan → Code → Review pipeline with sub-agent memory
- **Squad** (GitHub Copilot) — Coordinator → Plan → Implement → Review → Test specialist pipeline

**The Spec Toolkits** (how requirements are structured):
- **GSD** (Get Shit Done) — Milestone/phase project management. Ship fast.
- **Spec Kit** (GitHub) — Feature scenarios, acceptance criteria, architectural specs
- **OpenSpec** (Fission-AI) — Lightweight `plan → apply → archive` workflow

**The Game**: A full-featured terminal Snake — arrow key controls, food spawning, score tracking, wall and self collision, game over screen, restart. All in Python curses.

**The Machine**: An NVIDIA Jetson (ARM64, 8GB RAM) — because if your tools can't work on constrained hardware, they're not as universal as they claim.

## The Results at a Glance

```
╔═══════════════╦═══════╦══════════╦═════════╗
║               ║  GSD  ║ Spec Kit ║ OpenSpec║
╠═══════════════╬═══════╬══════════╬═════════╣
║ Superpowers   ║ 178 L ║ 213 L 🏆 ║  179 L  ║
║ DeerFlow      ║ 181 L ║ 152 L    ║  171 L  ║
║ Squad         ║ 132 L ║ 180 L    ║  157 L  ║
╚═══════════════╩═══════╩══════════╩═════════╝
                        (L = lines of code)
```

All nine produced working, playable games with zero manual interventions. Let that sink in. Every combination cleared the spec.

The interesting part isn't *whether* they worked — it's *how* they worked.

## What Each Combination Produced

### 🏆 Winner: Superpowers + Spec Kit (213 LOC)

Five clean classes: `GameConfig`, `Direction`, `Snake`, `Food`, `Renderer`, and `Game`. Single responsibility everywhere. The kind of code you'd accept in a PR without notes.

```python
class Snake:
    def __init__(self, start_y, start_x):
        self.body = [(start_y, start_x), (start_y, start_x - 1), (start_y, start_x - 2)]
        self.direction = Direction.RIGHT
        self.grow_pending = False

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
```

**Why it won**: Superpowers' two-stage review (spec compliance first, then code quality) combined with Spec Kit's structured acceptance criteria created a natural pressure toward clean architecture. The spec toolkit demanded scenarios; the orchestrator demanded quality. The result is code that reads like it was written by a senior dev who actually cares.

### Best for Speed: Squad + GSD (132 LOC)

The shortest, leanest implementation. No classes, no abstractions — just functions that do exactly what the spec says.

```python
def play(stdscr):
    h, w = stdscr.getmaxyx()
    snake = [(cy, cx), (cy, cx - 1), (cy, cx - 2)]
    direction = (0, 1)
    # ... 130 lines of clean, working game
```

**The vibe**: GSD's "ship it" philosophy met Squad's pragmatic pipeline and produced the fastest path from spec to working game. If you need something yesterday, this is your combo.

### Most Testable: Squad + OpenSpec (157 LOC)

Dict-based state with pure functions. Every game operation is a function that takes state in and returns state out.

```python
def step(state):
    """Advance game one tick. Returns updated state."""
    dy, dx = DIRECTIONS[state['dir']]
    hy, hx = state['snake'][0]
    nh = (hy + dy, hx + dx)
    # Pure logic, trivially testable
```

**Why it matters**: You could drop `pytest` tests on this without mocking a single thing. The state is just a dict. The functions are pure. This is what TDD dreams are made of.

### Most Creative: DeerFlow + OpenSpec (171 LOC)

The only implementation with an event bus pattern:

```python
class EventBus:
    def on(self, event, handler):
        self._handlers.setdefault(event, []).append(handler)
    def emit(self, event, **kwargs):
        for h in self._handlers.get(event, []):
            h(**kwargs)
```

DeerFlow's research-first approach (its research sub-agent examines best practices before the coding agent starts) led to an architecture you'd use for a real game engine, not a toy project. Over-engineered for Snake? Sure. But it shows the framework *thinking* about extensibility.

### The Box-Drawing Prize: DeerFlow + GSD

This one gave us a proper box-drawing game over screen:

```python
texts = [
    ("╔══════════════════╗", -2),
    ("║    GAME  OVER    ║", -1),
    ("║  Score:     42   ║", 0),
    ("║  r=Retry  q=Quit ║", 1),
    ("╚══════════════════╝", 2),
]
```

Small detail, but it's the kind of polish that makes a user smile.

## The Patterns I Noticed

### 1. Spec Toolkits Shape Architecture More Than Orchestrators

This was the biggest surprise. The orchestrator (Superpowers vs DeerFlow vs Squad) affected code *quality*, but the spec toolkit affected code *structure*:

- **GSD** → procedural, minimal, ship-focused
- **Spec Kit** → OOP, typed, well-separated concerns
- **OpenSpec** → functional, state-as-data, testable

The orchestrator is the quality dial. The spec toolkit is the architecture dial.

### 2. Two-Stage Review Is Genuinely Better

Superpowers' approach of reviewing spec compliance *separately* from code quality caught things that single-pass review missed. It's like having a PM and a tech lead review independently — different eyes catch different problems.

### 3. Research Agents Add Polish at Scale

DeerFlow's research-first pattern seems overkill for a snake game. But extrapolate to a real project — having an agent that examines existing patterns, library docs, and best practices *before* writing code could prevent entire categories of mistakes.

### 4. "Just Ship It" Has Its Place

Squad + GSD produced the fewest lines and a perfectly working game. Sometimes you don't need five classes and an event bus. You need 132 lines and a working product.

## The Honest Caveats

Let me be transparent about what this experiment actually tested:

1. **These frameworks are AI agent guidance systems**, not automated compilers. They provide prompts, workflows, and structure for AI agents to follow. The "nine experiments" followed each framework's documented methodology.

2. **DeerFlow couldn't run natively on ARM64/Jetson** (needs Python 3.12+). Its workflow was simulated based on its well-documented architecture.

3. **Squad requires Copilot Pro+ for cloud multi-agent**. The pipeline was simulated locally following its documented Coordinator → specialists pattern.

4. **Zero interventions across all 9** partly reflects that Snake is a well-understood problem. A more complex project would likely reveal bigger differences.

## My Recommendations

**For solo developers who want quality**: Superpowers + Spec Kit. The two-stage review and structured specs create a virtuous cycle.

**For teams that need speed**: Squad + GSD. Minimal ceremony, maximum shipping.

**For projects that need testability**: Squad + OpenSpec. Pure functions from day one.

**For complex research-heavy projects**: DeerFlow + any spec toolkit. The research agent pattern pays dividends on unfamiliar problems.

## What's Next

The real test would be building something complex — a full-stack app, a distributed system — with each combination and measuring over weeks, not minutes. That's the experiment I'd love to see.

For now, if you're choosing your AI agent stack in 2026, here's the bottom line: **the spec toolkit matters more than you think, and two-stage review is worth the overhead.**

The code from all nine experiments is open source. Go play some Snake.

---

*Nishant Manchanda builds things in Seattle. He's interested in AI agents, graph-based memory, and cats (two tabbies).*

*All code: [github.com/nishantmanchanda/multi-agent-benchmark](https://github.com/nishantmanchanda/multi-agent-benchmark)*
