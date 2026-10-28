# T2 retained source and project knowledge

[t2-case.bundle](t2-case.bundle) is a complete-history Git bundle of the isolated synthetic fixture. It retains the accepted module document, current knowledge index, requested human-readable answer, approved plan/history, maintained checks and reusable fixture on fixture `main`, plus the prototype source on its separate branch. It contains no raw browser profile, temporary output, diagnostic or recovery note.

| Reference | Commit |
| --- | --- |
| Fixture main after reviewer feedback and blocked-recovery recording | `b505846252ab077cbb5677f97741ffd8b327a561` |
| `prototype/case-reopen-20261028-e41` | `34c3687831eaf0aaef9326f34e70c0b9b39aea37` |

Bundle SHA-256: `062c1cfde3aec45becffa7d78139f03e447fff4940adfa9e339af71c08c9b32f` (21,143 bytes). Native `git bundle verify` reports complete history with no prerequisites; the controller independently verified the bundle and references.

To inspect it, restore into an owned temporary review location:

```powershell
git clone --branch main <path-to-t2-case.bundle> <owned-review-folder>
git -C <owned-review-folder> show 34c3687831eaf0aaef9326f34e70c0b9b39aea37:src/case-lifecycle.prototype.html | Set-Content -Encoding utf8 <owned-review-folder>/review.prototype.html
```

Open the extracted HTML and use its close/reopen walkthroughs. The pure lifecycle module is the first script block; the second owns only demonstration state and presentation. Current knowledge is at `docs/modules/case-lifecycle.md`, evidence and the requested answer at `work/case-reopen/discovery.md`. The maintained syntax check and three identity tests use only Python's standard library. Fixture-specific installed-helper paths are historical evaluation addresses; standalone prototype review does not require those helpers or repository setup.

The accepted conclusion is delegated synthetic-fixture design, not real product acceptance or Python production implementation. The [evaluation](../validation.md#t2-bounded-designprototype-and-recovery-incomplete-cleanup) records the exact unresolved cleanup. Retained source and knowledge do not establish a cleanup pass.
