# Project Startup Notes

These notes explain how a future Codex session should restart work on this project without losing context.

## Why This File Exists

This project has two kinds of complexity:

- cultural complexity: sources, themes, interpretation, institutional metadata, subjective curation
- infrastructure complexity: Docker, PixPlot, large image folders, SQLite state, generated browser atlases

The goal is to make future work resume from known state instead of rediscovering the same problems.

## Automatic Startup Instructions

The repo root now has `AGENTS.md`.

That file is the project-level startup instruction file for Codex-style agents. It should be treated as the first operational guide for this repository. If a future environment does not automatically load it, the first manual step is simply: read `AGENTS.md`.

The human-readable companion files are:

- `PROJECT_MEMORY.md`
- `docs/project-startup-notes.md`
- `docs/serpent-atlas-workflow.md`
- `docs/pixplot-integration-notes.md`

## Current Working State

As of May 2, 2026:

- the fork is on GitHub at `https://github.com/giosampietro/Meta-Curation-in-Cultural-Sphere`
- the serpent collection exists at `data/samples/serpents-open-5k`
- the generated PixPlot atlas exists at `data/pixplot/serpents-open-5k`
- the atlas preview URL is `http://127.0.0.1:8771/data/pixplot/serpents-open-5k/`
- PixPlot runs through Docker image `metacuration-pixplot:local`
- generated data remains ignored by Git

The 5k serpent atlas contains:

- 5,307 downloaded image files
- 5,307 clean PixPlot metadata rows
- 5,306 images processed by PixPlot
- one oblong image skipped by PixPlot
- source/layer/search-term toggles patched into the generated atlas

## Docker Recovery Notes

Docker failed because the Docker Desktop backend was alive but not responding through its socket.

The useful health check is:

```bash
curl --unix-socket /Users/giorgio/.docker/run/docker.sock http://localhost/_ping
```

Healthy result:

```text
OK
```

Failure patterns:

- `docker ps` hangs
- `docker info` hangs
- `_ping` hangs
- the socket file exists but does not respond

The fix that worked:

1. Identify the stuck `com.docker.backend` process.
2. Force-stop that backend process.
3. Reopen Docker Desktop.
4. Wait for the engine to restart.
5. Verify `_ping` returns `OK`.
6. Only then run Docker build/run commands.

Do not delete Docker images, containers, volumes, or project data as a first response. The problem was not corrupted project data; it was a stuck backend.

## PixPlot Strategy

PixPlot should stay inside Docker.

Reason:

- PixPlot pulls a heavy machine-learning stack.
- Local system Python may be the wrong version.
- The Docker image isolates TensorFlow, PixPlot, and pinned dependencies.

The Docker image is:

```text
metacuration-pixplot:local
```

The 5k atlas command is recorded in `docs/serpent-atlas-workflow.md`.

## Large Collection Strategy

For future large topics:

1. Run count-only probes first.
2. Start with open/no-key sources.
3. Normalize into shared metadata fields.
4. Store state in SQLite.
5. Make source/record failures non-fatal.
6. Use controlled parallel downloads.
7. Generate review HTML and PixPlot metadata before clustering.
8. Verify metadata rows match image files before PixPlot.
9. Run PixPlot only after the dataset is clean.

One failed museum record should never stop the atlas.

## Known Source Behavior

Met:

- no key required
- good open-access source
- search is slow at scale because it returns object IDs first
- object records can return 403
- search terms can return 403
- skip bad records/terms and continue

V&A:

- no key required for current workflow
- strong source for volume
- useful for expanded symbolic/mythic serpent material

Art Institute of Chicago:

- no key required
- public domain filter works well
- lower volume than V&A, but high metadata quality

Cleveland Museum of Art:

- no key required
- clean open-access API
- medium volume

Rijksmuseum and Cooper Hewitt:

- not yet implemented in the current connector set
- need careful API/image-resolution work before being part of the main scrape

Harvard, Europeana, Smithsonian:

- likely useful later
- require API keys or extra setup

## Metadata Integrity Rule

Before PixPlot, always verify:

- image count
- metadata row count
- unique filenames
- source split
- layer split

Important bug fixed:

The metadata collector must use the exact `filename` field from each metadata JSON when available. Prefix matching can make object `1` accidentally match `10.jpg`, `100.jpg`, etc., which creates false extra rows.

## Communication Rule

The user wants to understand what is happening but does not want to manage files or terminal commands directly.

Good update style:

- short
- concrete
- plain language
- explains the consequence

Example:

```text
Docker is responding again. The issue was the backend socket, not the PixPlot code or the image collection.
```

Avoid presenting long command blocks unless documenting memory or giving explicit instructions.

