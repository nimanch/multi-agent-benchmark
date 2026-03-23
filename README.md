# Multi-Agent Snake Game Benchmark

A systematic comparison of 9 combinations of multi-agent orchestrators × spec-driven toolkits, all building the same Python CLI Snake game from a shared specification.

**Article**: [Evaluating 9 AI Agent Combinations on the Same Snake Game](ARTICLE.md)

## The 3×3 Matrix

|  | [GSD](#gsd-get-shit-done) | [Spec Kit](#spec-kit) | [OpenSpec](#openspec) |
|--|-----|----------|---------|
| **[Superpowers](#superpowers)** | Procedural (178 LOC) | OOP 5-class (213 LOC) 🏆 | Functional+dataclass (179 LOC) |
| **[DeerFlow](#deerflow-20)** | Module functions (181 LOC) | State machine (152 LOC) | Event-driven (171 LOC) |
| **[Squad](#squad)** | Clean minimal (132 LOC) | Protocol pattern (180 LOC) | Dict-state pure (157 LOC) |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/nimanch/multi-agent-benchmark.git
cd multi-agent-benchmark

# Run any of the 9 snake games (no dependencies beyond Python 3.x):
python3 superpowers-gsd/snake.py
python3 deerflow-speckit/snake.py
python3 squad-openspec/snake.py
# ... etc.
```

**Requirements**: Python 3.x with `curses` (standard library). Terminal at least 20×10 chars.

**Controls**: Arrow keys to move, `r` to restart, `q` to quit.

---

## Reproducing the Experiment

This section explains how to set up each tool from scratch and run the experiments yourself. The experiment was conducted on an NVIDIA Jetson (ARM64, 8GB RAM, Ubuntu, Python 3.10) but should work on any Linux/macOS machine.

### Prerequisites

- **Python 3.10+** (3.12+ required for DeerFlow native runs)
- **Node.js 22+** (for Copilot CLI / Squad)
- **GitHub CLI** (`gh`) — for GitHub Models API access and Copilot
- **Git**

### The Shared Spec

All 9 experiments start from the same specification: [`SNAKE_SPEC.md`](SNAKE_SPEC.md). Each experiment directory gets a copy as `SPEC.md`. This is the "contract" every agent combination must fulfill.

---

## Tool Setup

### Orchestrators

#### Superpowers

[Superpowers](https://github.com/obra/superpowers) (obra, 94K+ stars) is a subagent-driven development framework with planning, implementation, and two-stage review (spec compliance + code quality).

**Install:**

```bash
# Superpowers is a set of agent skills — clone to your agent skills directory
mkdir -p ~/.agents/skills
git clone https://github.com/obra/superpowers.git ~/.agents/skills/superpowers
```

**How it works:** Superpowers provides skill definitions in `.superpowers/skills/` that guide AI agents through structured workflows: `writing-plans`, `executing-plans`, `subagent-driven-development`, and `verification-before-completion`. Your AI coding agent (e.g., Claude Code, Copilot) reads these skills and follows the multi-stage process.

**Project setup for an experiment:**

```bash
mkdir superpowers-gsd && cd superpowers-gsd

# Link Superpowers skills
mkdir -p .superpowers/skills
# Copy or symlink the relevant skills:
cp -r ~/.agents/skills/superpowers/skills/* .superpowers/skills/

# Copy the shared spec
cp ../SNAKE_SPEC.md SPEC.md
```

Then run your AI agent in the directory — it picks up the `.superpowers/` context automatically.

#### DeerFlow 2.0

[DeerFlow 2.0](https://github.com/bytedance/deer-flow) (ByteDance) follows a Research → Plan → Code → Review pipeline with sub-agent memory.

**Install:**

```bash
# DeerFlow requires Python 3.12+
# If your system Python is older, use pyenv:
pyenv install 3.12.9
pyenv local 3.12.9

# Clone and install
git clone https://github.com/bytedance/deer-flow.git ~/deerflow
cd ~/deerflow/backend
uv sync  # or: pip install -e .
```

**Configuration** — create `.deerflow/config.yaml` in each experiment directory:

```yaml
config_version: 3

models:
  - name: gpt-4o
    display_name: GPT-4o (GitHub Models)
    use: langchain_openai:ChatOpenAI
    model: gpt-4o
    api_key: <your-github-token>  # from: gh auth token
    base_url: https://models.inference.ai.azure.com
    max_tokens: 4096
    temperature: 0.7

tool_groups:
  - name: web
  - name: file:read
  - name: file:write
  - name: bash

tools:
  - name: write_file
    group: file:write
    use: deerflow.sandbox.tools:write_file_tool
  - name: read_file
    group: file:read
    use: deerflow.sandbox.tools:read_file_tool

sandbox:
  use: deerflow.sandbox.local:LocalSandboxProvider
```

**Run natively:**

```python
from deerflow import DeerFlowClient

client = DeerFlowClient()
result = client.chat("""
Read SPEC.md and implement the Snake game as snake.py.
Follow the GSD methodology: define milestones, execute phases, ship.
""")
```

**Gotchas:**
- `sandbox: mode: local` fails Pydantic validation — use `sandbox: use: deerflow.sandbox.local:LocalSandboxProvider`
- DeerFlow requires Python ≥3.12 (won't work with system Python 3.10)
- GitHub Models API works well as the LLM backend (`gh auth token` for the API key)

#### Squad

[Squad](https://github.com/bradygaster/squad) (v0.8.25) is a team management layer for GitHub Copilot that creates persistent specialist roles.

**Install:**

```bash
# Install Squad CLI
npm install -g @anthropic/squad  # or the appropriate package
# Verify
squad --version

# Install GitHub Copilot CLI (required)
gh extension install github/gh-copilot
```

**Initialize a project:**

```bash
mkdir squad-gsd && cd squad-gsd
squad init
# This creates .squad/ with:
#   config.json, team.md, routing.md, agents/, ceremonies.md, etc.

# Copy the shared spec
cp ../SNAKE_SPEC.md SPEC.md
```

**Run:**

```bash
# Squad doesn't register as --agent for Copilot.
# Instead, Copilot reads .squad/ context when invoked in the directory:
copilot --allow-all --no-ask-user -s \
  -p "Read SPEC.md and implement snake.py following GSD methodology" \
  --model gpt-5.2
```

**Important note:** `--agent squad` does **not** work — Squad is a team coordination layer for GitHub Issues/PR workflows, not a single-prompt agent. In this benchmark, Squad provided project context (`.squad/` files) that Copilot read, but no true multi-agent orchestration occurred. See [SQUAD_RERUN.md](SQUAD_RERUN.md) for details.

---

### Spec Toolkits

Each toolkit shapes *how* the agent approaches the problem. They're combined with orchestrators (one toolkit per experiment directory).

#### GSD (Get Shit Done)

[GSD](https://github.com/gsd-build/get-shit-done) (v1.28.0) is a milestone-based project lifecycle manager. Focus: ship pragmatic code fast.

**Install:**

```bash
# GSD installs as a Copilot agent skill
mkdir -p ~/.copilot/get-shit-done
git clone https://github.com/gsd-build/get-shit-done.git ~/.copilot/get-shit-done
```

**Project setup:**

```bash
# In each experiment directory, link GSD:
mkdir -p .copilot
cp -r ~/.copilot/get-shit-done .copilot/get-shit-done

# Optionally add MCP config:
cat > .copilot/mcp-config.json << 'EOF'
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@anthropic/github-mcp-server"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    }
  }
}
EOF
```

**Effect on code:** Pragmatic, minimal, "just works" style. Fewest lines. Milestone/phase workflows encourage shipping over architecture.

#### Spec Kit

[Spec Kit](https://github.com/github/spec-kit) is a structured feature specification toolkit with scenarios and acceptance criteria.

**Install:**

```bash
git clone https://github.com/github/spec-kit.git ~/spec-kit
```

**Project setup:**

```bash
# Create a spec-kit/ directory in the experiment folder with a feature spec:
mkdir -p spec-kit
cat > spec-kit/snake-game.md << 'EOF'
# Feature: Terminal Snake Game

## Summary
A terminal-based Snake game in Python using curses.

## Requirements
- Snake moves continuously, arrow keys change direction
- Cannot reverse direction
- Food spawns randomly as `*`, snake body `█`, head `O`
- Score +10 per food, displayed at top
- Wall and self collision = game over
- Game over screen with final score, 'q' quit, 'r' restart
- 100ms tick, min terminal 20x10
- Single file: snake.py

## Acceptance Criteria
See SPEC.md for full criteria list.
EOF
```

**Effect on code:** Most structured output — OOP patterns, type hints, clear separation of concerns. Encourages scenarios-based thinking.

#### OpenSpec

[OpenSpec](https://github.com/Fission-AI/openspec) is a lightweight spec-driven framework with `plan → apply → archive` workflow.

**Install:**

```bash
git clone https://github.com/Fission-AI/openspec.git ~/openspec
```

**Project setup:**

```bash
# Create an openspec/ directory with a plan:
mkdir -p openspec
cat > openspec/plan.md << 'EOF'
# Plan: Terminal Snake Game

## Goal
Build a terminal Snake game in Python curses as a single file (snake.py).

## Tasks
1. Set up curses window with border
2. Initialize snake (position, direction, body list)
3. Implement game loop with 100ms tick
4. Handle arrow key input, prevent reverse
5. Move snake, check wall/self collision
6. Spawn food randomly, detect eating
7. Track and display score
8. Implement game over screen with restart

## Constraints
- Python 3, curses only, no external deps
- See SPEC.md for full specification
EOF
```

**Effect on code:** Clean functional patterns. State-as-data approach. Task-oriented decomposition.

---

## Running an Experiment

Here's the general flow for each of the 9 combinations:

### 1. Create the experiment directory

```bash
mkdir <orchestrator>-<toolkit>
cd <orchestrator>-<toolkit>

# Copy the shared spec
cp ../SNAKE_SPEC.md SPEC.md
```

### 2. Set up orchestrator context

- **Superpowers**: Copy `.superpowers/skills/` into the directory
- **DeerFlow**: Create `.deerflow/config.yaml` (see above)
- **Squad**: Run `squad init` to generate `.squad/`

### 3. Set up toolkit context

- **GSD**: Copy `.copilot/get-shit-done/` into the directory
- **Spec Kit**: Create `spec-kit/snake-game.md` with the feature spec
- **OpenSpec**: Create `openspec/plan.md` with the task plan

### 4. Run the agent

For **Superpowers** experiments, use any agent that reads `.superpowers/` skills (e.g., Claude Code):
```bash
# The agent reads .superpowers/ and SPEC.md, then follows the
# subagent-driven-development workflow automatically
```

For **DeerFlow** experiments:
```python
from deerflow import DeerFlowClient
client = DeerFlowClient()
result = client.chat("Read SPEC.md and implement snake.py. Use <toolkit> methodology.")
```

For **Squad** experiments:
```bash
copilot --allow-all --no-ask-user -s \
  -p "Read SPEC.md and implement snake.py following <toolkit> methodology" \
  --model gpt-5.2
```

### 5. Verify the output

```bash
# Check it compiles
python3 -m py_compile snake.py

# Play it
python3 snake.py
```

---

## Simulation Transparency

These frameworks are **AI agent orchestration prompts/workflows**, not automated CLI pipelines. Each experiment was conducted by:

1. Following the framework's documented methodology
2. Using its architectural patterns to guide code structure
3. Applying its review/verification processes

Some frameworks couldn't run natively on the test hardware:
- **DeerFlow**: Initially simulated (Python 3.12 unavailable), later re-run natively via pyenv. Both versions preserved (`snake.py` = native, `snake.py.simulated` = simulated). See [DEERFLOW_NATIVE.md](DEERFLOW_NATIVE.md).
- **Squad**: `--agent squad` doesn't register with Copilot. Effectively single-agent Copilot with Squad's `.squad/` context. See [SQUAD_RERUN.md](SQUAD_RERUN.md).
- **Superpowers**: Ran natively — the only orchestrator that fully worked as documented.

---

## Results

See [EVALUATION.md](EVALUATION.md) for detailed per-implementation scoring (5 dimensions, 25 points max).

### Final Ranking

| Rank | Implementation | Score | Key Strength |
|---|---|---|---|
| 🥇 | deerflow-gsd | 22/25 | Food-spawn safety net, graceful terminal check, no bugs |
| 🥈 | squad-gsd | 21/25 | Cleanest, most readable code, zero over-engineering |
| 🥈 | squad-openspec | 21/25 | Most testable design, interactive terminal resize loop |
| 4 | superpowers-gsd | 20/25 | Solid all-around, Unicode borders |
| 5 | superpowers-speckit | 19/25 | Best OOP architecture, but has grow-timing bug |
| 6 | deerflow-speckit | 18/25 | Good state machine pattern |
| 7 | superpowers-openspec | 17/25 | Decent functional approach |
| 7 | deerflow-openspec | 17/25 | EventBus with zero subscribers |
| 7 | squad-speckit | 17/25 | Over-typed, unused Protocol |

### Key Findings

1. **GSD swept the top 3** — pragmatic "just ship it" beats architectural ambition for this task size
2. **Spec Kit produces the most structured code** but introduced bugs (grow-timing delay in 2 of 3 implementations)
3. **The toolkit shaped code more than the orchestrator** — same toolkit produced similar patterns regardless of orchestrator
4. **Over-engineering correlates with lower scores** — EventBus with no subscribers, Protocol with no dispatch
5. **Native DeerFlow produced simpler code than simulated** — the `DeerFlowClient.chat()` API doesn't fully exercise the documented multi-agent pipeline

---

## Repository Structure

```
multi-agent-benchmark/
├── README.md               # This file
├── SNAKE_SPEC.md           # Common spec all 9 games implement
├── RESULTS.md              # Comparison & analysis
├── EVALUATION.md           # Detailed scoring (5 dimensions × 9 implementations)
├── ARTICLE.md              # Medium article
├── DEERFLOW_NATIVE.md      # DeerFlow native vs simulated analysis
├── SQUAD_RERUN.md          # Squad re-run findings
├── article.html            # Rendered article
├── screenshots/            # Game screenshots
├── gifs/                   # Gameplay GIFs
├── superpowers-gsd/        # Superpowers + GSD
│   ├── .superpowers/       #   Superpowers skills
│   ├── .copilot/           #   GSD workflow + MCP config
│   ├── SPEC.md             #   Snake spec (copy)
│   └── snake.py            #   Output: 178 LOC procedural
├── superpowers-speckit/    # Superpowers + Spec Kit
│   ├── .superpowers/
│   ├── spec-kit/           #   Feature spec
│   └── snake.py            #   Output: 213 LOC OOP (5 classes)
├── superpowers-openspec/   # Superpowers + OpenSpec
│   ├── .superpowers/
│   ├── openspec/           #   Task plan
│   └── snake.py            #   Output: 179 LOC functional+dataclass
├── deerflow-gsd/           # DeerFlow + GSD
│   ├── .deerflow/          #   DeerFlow config
│   ├── .copilot/           #   GSD workflow
│   ├── snake.py            #   Output: native (91 LOC)
│   └── snake.py.simulated  #   Simulated version (181 LOC)
├── deerflow-speckit/       # DeerFlow + Spec Kit
│   ├── .deerflow/
│   ├── spec-kit/
│   ├── snake.py            #   Output: native (110 LOC)
│   └── snake.py.simulated  #   Simulated version (152 LOC)
├── deerflow-openspec/      # DeerFlow + OpenSpec
│   ├── .deerflow/
│   ├── openspec/
│   ├── snake.py            #   Output: native (131 LOC)
│   └── snake.py.simulated  #   Simulated version (171 LOC)
├── squad-gsd/              # Squad + GSD
│   ├── .squad/             #   Squad team definitions
│   ├── .copilot/           #   GSD workflow
│   └── snake.py            #   Output: 132 LOC clean procedural
├── squad-speckit/          # Squad + Spec Kit
│   ├── .squad/
│   ├── spec-kit/
│   └── snake.py            #   Output: 180 LOC Protocol pattern
└── squad-openspec/         # Squad + OpenSpec
    ├── .squad/
    ├── openspec/
    └── snake.py            #   Output: 157 LOC dict-state pure functions
```

## Platform

Tested on NVIDIA Jetson (ARM64, 8GB RAM, Ubuntu, Python 3.10/3.12).

## Author

[Nishant Manchanda](https://github.com/nimanch) — March 2026
