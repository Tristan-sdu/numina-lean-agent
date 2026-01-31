# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

## Project Overview

**Numina-Lean-Agent** is a Claude Code–based agentic system for formal theorem proving in Lean 4. Key capabilities:
- Automated theorem proving using Claude for Lean 4 math proofs
- Multiple run modes: single file, batch, and folder scan
- Prompt templates for different difficulty levels
- Multi-agent architecture: coordinator, blueprint agent, sketch agent, and proof agent
- Toolchain integration via MCP (Model Context Protocol) with Lean LSP

**Highlights:**
- Proved all 12 problems of Putnam 2025
- Completed a paper-level formalization of “Effective Brascamp-Lieb inequalities”
- Strong performance on the MiniF2F benchmark

## System Architecture

### Core Workflow
1. Initialize: load task config and prompt templates
2. Session loop: run Claude rounds and check proof progress
3. Verification: use `lean_diagnostic_messages` to validate files
4. Commits: optionally create git commits per round
5. Results: save JSON outputs and MCP logs

### Directory Layout
```
scripts/                    # Core Python scripts
  run_claude.py             # CLI entry (run/batch/from-folder)
  runner.py                 # Session management and execution
  task.py                   # Task metadata and result types
  lean_checker.py           # Lean file verification helpers
  statement_tracker.py      # Track statement changes across rounds
  mcp_stats.py              # MCP log analysis
  extract_sublemmas.py      # Sublemma extraction

leanproblems/               # Lean 4 project with problems
  Minif2f/                  # MiniF2F benchmark instances
  Putnam2025/               # Putnam 2025 (12 problems)
  Leanproblems/             # Project modules
  lakefile.toml             # Lake build config (mathlib v4.26.0)
  lean-toolchain            # Lean version (v4.26.0)
  lake-manifest.json        # Dependency manifest

prompts/                    # Prompt templates
  prompt_complete_file.txt  # Standard completion mode
  prompt_hard_mode.txt      # Hard mode with hints
  prompt_medium_mode.txt    # Medium mode
  docs/                     # Subagent documentation
    prompts/                # Agent instructions
      common.md             # Shared rules
      coordinator.md        # Coordinator
      blueprint_agent.md    # Blueprint agent
      sketch_agent.md       # Sketch agent
      proof_agent.md        # Proof agent
    technique/              # System design docs

config/                     # Batch configs
  config_minif2f.yaml       # MiniF2F evaluation config


  setup.md                  # Environment setup
  usage.md                  # Usage guide
  setup.sh                  # Automated setup script
  myproject/                # Example project
```

## Common Commands

### Build the Lean project
```bash
cd leanproblems
lake update
lake exe cache get
lake build
```

### Run modes
```bash
# Single file
python -m scripts.run_claude run leanproblems/Minif2f/mathd_algebra_478.lean \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5

# Batch from config
python -m scripts.run_claude batch config/config_minif2f.yaml

# All .lean files in a folder
python -m scripts.run_claude from-folder leanproblems/Minif2f \
  --prompt-file prompts/prompt_complete_file.txt \
  --max-rounds 5

# Parallel batch
python -m scripts.run_claude batch config/config_minif2f.yaml --parallel --max-workers 4
```

### MCP setup
MCP is directory-scoped; add it in the target working directory:
```bash
cd leanproblems
claude mcp add lean-lsp -- /absolute/path/to/lean-lsp-mcp/numina-lean-mcp.sh
claude mcp list
```

## Configuration System

### YAML example
```yaml
defaults:
  task_type: file
  prompt_file: prompts/prompt_complete_file.txt
  cwd: .
  check_after_complete: true
  permission_mode: bypassPermissions
  result_dir: results/minif2f
  mcp_log_dir: mcp_logs/minif2f
  max_rounds: 2
  git_commit: false  # optional per-round git commits

tasks:
  - target_path: leanproblems/Minif2f/algebra_sqineq_2atp2bpge2ab.lean
    mcp_log_name: algebra_sqineq_2atp2bpge2ab
  - target_path: leanproblems/Minif2f/imo_1964_p1.lean
    mcp_log_name: imo_1964_p1
    max_rounds: 5  # override default
```

### Inheritance rules
- `defaults` define baseline values.
- Each task inherits defaults and may override any field.
- Final config = defaults + task overrides.

## Theorem-Proving Workflow

### Core conventions
1. No-axiom policy: never use `axiom`; only `sorry` for unfinished parts.
2. Verification: after edits, run `lean_diagnostic_messages`.
3. Tool priority: prefer `simp`, `native_decide`, `norm_cast`, etc.
4. Blueprint sync: in subagent mode, `BLUEPRINT.md` is the single source of truth; update immediately.

### Prompt system key cues
- Use `lean_diagnostic_messages`; severity 1 means errors.
- Prefer `simp`, then `simp?` for minimal simp lemmas.
- Use `native_decide` for computation goals.
- Use `#eval` to evaluate expressions.
- Use `norm_cast` for coercions.
- Use `apply?` to find applicable lemmas.
- If `decide` times out, do not raise `maxHeartbeats`; prove symbolically with mathlib lemmas.

### End signals
The runner reacts to:
- `END_REASON:COMPLETE` — file has no `sorry` and compiles cleanly.
- `END_REASON:LIMIT` — round limit hit or `sorry`/errors remain.

## Subagent Architecture

Supported agents:
1. **Coordinator** — orchestration; reads blueprint and assigns work
2. **Blueprint Agent** — refines mathematical blueprints using Gemini/GPT
3. **Sketch Agent** — formalizes informal statements into Lean code
4. **Proof Agent** — proves specific lemmas/theorems

## Lean LSP Tooling

### Key tools
- `lean_file_outline` — file outline (imports, declarations)
- `lean_local_search` — quick declaration lookup
- `lean_goal` — inspect proof state
- `lean_diagnostic_messages` — compile/diagnostic check
- `lean_leandex` — semantic theorem search
- `lean_loogle` — expression/type search
- `lean_leanfinder` — concept-based search
- `lean_state_search` — proof-state search

### Usage principles
- Line/column indices are 1-based.
- Analyze/search context before each edit.
- Prefer `lean_diagnostic_messages` over `lake build` for validation.

## Environment Variables

```bash
# Example .env
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_AUTH_TOKEN=sk-...
export API_TIMEOUT_MS=600000
export ANTHROPIC_MODEL=deepseek-chat
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
```

## Important Files

- [scripts/runner.py](scripts/runner.py) — core session loop
- [scripts/task.py](scripts/task.py) — task metadata and results
- [prompts/prompt_complete_file.txt](prompts/prompt_complete_file.txt) — standard prompt template
- [tutorial/usage.md](tutorial/usage.md) — detailed usage guide
- [tutorial/setup.md](tutorial/setup.md) — environment setup guide
- [prompts/prompt_complete_file.txt](prompts/prompt_complete_file.txt) - 标准提示模板
