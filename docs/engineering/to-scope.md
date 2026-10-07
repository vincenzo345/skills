## What it does

`to-scope` turns a normalized meeting record into a provisional scope tree. It tests coverage and conflicts, lets the builder resolve build-boundary questions, and takes the remaining workflow back to the expert for correction and sign-off.

## When to use it

Invoke `/to-scope` after `/to-record` when an expert owns the process and a builder owns the slice to build. It resumes from existing scope artifacts across sessions. Keep the high-level problem statement distinct from the source transcript and the expert-corrected scope.

The result feeds `grill-with-docs` for any remaining design decisions, or `to-spec` once the solution is sufficiently settled.

## Source

Ported from Skillsrepo's earlier `to-scope` implementation for the v2 workflow.
