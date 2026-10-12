# Workflow gap log

This is the working list for refining the [software development workflow](software-development-workflow.md). A recorded requirement is not an implemented capability. Finish the stage-by-stage output and handoff design before starting the separate CI/CD implementation workstream. Add evidence and a concrete acceptance check before promoting any item to a build ticket.

## Agreed rules

| ID | Rule | Record or handoff consequence |
| --- | --- | --- |
| R-01 | Use **stage** for a development workflow step and **phase** for a chunk of work within one agent session. | A stage transition passes durable evidence; `/handoff` remains for moving work to another harness, directory, or person. |
| R-02 | Give each nontrivial change one indexed work record in the configured issue tracker or its local Markdown equivalent. | Link the spec, tickets, diagrams, ADRs, PR, and release evidence from that record. Keep system facts in their durable project documents. |
| R-03 | At a stage transition, record the outcome, evidence or links, unresolved questions, next action, and owner. | The next stage can start from the record without reconstructing the previous conversation. |
| R-04 | In an application repo, maintain `docs/development.md` for local run, test, and CI commands and `docs/operations.md` for release, recovery, and observability. Link both from the root README. | Initial readiness verifies the commands and records gaps. Recheck when a path changes materially or a new contributor cannot follow it. |
| R-05 | Require a working local run and verification path before feature implementation. Require working CI, release, recovery, and observation paths before the first production release. | Missing capabilities are tracked as blocking work with owners, according to the gate they block. |
| R-06 | A push or PR should run applicable checks and a CI/CD coverage check. Select templates only for capabilities the application actually has. | Store the selected capabilities and reasons in a versioned CI policy file. An image build or deployment can require Docker checks; local Docker use alone does not. |
| R-07 | A PR that adds or removes a capability updates the CI policy and applicable templates in the same change. | The coverage check blocks merge when the capability and CI configuration disagree. |
| R-08 | Preserve the information from every requirements or discovery meeting, including later meetings that revise understanding or scope. | Do not overwrite an earlier meeting record when a new one is added. Link later evidence to the affected work record and scope revision. The durable archive location is still open. |
| R-09 | Merge framing and discovery into the first development stage. | The stage investigates the problem, requirements, current behavior, and success criteria before design. Open-question handling remains to be defined. |
| R-10 | Keep an indexed, durable private archive of each meeting's available original material, normalized transcript, attachments, and provenance. | `.scratch/` remains a working location and cannot be the only preserved copy. The concrete archive location and links remain to be chosen. |
| R-11 | Carry known unknowns forward with a statement, impact, owner, resolution method, and latest safe resolution point. | An unknown blocks the work that depends on its answer, not unrelated work. |
| R-12 | An affected feature may enter design or a prototype with an open requirement, but it cannot cross a signed `to-scope` handover or enter its build spec until that requirement is answered or explicitly out of build. | Unaffected features can continue. |
| R-13 | Add each later meeting as a new source record. Update the living scope tree, create a new signed handover snapshot for a changed feature, and check affected downstream specs and tickets. | Keep earlier snapshots and pause only work whose assumptions changed. Later meetings carry more weight, but the exact conflict-resolution rule is still open. |
| R-14 | Default to a project-configured, access-controlled meeting archive outside the source repo, with one folder per meeting for all available original material, normalized transcript, attachments, and provenance. | The indexed work record holds stable archive links. `.scratch/` remains a working copy. |

## Open design and implementation items

