# Amanoba Mac Mini Install Handoff

Use this document as the single copy-paste handoff for an AI agent that must install, validate, harden, and operate Amanoba on a Mac mini.

This version is portable. It does not assume a fixed home directory. Substitute `<USER_HOME>` with the actual account home on the target machine, or use `$HOME` directly in shell commands.

## Repositories

- Product repository: `https://github.com/moldovancsaba/amanoba_courses.git`
- Planning / backlog repository: `https://github.com/moldovancsaba/mvp-factory-control`
- Planning board: `https://github.com/users/moldovancsaba/projects/1`

## Local Workspaces

- Amanoba courses workspace: `<USER_HOME>/Projects/amanoba_courses`
- Live Amanoba app workspace: `<USER_HOME>/Projects/amanoba`

## Required Runtime Target

- Current operator-facing build: `Amanoba v0.2.0`
- Menubar bundle: `AmanobaMenubar.app`
- Dashboard roster: compact `Model Roster`
- Resident roles:
  - `DRAFTER` on `127.0.0.1:8080`
  - `WRITER` on `127.0.0.1:8081`
  - `JUDGE` on `127.0.0.1:8082`
- Fallback runtime: `ollama`

## Required Tools

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

## Required Models

- `DRAFTER: Gemma 3 270M`
- `WRITER: Granite 4.0 350M (H-variant)`
- `JUDGE: Qwen 2.5 0.5B`

## Source of Truth

Read these files before changing anything:

- `<USER_HOME>/Projects/amanoba_courses/docs/current-ssot.md`
- `<USER_HOME>/Projects/amanoba_courses/docs/system-versioning.md`
- `<USER_HOME>/Projects/amanoba_courses/docs/local-course-quality-daemon.md`
- `<USER_HOME>/Projects/amanoba_courses/docs/menubar-user-guide.md`
- `<USER_HOME>/Projects/amanoba_courses/docs/user-manual.md`
- `<USER_HOME>/Projects/amanoba_courses/docs/reference/sovereign-course-creator-compatibility-contract.md`
- `<USER_HOME>/Projects/amanoba_courses/docs/reference/quiz-quality-pipeline-handover.md`
- `<USER_HOME>/Projects/amanoba_courses/docs/reference/quiz-quality-pipeline-playbook.md`
- `<USER_HOME>/Projects/amanoba_courses/docs/reference/course-creation-qa-playbook.md`

## Environment Bootstrap

If `.env.local` is missing or stale, recreate it from Vercel before starting the stack.

Required env values:

- `MONGODB_URI`
- `DB_NAME=amanoba`
- optional: `OPENAI_API_KEY`

Use Vercel as the source of truth:

```bash
cd "<USER_HOME>/Projects/amanoba"
vercel login
vercel link --yes --scope narimato --project amanoba
vercel env ls
vercel env pull .env.local --yes
npm install
```

Then verify:

```bash
rg -n "MONGODB_URI|DB_NAME=amanoba|OPENAI_API_KEY" .env.local
```

## Required Order

1. Sync the repo.
2. Read the SSOT docs.
3. Pull `.env.local` from Vercel.
4. Verify the environment variables.
5. Install dependencies if needed.
6. Install or refresh launch agents.
7. Install or refresh the menubar.
8. Start the QC stack.
9. Verify the resident models.
10. Verify the dashboard.
11. Verify the worker and watchdog.
12. Keep the system awake.
13. Fix any mismatch between docs and runtime.
14. Commit and push the final state to `origin/main`.

## Commands in Exact Order

### 1. Sync repo

```bash
cd "<USER_HOME>/Projects/amanoba_courses"
git fetch --all --prune
git checkout main
git pull --rebase origin main
```

### 2. Read SSOT docs

```bash
sed -n '1,220p' docs/current-ssot.md
sed -n '1,200p' docs/system-versioning.md
sed -n '1,240p' docs/local-course-quality-daemon.md
sed -n '1,160p' docs/menubar-user-guide.md
sed -n '1,220p' docs/user-manual.md
sed -n '1,220p' docs/reference/sovereign-course-creator-compatibility-contract.md
sed -n '1,220p' docs/reference/quiz-quality-pipeline-handover.md
sed -n '1,220p' docs/reference/quiz-quality-pipeline-playbook.md
sed -n '1,220p' docs/reference/course-creation-qa-playbook.md
```

### 3. Bootstrap environment from Vercel

```bash
cd "<USER_HOME>/Projects/amanoba"
vercel login
vercel link --yes --scope narimato --project amanoba
vercel env ls
vercel env pull .env.local --yes
```

Then confirm:

```bash
rg -n "MONGODB_URI|DB_NAME=amanoba|OPENAI_API_KEY" .env.local
```

### 4. Install dependencies

```bash
cd "<USER_HOME>/Projects/amanoba"
npm install
```

### 5. Install launch agents

```bash
bash scripts/install-course-quality-launchagents.sh
```

### 6. Install the menubar

```bash
bash tools/macos/AmanobaMenubar/install_AmanobaMenubar.sh
open "$HOME/Applications/AmanobaMenubar.app"
```

If the menubar looks stale, rerun the installer from the current checkout. The installer must replace the old bundle instead of layering on top of it.

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

- Confirm the worker is working
- Confirm `pending` decreases over time
- Confirm `done` increases over time
- Confirm the worker does not freeze on one lesson
- Confirm the watchdog repairs stalls instead of leaving the worker wedged

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

Run the stack under `caffeinate` or equivalent launch-managed awake behavior so the Mac does not sleep while Amanoba is live.

### 12. Fix any mismatch

- Update docs if the code/runtime changed.
- Update code if the docs reflect the intended live runtime and the implementation drifted.
- Remove stale bundles or stale references.

### 13. Commit and push

```bash
git status --short
git add -A
git commit -m "Sync Amanoba Mac mini handoff"
git push origin main
```

## Definition of Success

- One repository is the source of truth: `amanoba_courses`
- One menubar bundle exists on the machine
- The menubar matches the repo
- The dashboard matches the runtime
- The resident models are warm
- The QC worker advances automatically
- The watchdog repairs stalls
- `.env.local` is recreated from Vercel when needed
- The final commit is pushed to `origin/main`
