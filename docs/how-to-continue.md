# How To Continue This Project

This page is the handoff note for the next working session.

## Start Here

Read these files in this order:

1. `PROJECT_MEMORY.md`
2. `docs/original-first-walkthrough.md`
3. `docs/dependency-and-runnability-audit.md`
4. `docs/met-sample-run-report.md`
5. `docs/nontechnical-project-map.md`
6. `docs/phase-2-runnable-workflow.md`
7. `docs/pixplot-integration-notes.md`

That sequence explains the project before touching code.

## What Has Already Been Proven

The original project can collect real images and metadata from the Metropolitan Museum of Art API.

The first safe run:

- searched for `cloud`
- found 278 Met object records
- processed 2 object records
- downloaded 8 images
- saved 2 metadata files
- produced a local browser review page

Local sample page:

- `data/samples/met-cloud-test/review.html`

The sample data is intentionally ignored by Git, so it stays local unless we intentionally publish or archive it.

## What Not To Do Next

Do not start by rewriting the whole project.

Do not start by adding Cloudflare, Google Drive, or Vertex AI yet.

Do not normalize all folder names yet, even though some folder names have trailing spaces. That should be done as a documented cleanup step because it changes paths throughout the project.

## Best Next Step

Phase 2 should make the original project minimally runnable and clearer without changing its character.

Recommended next repairs:

1. Confirm the Phase 2 runner works on the local machine.
2. Decide whether to install PixPlot locally or defer heavy clustering to a separate environment.
3. Add manual-mixing support so subjective images can be included before PixPlot.
4. Add a fuller browser interface after the command-line wrapper is reliable.
5. Document each repair in `PROJECT_MEMORY.md`.

## Future Product Direction

After the original project is readable and minimally runnable, evolve toward the custom living atlas:

- browser-based import and review
- Google Drive import
- visual and semantic clustering
- human recuration
- notes and narrative sequences
- private studio access
- public selected constellations

The guiding principle is: keep the cultural method visible while making the system easier to use.
