# Amanoba Mac Mini Install Handoff

This document is the exact handoff to give an AI agent when installing, validating, and operating Amanoba on a Mac mini.

It is written to be self-contained: one repository, one order of operations, one command list, one validation path.

## Repository and workspace

- Product repository: `https://github.com/moldovancsaba/amanoba_courses.git`
- Local workspace: `/Users/moldovancsaba/Projects/amanoba_courses`
- Live Amanoba app workspace: `/Users/moldovancsaba/Projects/amanoba`
- Planning / backlog repository: `https://github.com/moldovancsaba/mvp-factory-control`
- Planning board: `https://github.com/users/moldovancsaba/projects/1`

## Current runtime target

- Current operator-facing build: `Amanoba v0.2.0`
- The menubar and dashboard must match the current repo state exactly.
- The menubar must remain a single bundle: `AmanobaMenubar.app`
- The dashboard must show the compact `Model Roster`
- The resident creator roles must stay warm on:
  - `127.0.0.1:8080` for `DRAFTER`
  - `127.0.0.1:8081` for `WRITER`
  - `127.0.0.1:8082` for `JUDGE`

## Required tools and models

### Tools

- `git`
- `rg`
- `node`
- `npm`
- `tsx`
- `vercel`
- `launchctl`
- `caffeinate`
- `swiftc`
- `ollama`
- `mlx_lm`

### Models

- `DRAFTER`: Gemma 3 270M
- `WRITER`: Granite 4.0 350M (H-variant)
- `JUDGE`: Qwen 2.5 0.5B
- Fallback runtime: `ollama` with keep-alive behavior

## Required source of truth

Read these before changing anything:

- `/Users/moldovancsaba/Projects/amanoba_courses/docs/current-ssot.md`
- `/Users/moldovancsaba/Projects/amanoba_courses/docs/system-versioning.md`
- `/Users/moldovancsaba/Projects/amanoba_courses/docs/local-course-quality-daemon.md`
- `/Users/moldovancsaba/Projects/amanoba_courses/docs/menubar-user-guide.md`
- `/Users/moldovancsaba/Projects/amanoba_courses/docs/user-manual.md`
- `/Users/moldovancsaba/Projects/amanoba_courses/docs/reference/sovereign-course-creator-compatibility-contract.md`
- `/Users/moldovancsaba/Projects/amanoba_courses/docs/reference/quiz-quality-pipeline-handover.md`
- `/Users/moldovancsaba/Projects/amanoba_courses/docs/reference/quiz-quality-pipeline-playbook.md`
- `/Users/moldovancsaba/Projects/amanoba_courses/docs/reference/course-creation-qa-playbook.md`

## Required machine bootstrap order

1. Pull or clone the repository.
2. Read the SSOT docs.
3. Restore or create `.env.local` from the linked Vercel project.
4. Verify the local QC runtime sees the real MongoDB connection.
5. Install or refresh launch agents.
6. Install or refresh the menubar.
7. Start the QC stack.
8. Verify the resident models.
9. Verify the worker and watchdog.
10. Verify the menubar and dashboard.
11. Commit and push the final state to `origin/main`.

## Required environment bootstrap

If `.env.local` is missing or stale, recreate it from Vercel before starting the stack.

Required values:

- `MONGODB_URI`
- `DB_NAME=amanoba`
- optional: `OPENAI_API_KEY`

Supported bootstrap commands:

```bash
vercel login
vercel link
vercel env ls
vercel env pull .env.local
```

After pulling env vars, verify that `.env.local` contains the required values before proceeding.

## Required command order

### 1. Sync repo

```bash
cd /Users/moldovancsaba/Projects/amanoba_courses
git checkout main
git pull origin main
```

### 2. Read the SSOT

```bash
sed -n '1,220p' docs/current-ssot.md
sed -n '1,160p' docs/system-versioning.md
sed -n '1,220p' docs/local-course-quality-daemon.md
sed -n '1,140p' docs/menubar-user-guide.md
sed -n '1,160p' docs/user-manual.md
```

### 3. Bootstrap environment

```bash
vercel login
vercel link
vercel env ls
vercel env pull .env.local
```

Then confirm:

```bash
rg -n "MONGODB_URI|DB_NAME=amanoba|OPENAI_API_KEY" .env.local
```

### 4. Install dependencies if needed

```bash
npm install
```

### 5. Install or refresh launch agents

```bash
bash scripts/install-course-quality-launchagents.sh
```

### 6. Install or refresh the menubar

```bash
bash tools/macos/AmanobaMenubar/install_AmanobaMenubar.sh
open ~/Applications/AmanobaMenubar.app
```

If the menubar looks stale, rerun the installer from the current checkout. The installer is expected to remove the old bundle and replace it cleanly.

### 7. Verify services

```bash
launchctl print gui/$UID/com.amanoba.coursequality.worker
launchctl print gui/$UID/com.amanoba.coursequality.dashboard
launchctl print gui/$UID/com.amanoba.coursequality.watchdog
launchctl print gui/$UID/com.amanoba.coursequality.ollama
```

### 8. Verify resident models

- Check `http://127.0.0.1:8080`
- Check `http://127.0.0.1:8081`
- Check `http://127.0.0.1:8082`
- Confirm the dashboard shows the compact `Model Roster`

### 9. Verify worker progress

- Confirm `worker working`
- Confirm `pending` decreases over time
- Confirm `done` increases over time
- Confirm the worker does not freeze on a single lesson

### 10. Verify menubar behavior

- Menubar version must show `Amanoba v0.2.0`
- Menu must show only:
  - `Open Dashboard`
  - `Restart Services`
  - `Shutdown Services`
  - `Quit`
- No debug-only items
- No `Open Health JSON`
- No long filesystem paths in visible labels

### 11. Keep the machine awake

The stack must run under `caffeinate` or equivalent launch-managed awake behavior so the Mac does not sleep while the QC system is live.

### 12. Commit and push

```bash
git status --short
git add -A
git commit -m "Bring Amanoba Mac mini handoff into sync"
git push origin main
```

## Exact task order for the agent

1. Sync the repo.
2. Read the SSOT.
3. Pull `.env.local` from Vercel.
4. Verify MongoDB and environment variables.
5. Install dependencies.
6. Install launch agents.
7. Install the menubar.
8. Start the stack.
9. Verify the resident models.
10. Verify the dashboard.
11. Verify the worker and watchdog.
12. Fix any mismatch between docs and runtime.
13. Keep the system awake and automatic.
14. Commit and push.

## Definition of success

- One repository is the source of truth: `amanoba_courses`
- The Mac mini has one installed menubar bundle only
- The menubar matches the repo
- The dashboard matches the runtime
- The resident models are warm
- The QC worker advances automatically
- The watchdog repairs stalls
- `.env.local` is recreated from Vercel when needed
- The final commit is pushed to `origin/main`