| ID | Stage | Gap or question | Next design output | Timing |
| --- | --- | --- | --- | --- |
| G-01 | All | The workflow lists stage outcomes but has no exact record update rule, file location, or owner for each stage. | Complete the stage-by-stage record and handoff map, including create versus update rules. | Current design work |
| G-02 | 0 | `setup-repo` configures agent records, but no skill verifies application run, CI, release, recovery, and observation paths or maintains the two guides. | Define `project-readiness` inputs, verification steps, output, and exit check. | After stage design and a pilot |
| G-03 | 0 and 6 | No application capability policy or deterministic check currently compares capabilities with selected CI/CD jobs on pushes and PRs. | Specify policy schema, evidence rules, event and branch coverage, required status check, and mismatch reporting. | Separate CI/CD workstream |
| G-04 | 0 and 6 | The reusable CI/CD template catalog and selection rules are not designed. | Draft a capability-to-template matrix and test it against real application repos. Candidate families: language checks, image build, database migration, deployment, and post-release verification. Add a template only after its trigger and acceptance check are clear. | Separate CI/CD workstream, after G-03 |
| G-05 | 3 and 5 | Architecture views have a drawing procedure but no skill or application record convention for creating and updating them. | Define source location, review owner, and change triggers for context and container views. | After stage design and a pilot |
| G-06 | 7 | No skill owns release evidence tied to the deployed revision. | Define `release-verify` input, record, recovery check, and post-release acceptance check. | After stage design and a pilot |
| G-07 | 8 | `retro` improves the agent environment; it does not own observation of product outcomes or operational signals. | Identify the outcome record and who checks it after release. | Current stage design work |
| G-08 | Routing | `guide-me` currently ends the main route at review and retro, while the proposed workflow adds readiness, architecture maintenance, release, and observation. | Reconcile the router when the workflow and any promoted skills are finalized. | Later, with router or skill changes |
| G-09 | Pilot | The workflow has not been tested end to end on a bounded application task. | Capture correctness, rework, elapsed time, token use, human interruptions, and which records were useful at each handoff. | Before expanding the skill set |
| G-10 | 1 and 2 | The draft still separates framing from discovery, contrary to the agreed first-stage boundary. | Revise stage names, numbering, outputs, and skill routes after the stage design is settled. | Current stage design work |
| G-11 | 1 | `to-record` writes normalized transcripts beside raw exports under gitignored `.scratch/`; this working location alone cannot guarantee future review across machines. | Choose a durable private archive convention and stable links for all available meeting material. | Current stage design work |
| G-12 | 1 and later | The later-meeting revision rule is agreed, but the exact archive index, scope revision link, and downstream impact record are unspecified. | Define the file and link convention that implements R-13. | Current stage design work |
| G-13 | 1 and later | The unknowns rule is agreed, but the work record has no defined fields or statuses for it. | Define the unknown register format and how its resolution gate is checked at each stage. | Current stage design work |
| G-14 | 1 and later | Later meetings should carry more weight than earlier ones, but a later statement may be unclear, come from a different authority, or conflict with a signed scope snapshot. | Define when a later statement supersedes an earlier one, how conflicts remain visible, who resolves each kind, and what downstream work pauses. | Current stage design work |

## CI/CD template strategy to evaluate later

1. Inspect a real application and its delivery path before choosing templates. Separate capabilities that can be detected from files from choices that need an explicit declaration in the CI policy.
2. Start with a small core check for application build and test commands plus policy consistency. Add conditional templates only when their capability exists. For example, an image build check applies when an image is built or deployed, not just when Docker is used to start a local database.
3. Decide whether each template is copied into an application or called as a reusable workflow. GitHub supports [workflow templates and reusable workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations); the latter centralize repeatable logic, while applications still need a caller and project-specific inputs.
4. Test the policy and each template in a pilot repo. Check push and PR events, branch coverage, permission scope, job names, required status checks, and the failure message. GitHub's [protected branch guidance](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) explains how required checks can block merge.
5. Roll out one template family at a time. An [image publishing workflow](https://docs.github.com/en/actions/tutorials/publish-packages/publish-docker-images) is a candidate only for applications that publish images; its build and provenance steps should be evaluated against that application's registry and release path.

Do not treat this strategy as a template implementation or as proof that any application is ready to release. The actual application commands and release evidence decide that.
