# Amanoba Menubar User Guide

This guide explains what you can do from the macOS menu bar app (`AmanobaMenubar`).

## Install

```bash
cd /Users/moldovancsaba/Projects/amanoba_courses
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

## What You See

- `Amanoba v0.1.0`
- `Health: dashboard up|down`
- `Power: gentle|balanced|fast`
- `Jobs: pending | running | done | failed`

When a job is running, the menu-bar title changes from `AQ` to `AQ*`.

## Daily Actions

- `Open Control Center`
- `Open Feed JSON`
- `Open Health JSON`
- `Process One Job`
- `Scan Workspace`

The control center opens the kanban board where you can inspect completed cards in a modal and challenge a result back into the queue with a single comment.

## Power Control

- `Set Gentle Mode`
- `Set Balanced Mode`
- `Set Fast Mode`

These actions call the dashboard power-mode API and persist the chosen mode to `course_quality_daemon.json`.

## Operations

- `Restart Services`
- `Install/Refresh Services`
- `Open Logs Folder`

## Auto-Launch

The installer adds `AmanobaMenubar.app` to macOS Login Items when possible, so it starts automatically after login.
