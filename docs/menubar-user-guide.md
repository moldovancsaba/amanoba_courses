# Amanoba Menubar User Guide

This guide explains what you can do from the macOS menu bar app (`AmanobaMenubar`).

Current build version:

- `Amanoba v0.2.0`

## Status and SSOT

- **Status:** current user guide
- **Document owner:** Amanoba maintainers
- **Runtime SSOT:** `docs/current-ssot.md`
- **Conflict rule:** if the menubar changes, update this guide to match the rebuilt app before using it as user-facing documentation

## Install

```bash
cd /Users/chappie/Projects/amanoba_courses
bash tools/macos/AmanobaMenubar/install_AmanobaMenubar.sh
```

Run it:

```bash
open ~/Applications/AmanobaMenubar.app
```

One-command install and run:

```bash
bash tools/macos/AmanobaMenubar/run_AmanobaMenubar.sh
```

Resource and dependency check:

```bash
bash tools/macos/AmanobaMenubar/check_AmanobaMenubar_resources.sh
```

If the installed menubar looks stale or different from the repo source, run the installer again from the current checkout. The installer quits any running copy and replaces the bundle before rebuilding.

## What You See

- `Amanoba v0.2.0`
- `Health: dashboard up | worker idle|working|stalled`
- `Power: gentle|balanced|fast`
- `Jobs: pending | running | done | failed`
- a compact `Model Roster` in the dashboard with five live entries:
  - `DRAFTER`
  - `WRITER`
  - `JUDGE`
  - `mlx`
  - `ollama`

The menu-bar title uses simple color states:

- `🟢 AQ` when QC work is running
- `⚪ AQ` when the dashboard is healthy and no card is running
- `🔴 AQ` when the dashboard health check fails

## Daily Actions

- `Open Dashboard`
- `Restart Services`
- `Shutdown Services`
- `Quit`

`Open Dashboard` opens the browserview control center. The current UI shows the `Course Creator` and `Quality Control` pages and the live queue.

`Restart Services` bootstraps the worker, dashboard, watchdog, and Ollama launch agents again.

`Shutdown Services` boots those launch agents out of `gui/$UID`.

`Quit` closes the menubar app after requesting service shutdown.

## Operations

- one long-lived QC worker daemon
- one dashboard service
- one watchdog service
- one launch-managed `caffeinate` service
- resident MLX creator roles for:
  - drafter on `8080`
  - writer on `8081`
  - judge on `8082`
- Ollama fallback with `keep_alive`
- launch agents wrapped in `caffeinate -dimsu`
- menubar title uses only short role labels, not model paths

## Auto-Launch

The installer adds `AmanobaMenubar.app` to macOS Login Items when possible, so it starts automatically after login.
