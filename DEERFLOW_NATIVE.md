# DeerFlow Native Run Attempt

**Date:** 2026-03-22
**Machine:** ARM64 NVIDIA Jetson, Ubuntu, Python 3.10.12

## What Was Done

### Python 3.12 Installation ✅
- Installed pyenv: `curl -s https://pyenv.run | bash`
- Built Python 3.12.9 via pyenv: `pyenv install 3.12.9`
- Location: `~/.pyenv/versions/3.12.9/bin/python3.12`
- Warnings: Missing bzip2, curses, readline, sqlite3 extensions (non-critical for DeerFlow)
- **Time:** ~4 minutes (ARM64 compile)

### DeerFlow Clone ✅
- Cloned: `git clone https://github.com/bytedance/deer-flow.git ~/deerflow`
- Version: DeerFlow 2.0 (ground-up rewrite, shares no code with v1)
- Architecture: Super agent harness with sub-agents, memory, sandboxes, skills
- Has embedded Python client (`DeerFlowClient`) for programmatic use without HTTP server

### DeerFlow Setup ❌ — Blocked on API Keys
DeerFlow requires an LLM API key to run. It supports:
- OpenAI (GPT-4, GPT-5)
- DeepSeek
- Volcengine/Doubao
- OpenRouter (any model via OpenAI-compatible API)
- Google Gemini

**No LLM API keys were available in the environment.** Only available keys:
- `MATON_API_KEY` (API gateway, not an LLM)
- `BRAVE_API_KEY` (web search)
- `AZURE_TRANSCRIBE_KEY` (speech-to-text only, not a general LLM endpoint)

### What Would Be Needed
1. Set `OPENAI_API_KEY` or equivalent in the environment
2. Create `config.yaml` from `config.example.yaml` with model configuration
3. Run `make install` (requires uv, Node.js 22+, pnpm, nginx — or use embedded client)
4. Use `DeerFlowClient` for programmatic access:
   ```python
   from deerflow.client import DeerFlowClient
   client = DeerFlowClient()
   response = client.chat("Build a snake game following this spec: ...")
   ```

## Conclusion

**DeerFlow could not run natively** — not due to Python version (3.12 was successfully installed) but due to missing LLM API keys. The original article's characterization of the DeerFlow limitation as "Python 3.12+ requirement on ARM64" was partially correct but incomplete: even with Python 3.12 available, DeerFlow needs an LLM API key to orchestrate its sub-agents.

The existing simulated DeerFlow results remain unchanged. To run DeerFlow natively in the future:
1. Add an `OPENAI_API_KEY` or `OPENROUTER_API_KEY` to the environment
2. Configure `~/deerflow/config.yaml`
3. Re-run the 3 experiments with appropriate prompts
