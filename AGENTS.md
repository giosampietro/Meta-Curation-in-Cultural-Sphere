# Project Startup Instructions for Codex

This project is a forked, evolving research tool. Treat it as both cultural-method documentation and working software.

## Read First

At the start of a new session, read these files before making assumptions:

1. `PROJECT_MEMORY.md`
2. `docs/project-startup-notes.md`
3. `docs/serpent-atlas-workflow.md`
4. `docs/pixplot-integration-notes.md`

Generated data lives under `data/` and is intentionally ignored by Git. Do not try to commit downloaded images, PixPlot output, SQLite catalogs, or generated review pages.

## User Preference

The user does not want to operate through terminal/files directly. Handle the technical layer, then explain outcomes in plain language:

- what was done
- where the result is
- what is working
- what is blocked
- what to do next

Avoid giving raw command-heavy instructions unless the user asks for them or they are needed for project memory.

## Current Stable State

The current main atlas is:

- Collection: `data/samples/serpents-open-5k`
- PixPlot atlas: `data/pixplot/serpents-open-5k`
- Preview URL: `http://127.0.0.1:8771/data/pixplot/serpents-open-5k/`
- Docker image: `metacuration-pixplot:local`

The preview server may already be running on port `8771`. If starting it fails with `EADDRINUSE`, check the URL directly before starting another server.

## Docker/PixPlot Rules

PixPlot should run through Docker, not system Python. The dependency stack is heavy and fragile.

Before running PixPlot:

1. Check Docker socket health:
   `curl --unix-socket /Users/giorgio/.docker/run/docker.sock http://localhost/_ping`
2. Expected result: `OK`
3. If Docker commands hang, do not repeatedly retry heavy Docker commands.
4. Diagnose the socket/backend first.

Known Docker failure mode:

- Symptom: `docker ps`, `docker info`, or `_ping` hangs or never replies.
- Likely cause: Docker Desktop backend is wedged.
- Fix that worked on May 2, 2026: force-stop the stuck `com.docker.backend` process, reopen Docker Desktop, wait, then verify `_ping` returns `OK`.

Do not delete Docker images, containers, volumes, or project data unless the user explicitly asks.

## Large Scrape Rules

For large museum scrapes:

- Start with count-only probes.
- Use no-key/open sources first.
- Make failures non-fatal: one bad museum record or search term must not kill the whole atlas.
- Use SQLite state for resume/dedupe.
- Use controlled parallel downloads, not uncontrolled scraping.
- Record what was collected by source, layer, and search term.

For Met specifically:

- Met search returns object IDs first, then object details must be fetched one by one.
- Met can return 403 for individual searches or records.
- Skip inaccessible Met records/source-term failures rather than aborting the run.

## PixPlot Metadata Rules

Before running PixPlot, verify:

- image file count matches metadata row count
- metadata filenames are unique
- `source`, `theme_layer`, `search_term`, and `rights` are present

The metadata writer must use the exact `filename` stored in metadata JSON when available. Prefix matching can create false duplicates, for example object `1` accidentally matching `10.jpg`.

## Documentation Rules

When resolving an infrastructure issue, update:

- `PROJECT_MEMORY.md` for current state
- the relevant workflow doc under `docs/`
- tests if the issue was code-related

Commit and push small, meaningful changes. Keep generated data ignored.

