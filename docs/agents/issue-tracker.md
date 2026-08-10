# Issue tracker: Local Markdown

Issues, specs, and wayfinder maps for this repo live as markdown files in `.scratch/`.

`.scratch/` is gitignored — planning for this pack is deliberately kept out of the
public repo. If you want a map published, move it out of `.scratch/` by hand.

## Conventions

- One effort or feature per directory: `.scratch/<slug>/`
- The spec is `.scratch/<slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<slug>/issues/<NN>-<slug>.md`,
  numbered from `01` — never a single combined tickets file
- Triage state is recorded as a `Status:` line near the top of each issue file
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<slug>/`, creating the directory if needed.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the
issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` — the Destination / Notes / Decisions-so-far /
  Not-yet-specified / Out-of-scope body.
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with
  the question in the body. A `Type:` line records the ticket type
  (`research` / `prototype` / `grilling` / `task`); a `Status:` line records
  `open` / `claimed` / `resolved`.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when
  every file it lists is `resolved`.
- **Frontier**: scan `.scratch/<effort>/issues/` for files that are open, unblocked,
  and unclaimed; lowest number wins.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under an `## Answer` heading, set `Status: resolved`,
  then append a context pointer (gist plus link) to the map's Decisions-so-far in `map.md`.

## Referring to tickets

Refer to a map or ticket by its **title**, never by a bare number. The number rides
inside the link; it never stands in for the name.
