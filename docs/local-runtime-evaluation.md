# Local Runtime Evaluation

## Status and SSOT

- **Status:** supporting migration note
- **Document owner:** Amanoba maintainers
- **Runtime SSOT:** `docs/current-ssot.md`
- **Conflict rule:** if this note conflicts with the current code or runtime docs, the code/runtime docs win and this file should be updated or treated as historical context

## What was checked

- Offline-first local routing patterns for resident model servers and fallback models.
- A single continuous worker loop with health checks, heartbeat tracking, and watchdog repair.
- macOS menubar packaging for a small operator-facing control surface.
- Restart-proof launchd patterns with `RunAtLoad`, `KeepAlive`, and `StartInterval` where appropriate.
- Confidence/trust-tier style state reporting for queue items and live runtime health.

## Decision for Amanoba

Use this stack in order:

1. `mlx` as the primary local rewrite backend.
2. `ollama` as the fallback local rewrite backend.

Optional, not active in the default Amanoba runtime order:

- `openai` only when internet is available and an API key exists

The code still keeps an internal null provider as a guard rail, but it is not part of the documented runtime stack and is not shown in the UI.

## Current machine check

- `ollama`: installed locally.
- `mlx`: installed locally.
- `mlx_lm`: installed and usable for text-generation.
- hardware: Apple Silicon.
- resident creator roles are served on local ports `8080`, `8081`, and `8082`.

## Sovereign patterns adopted

- dashboard/ollama launchd `RunAtLoad` + `KeepAlive`
- worker launchd `RunAtLoad` + `KeepAlive`
- watchdog launchd `RunAtLoad` + `StartInterval`
- dedicated worker and dashboard services
- optional managed local `ollama` service
- dedicated MLX interpreter for health checks and generation
- watchdog-enforced primary writer policy for MLX/Apertus
- resident creator role servers that stay warm across requests
- low-power Ollama defaults for fallback background rewriting
- confidence score + trust tier on queued and completed jobs
- health snapshot for provider selection and dashboard display

## Why keep this standalone

The current system should stay self-contained. The implementation copies the useful patterns, but it does not depend on any of the older systems at runtime. That keeps the Mac mini migration simpler and avoids hidden coupling to other codebases.
