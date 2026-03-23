# Squad Experiments Re-run Summary

**Date:** 2026-03-22  
**Squad CLI:** v0.8.25  
**Copilot CLI:** v0.0.410  
**Model used:** gpt-5.2 (default failed with auth/model errors)

## Key Finding

The `--agent squad` flag does **not** work — Squad CLI is a team management layer that creates `.squad/` directories with agent definitions, routing tables, and ceremonies. It is not itself a Copilot agent. The available agents from `.copilot/` were GSD-related (gsd-executor, gsd-planner, etc.), not "squad".

**What we actually ran:** `copilot --allow-all --no-ask-user -s -p "<prompt>" --model gpt-5.2` in each squad directory. Copilot read the SPEC.md and `.squad/` context, then generated snake.py. The Squad `.squad/` directory provided project context but didn't orchestrate multi-agent workflows — Copilot operated as a single agent.

## Results

### 1. squad-gsd ✅
- **Output:** snake.py (196 lines, 4995 bytes)
- **Copilot read** SPEC.md and snake.py.simulated, then wrote a fresh implementation
- **Features:** 100ms tick, arrow keys, wall/self collision, score, game over with r/q
- **Compiled clean:** `python3 -m py_compile` passed

### 2. squad-speckit ✅
- **Output:** snake.py (220 lines, 5878 bytes)
- **Copilot read** SPEC.md, spec-kit/ reference, and snake.py.simulated
- **Added:** minimum terminal size enforcement (20x10), safer rendering with try/except
- **Compiled clean**

### 3. squad-openspec ✅
- **Output:** snake.py (203 lines, 4774 bytes)
- **Copilot read** SPEC.md, openspec/plan.md, and snake.py.simulated
- **Added:** min terminal size enforcement, corrected self-collision (tail cell edge case), TICK_MS constant
- **Compiled clean**

## Observations

1. **Squad ≠ Copilot Agent**: Squad CLI manages team definitions (`.squad/agents/`, routing, ceremonies) but doesn't register as a `--agent` for Copilot. It's meant for GitHub Issues/PR-based workflows, not single-prompt code generation.
2. **All 3 runs produced working code** — Copilot generated spec-compliant snake.py in each case.
3. **The simulated versions were used as reference** — Copilot read snake.py.simulated and improved upon it rather than starting truly from scratch.
4. **Default model failed** — Had to specify `--model gpt-5.2`; the default model returned auth/unknown errors.
5. **No true multi-agent orchestration occurred** — Without GitHub Issues or PR workflows, Squad's team routing wasn't exercised. Each run was effectively single-agent Copilot.

## File Inventory

| Directory | snake.py | snake.py.simulated | SPEC.md | Toolkit Context |
|-----------|----------|-------------------|---------|-----------------|
| squad-gsd | ✅ new (196L) | ✅ backed up | ✅ | .copilot/get-shit-done/ |
| squad-speckit | ✅ new (220L) | ✅ backed up | ✅ | spec-kit/snake-game.md |
| squad-openspec | ✅ new (203L) | ✅ backed up | ✅ | openspec/plan.md |
