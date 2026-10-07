## What it does

`to-record` turns a raw expert/builder meeting export into a normalized transcript while preserving every word. It flags attribution and record defects without interpreting the underlying workflow.

## When to use it

Invoke `/to-record` when a meeting export is the evidence for requirements. The first question establishes whether you were in the room; the skill then normalizes and verifies the record. Its preservation checker lives with the skill.

Pass the normalized file and unresolved flags to `/to-scope`. If requirements came from another source, use a suitable discovery method instead.

## Source

Ported from Skillsrepo's earlier `to-record` implementation for the v2 workflow.
