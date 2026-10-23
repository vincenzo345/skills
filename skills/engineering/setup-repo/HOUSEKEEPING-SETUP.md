# Configure housekeeping

Read during /setup-repo. Configure the convention once; ordinary tasks consume the baseline below without repeating setup discovery.

1. Read existing agent instructions, ignore rules and verification commands. Reuse an established temporary workspace when it separates disposable task files from maintained work. Otherwise propose `.scratch/agent-tmp/`, or a collision-free alternative. Preserve legacy scratch records and user content; ignore only the dedicated disposable subtree. Create task directories when used.
2. Include the chosen root, the baseline below and the adapted [housekeeping reference](housekeeping.md) with its [service branch](housekeeping-services.md) in the setup draft. Resolve `{{TEMP_ROOT}}` to the chosen repo-relative path. Keep the reference at `docs/agents/housekeeping.md` unless the repo already has an authoritative location; adjust the baseline pointer accordingly. Publish the service branch beside it and preserve their relative links. Preserve user edits on reruns and update existing sections instead of appending copies.
3. Write only the approved setup. Ensure the selected agent instruction file is actually loaded in the current environment, directly or through an existing pointer. If it is not, explain the gap and include the smallest pointer correction in the reviewed draft. Keep one policy source rather than duplicating the baseline across instruction files.
4. Check that the temporary root and reference agree, the narrow ignore rule covers disposable task contents, and durable records stay visible. Tell the user the chosen location and the distinction between maintained checks and one-off validation. Setup is complete when these agree and both references are reachable.

## Persistent baseline

Copy this block into the existing agent instructions, replacing the placeholder and preserving equivalent user guidance. Its core obligations remain inline; the reference is conditional.

```markdown
### Housekeeping

Reuse existing checks. Keep useful lint rules and regression tests in maintained tooling; classify one-off validation and generated output separately. Before creating disposable files or services, choose their owner, lifetime and cleanup. Put one-off files in `{{TEMP_ROOT}}/<task-id>/` with a unique task ID. For temporary placement, retention ambiguity or resources that can survive interruption, read `docs/agents/housekeeping.md` once when needed.

Clean your no-longer-needed disposable resources before completion, including after failed checks. Preserve requested deliverables, shared resources, active tasks and durable records. Verify ownership and resolved path boundaries; names, age and ignore rules are not deletion authority. Retain useful failure evidence only with its purpose and revisit condition. Report unresolved cleanup or intentional leftovers briefly. Ordinary edits without disposable resources need no housekeeping inventory, recovery note or extra report.
```
