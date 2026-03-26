# Amanoba Menubar User Guide

This guide explains what you can do from the macOS menu bar app (`AmanobaMenubar`) for `Amanoba v0.2.0`.

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

If the installed menubar looks stale or different from the repo source, run the installer again from the current checkout. The installer now quits any running copy and replaces the bundle before rebuilding.

## What You See

- `Amanoba v0.2.0`
- `Health: dashboard up|down`
- `Power: gentle|balanced|fast`
- `Jobs: pending | running | done | failed`

The menu-bar title uses simple color states:

- `🟢 AQ` when QC work is running
- `⚪ AQ` when the dashboard is healthy and no card is running
- `🔴 AQ` when the dashboard health check fails

## Daily Actions

- `Open Dashboard`
- `Scan Now`
- `Refresh Now`

The menubar is a small operator surface. It opens the dashboard, triggers a fresh scan, refreshes the status snapshot, switches power modes, restarts services, and opens logs.

## Power Control

- `Gentle Mode`
- `Balanced Mode`
- `Fast Mode`

These actions call the dashboard power-mode API and persist the chosen mode to `course_quality_daemon.json`.

## Operations

- `Restart Services`
- `Install/Refresh Services`
- `Open Logs Folder`

The underlying background model is:

- one long-lived QC worker daemon
- one dashboard service
- one watchdog service
- one launch-managed `caffeinate` service
- MLX/Apertus as the primary writer, with Ollama used only as fallback when MLX is unavailable

## Auto-Launch

The installer adds `AmanobaMenubar.app` to macOS Login Items when possible, so it starts automatically after login.
