# DeerFlow Native Run — March 22, 2026

## Summary

DeerFlow 2.0 was run natively on the Jetson ARM64 machine using the embedded Python client (`DeerFlowClient`) with GitHub Models API as the LLM backend. All three experiments completed successfully, producing working Snake game implementations.

## Setup

- **DeerFlow**: Cloned at `/home/nimanch/deerflow`, installed via `uv sync` in `backend/` workspace
- **Python**: 3.12.9 via pyenv (DeerFlow requires ≥3.12)
- **Model**: `gpt-4o` via `langchain_openai:ChatOpenAI`
- **API Endpoint**: `https://models.inference.ai.azure.com` (GitHub Models API)
- **API Key**: GitHub OAuth token (`gh auth token`)
- **Sandbox**: Local mode (`deerflow.sandbox.local:LocalSandboxProvider`)
- **Config**: Custom `config.yaml` with minimal tool set (write_file, read_file only — web search disabled)

## Method

Each experiment used `DeerFlowClient.chat()` with a single prompt containing:
1. The full SNAKE_SPEC.md content
2. Methodology-specific instructions (GSD milestones / Spec Kit scenarios / OpenSpec plan-apply-archive)
3. Instructions to output only Python code

DeerFlow orchestrated internally — sub-agent memory was enabled, tools were available. Each call took ~10-15 seconds.

## Results

| Variant | LOC | Compiles | Terminal Check | Architecture | Score |
|---|---|---|---|---|---|
| deerflow-gsd | 91 | ✅ | ✅ | Bare procedural | 18/25 |
| deerflow-speckit | 110 | ✅ | ✅ | Procedural | 18/25 |
| deerflow-openspec | 131 | ✅ | ❌ | OOP (SnakeGame class) | 17/25 |

All three compile and run correctly. Simulated versions preserved as `snake.py.simulated`.

## Key Finding: Native vs Simulated

| Variant | Simulated LOC | Native LOC | Simulated Score | Native Score |
|---|---|---|---|---|
| GSD | 181 | 91 | 22 | 18 |
| Spec Kit | 152 | 110 | 18 | 18 |
| OpenSpec | 171 | 131 | 17 | 17 |

The native runtime produced simpler, shorter code. The simulated deerflow-gsd (which followed the documented Research → Plan → Code → Review pipeline step by step) scored 22/25 — the former overall leader. The native version scored 18/25.

This suggests `DeerFlowClient.chat()` doesn't fully exercise the multi-agent pipeline that the documentation describes. The `chat()` method appears to route through the lead agent but may not invoke the full research → plan → code → review chain for straightforward code generation tasks.

## Issues Encountered

1. **Config validation**: Initial `sandbox: mode: local` failed Pydantic validation; needed `sandbox: use: deerflow.sandbox.local:LocalSandboxProvider`
2. **No install issues**: ARM64 + Python 3.12 via pyenv worked fine with `uv sync`
3. **Rate limits**: GitHub Models API handled all 3 requests without throttling
4. **Memory timer**: DeerFlow logged "Memory update timer set for 30s" and "Memory update queued" — sub-agent memory was active

## Files Changed

- `deerflow-gsd/snake.py` — native DeerFlow output (91 LOC)
- `deerflow-gsd/snake.py.simulated` — previous simulated version (181 LOC)
- `deerflow-speckit/snake.py` — native DeerFlow output (110 LOC)
- `deerflow-speckit/snake.py.simulated` — previous simulated version (152 LOC)
- `deerflow-openspec/snake.py` — native DeerFlow output (131 LOC)
- `deerflow-openspec/snake.py.simulated` — previous simulated version (171 LOC)
- `EVALUATION.md` — updated with native scores and analysis
- `ARTICLE.md` — updated methodology, scores, analysis for v5
- `article.html` — regenerated HTML
