# Amanoba User Manual

Owner: `amanoba_courses`

Current SSOT status:

- current operational manual for `Amanoba v0.2.0`
- if this file conflicts with live code or runtime, the code/runtime wins and this file must be updated

## Status and SSOT

- **Status:** current user manual
- **Document owner:** Amanoba maintainers
- **Runtime SSOT:** `docs/current-ssot.md`
- **Conflict rule:** if the live control surface changes, update this manual before treating it as user-facing documentation

## What this system does

The system keeps a local course-quality workflow running in the background.
It watches the live queue, repairs weak lessons and quiz questions, and keeps the core models resident so work can continue without manual restarts.

## Surfaces

- dashboard: `http://127.0.0.1:8765`
- menubar app: `AmanobaMenubar`
- launch agents:
  - `com.amanoba.coursequality.worker`
  - `com.amanoba.coursequality.dashboard`
  - `com.amanoba.coursequality.watchdog`
  - `com.amanoba.coursequality.caffeinate`
  - `com.amanoba.coursequality.ollama` when available
  - `com.amanoba.coursequality.role.drafter`
  - `com.amanoba.coursequality.role.writer`
  - `com.amanoba.coursequality.role.judge`

## What Operators Should See

- a compact `Model Roster` in the dashboard
- `mlx` as the primary QC writer
- `ollama` available as warm fallback
- the current MLX interpreter and model snapshot are configured in `course_quality_daemon.json`
- resident creator roles:
  - `DRAFTER` on `127.0.0.1:8080` using `Gemma 3 270M`
  - `WRITER` on `127.0.0.1:8081` using `Granite 4.0 350M (H)`
  - `JUDGE` on `127.0.0.1:8082` using `Qwen 2.5 0.5B`
- a single continuous QC worker
- a watchdog that repairs stalls and repeated timeout loops

## Main Screens

### Dashboard

Open the dashboard from the menubar or at:

- `http://127.0.0.1:8765`

The dashboard shows:

- `Course Creator`
- `Quality Control`
- the live queue
- live worker state
- power mode
- the compact `Model Roster`

### Menubar

The menubar is intentionally short. It shows:

- current health
- current power mode
- job counts
- the three role badges:
  - `DRAFTER`
  - `WRITER`
  - `JUDGE`

It also provides these actions:

- `Open Dashboard`
- `Restart Services`
- `Shutdown Services`
- `Quit`

## Menubar Rules

- short labels only
- no debug-only items
- no long filesystem paths
- no `Open Health JSON`

## Model Roster

The dashboard shows one compact `Model Roster` row with five live entries:

- `DRAFTER`
- `WRITER`
- `JUDGE`
- `mlx`
- `ollama`

The short labels are deliberate. The interface does not show long filesystem paths in the menubar.

## Typical Workflow

1. Open the menubar app.
2. Check whether the title shows the green, white, orange, or red state.
3. Open the dashboard if you want more detail.
4. Watch the `Active Now` and `Done` columns to confirm work is moving.
5. Use `Restart Services` only if the stack stops responding.

## What the Colors Mean

- `🟢 AQ` means work is running.
- `⚪ AQ` means the dashboard is healthy and no card is currently running.
- `🟠 AQ` means the worker is stalled and should be repaired.
- `🔴 AQ` means the health check failed.

## Always-On Rules

- install or refresh launch agents with `bash scripts/install-course-quality-launchagents.sh`
- bootstrap the live Amanoba app with:
  - `vercel login`
  - `vercel link --yes --scope narimato --project amanoba`
  - `vercel env ls`
  - `vercel env pull .env.local --yes`
- keep the Mac awake with the launch-managed `caffeinate` service
- use the dashboard and menubar as operator surfaces, not as debugging consoles

## Dependency Faults

- if the live Amanoba bridge cannot run, the worker heartbeat should show `waiting-dependency`
- `/Users/chappie/Projects/amanoba/.env.local` must include `MONGODB_URI` and `DB_NAME="amanoba"`
- if `MONGODB_URI` is missing in `/Users/chappie/Projects/amanoba/.env.local`, the worker is not live-configured yet
- the dashboard and watchdog should remain up even when the queue cannot advance

## What to Do If Work Looks Stuck

1. Open the dashboard and check `Active Now`.
2. Check the worker line in the live status strip.
3. Check the `Model Roster`.
4. If the worker is stalled, use `Restart Services`.
5. If the same item keeps failing, it may be quarantined for review instead of looping forever.

## What Not To Expect

- The menubar is not a debug console.
- The menubar does not expose raw health JSON.
- The dashboard does not show internal paths as the primary model labels.
- The system can still be slowed by macOS memory pressure, but the watchdog will try to recover resident models automatically.

## Fresh Install / Bootstrap

If you are installing the QC system on a new machine, recreate the local env file from the linked Vercel project before starting the services.

Required local file:

- `.env.local`

Minimum required values:

- `MONGODB_URI`
- `DB_NAME=amanoba`
- optional: `OPENAI_API_KEY` if you want the OpenAI fallback path

Bootstrap commands:

```bash
vercel login
vercel link
vercel env ls
vercel env pull .env.local
```

Then:

1. Verify `.env.local` contains `MONGODB_URI` and `DB_NAME`.
2. Install or refresh the launch agents.
3. Start the dashboard, worker, and watchdog.
4. Confirm the resident roles are up on `8080`, `8081`, and `8082`.

## Menubar Reset If It Looks Different

If the menubar on a machine does not match the repo, reinstall it from the current checkout. The installer now quits the running copy and removes the old app bundle before rebuilding, so the new bundle replaces stale UI state instead of layering on top of it.

## Short Version

- Use the menubar for quick status.
- Use the dashboard for detailed control.
- Use `Restart Services` only when the system is not moving.
