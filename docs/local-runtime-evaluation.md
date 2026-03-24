# Local Runtime Evaluation

## What was checked

- `{hatori}` uses local adapters for `ollama` and `llama.cpp`, with health checks and offline-first routing.
- `{reply}` uses `ollama` directly as its local LLM backend.
- `openclaw` contains mature control UI and macOS menubar packaging patterns, but it is a much larger TypeScript system than this course worker needs.
- `{sovereign}` contains the strongest restart-proof launchd patterns and a practical confidence/trust-tier model.

## Decision for Amanoba

Use this stack in order:

1. `ollama` as the primary local rewrite backend.
2. `mlx` as the secondary local rewrite backend.

Optional, not active in the default Amanoba runtime order:

- `openai` only when internet is available and an API key exists

The code still keeps an internal null provider as a guard rail, but it is not part of the documented runtime stack and is not shown in the UI.

## Current machine check

- `ollama`: installed locally.
- `mlx`: installed locally.
- `mlx_lm`: installed and usable for text-generation.
- hardware: Apple Silicon (`Apple M1 Pro`).

## Sovereign patterns adopted

- dashboard/ollama launchd `RunAtLoad` + `KeepAlive`
- worker/watchdog launchd `RunAtLoad` + `StartInterval`
- dedicated worker and dashboard services
- optional managed local `ollama` service
- low-power Ollama defaults for continuous background rewriting
- confidence score + trust tier on queued and completed jobs
- health snapshot for provider selection and dashboard display

## Why not directly embed Hatori, Reply, OpenClaw, or Sovereign

They are useful references, but coupling this project directly to those codebases would create unnecessary dependency and maintenance risk. The correct move here is to copy the proven patterns, not add a runtime dependency on those repos.
