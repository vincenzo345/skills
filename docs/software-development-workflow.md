# Software development workflow

Status: proposed workflow for the v2 skills. Use it on a bounded application task, record what causes rework, and revise the route before adding more skills. The [v2 pilot](v2-workflow-pilot.md) records the earlier experiment; this document describes the intended day-to-day route.

The [workflow gap log](workflow-gap-log.md) captures decisions and deferred implementation work while the stage handoffs are being designed.

## How to use this workflow

Start with the work in front of you, then take only the stages that reduce a real risk or answer an open question. A small, understood fix can move from diagnosis to build and verification. A new application needs the full route. At each stage, preserve enough evidence that the next person or agent can tell what was decided and why.

```text
Request or incident
  → frame the problem → discover → design → plan → build → verify
  → release → observe and learn
          ↑                       ↖ new request or failure
          └──── unresolved question
```

For a repo using these skills, run [`setup-repo`](../skills/engineering/setup-repo/SKILL.md) once to configure the issue tracker and domain documentation. It does not establish the target application's CI, deployment, or monitoring; assess those in the readiness stage below.

## Stage handoffs

An exit check is a question to answer, not a demand for a document on every change. Keep an answer in the issue, spec, pull request, or repo document where the next stage can find it.

| Stage | Enter when | Output and exit check | Current route |
| --- | --- | --- | --- |
| 0. Establish readiness | Starting an application or entering an unfamiliar repo | Identify how to run and test it, the issue tracker, required CI checks, deployment path, rollback or recovery method, and how a released revision is observed. Are missing checks visible as work? | [`setup-repo`](../skills/engineering/setup-repo/SKILL.md) covers tracker and domain-doc setup. Application readiness is a gap. |
| 1. Frame | A request, idea, meeting, or incident arrives | State the affected user, problem, desired outcome, constraints, and what evidence would show success. Is the request in scope? | [`to-record`](../skills/engineering/to-record/SKILL.md) and [`to-scope`](../skills/engineering/to-scope/SKILL.md) for meeting evidence; [`triage`](../skills/engineering/triage/SKILL.md) for incoming issues; [`grill-with-docs`](../skills/engineering/grill-with-docs/SKILL.md) for unresolved decisions. |
| 2. Discover | Facts, behavior, or terminology remain uncertain | Inspect the current system and primary evidence. Record verified facts, open questions, and the independent acceptance check. Can the problem be reproduced or the desired outcome observed? | [`research`](../skills/engineering/research/SKILL.md), [`domain-modeling`](../skills/engineering/domain-modeling/SKILL.md), [`diagnosing-bugs`](../skills/engineering/diagnosing-bugs/SKILL.md). Use [`wayfinder`](../skills/engineering/wayfinder/SKILL.md) when the decision path spans sessions. |
| 3. Design | More than one credible solution remains, or a system relationship changes | Choose responsibilities, interfaces, data flow, and failure behavior. Update the architecture views affected by the choice. Record an ADR only for a costly, surprising trade-off. Can someone explain the design and its risks from the evidence? | [`codebase-design`](../skills/engineering/codebase-design/SKILL.md), [`prototype`](../skills/engineering/prototype/SKILL.md), [`domain-modeling`](../skills/engineering/domain-modeling/SKILL.md). Architecture-view maintenance is a gap. |
| 4. Plan | The build is too large to hold as one verified change | Capture behavior, acceptance criteria, scope limits, testing seams, and ordered vertical slices with real dependencies. Can each slice be verified independently? | [`to-spec`](../skills/engineering/to-spec/SKILL.md), then [`to-tickets`](../skills/engineering/to-tickets/SKILL.md). A small change can go directly to build. |
| 5. Build | The next bounded slice is understood | Implement the behavior and keep local checks green. Update tests, architecture views, and operational instructions when the change affects them. Does the slice meet its acceptance criteria in a representative environment? | [`implement`](../skills/engineering/implement/SKILL.md), [`tdd`](../skills/engineering/tdd/SKILL.md); [`implement-spec`](../skills/engineering/implement-spec/SKILL.md) for a whole ticket graph. |
| 6. Verify | A change is ready for independent scrutiny | Run required CI and a relevant acceptance check; review the diff against the request, repo standards, and changed system relationships. Are failures resolved and remaining risks explicit? | [`code-review`](../skills/engineering/code-review/SKILL.md), [`pr`](../skills/engineering/pr/SKILL.md). |
| 7. Release | A reviewed revision is ready for users | Identify the revision, release path, data changes, recovery action, and post-release check. Verify the deployed revision and the user-visible behavior. Can the team detect and respond if it fails? | A release-verification skill is a gap; the application must supply its own deployment and CI commands. |
| 8. Observe and learn | The revision is in use or a failure arrives | Check the expected outcome and signals, capture defects as issues, diagnose failures, and improve one weak check or instruction exposed by the work. Is the outcome known, or is follow-up assigned? | [`triage`](../skills/engineering/triage/SKILL.md), [`diagnosing-bugs`](../skills/engineering/diagnosing-bugs/SKILL.md), [`retro`](../skills/engineering/retro/SKILL.md). |

Apply security, privacy, accessibility, performance, and migration checks when the change exposes those risks. Put the relevant check in the acceptance criteria and verify it before release. Do not add a ceremonial stage with no risk to resolve.

## Common routes

- **Small feature:** frame → check the affected design → build → verify → release → observe. Use a spec or tickets only if the change will span sessions or needs coordination.
- **New application:** establish readiness → frame and discover → draw the system context and container views → design and prototype uncertain behavior → spec and vertical slices → build → verify → release → observe.
- **Bug or incident:** capture symptom and impact → reproduce and diagnose → design only if the fix changes a seam or system relationship → build a regression check → verify → release → observe → retro.
- **Large uncertain effort:** use `wayfinder` to resolve decision tickets, then convert settled decisions into a spec and build slices. A decision ticket answers a question; an implementation issue delivers behavior.

## Architecture views

An architecture view is a diagram with a stated question, scope, and audience. It communicates relationships that are hard to recover quickly from code alone. Use the [C4 model](https://c4model.com/diagrams) as a small vocabulary for choosing a view, not as a requirement to draw every level.

| View | Question it answers | When to maintain it |
| --- | --- | --- |
| **System context** | Who uses this application, and which external systems does it exchange information with? | Keep one for each application. Start with the proposed relationships in a new project, then correct it against the built system. |
| **Container** | Which applications and data stores make up this system, what does each own, and how do they communicate? | Add for the application and update when these running parts, data ownership, or their relationships change. In C4, a container means an application or data store, not specifically a Docker container. |
| **Focused component, dynamic, or deployment view** | How is one complex part divided, how does one scenario unfold, or where does it run? | Create only when that question cannot be answered clearly by the existing views. Avoid a permanent code-level diagram unless it remains useful and maintainable. |

The C4 guidance recommends context and container views for teams and treats more detailed views as optional. A [container diagram](https://c4model.com/diagrams/container) shows the system's applications and data stores, their responsibilities, major technology choices, and communication. A [deployment diagram](https://c4model.com/diagrams/deployment) answers a different question: where instances run in a particular environment.

### Draw and maintain a view

1. **Name the question.** Choose the audience and one system or scenario in scope. For example, "Where does an order go after checkout?"
2. **Collect evidence.** Inspect the repo, runtime configuration, infrastructure definitions, and existing docs. Ask a person who knows the system about ownership and behavior the code cannot establish. Mark uncertain relationships as unverified.
3. **Sketch the smallest useful view.** A whiteboard is fine for exploration. Draw people, systems, applications, or data stores at one level of detail. Put the system boundary around what the team owns.
4. **Label every arrow.** Show its direction and the action or data exchanged, such as "sends checkout request". Include a title, scope, and key. For a container view, note important technologies or protocols. Use the [C4 review checklist](https://c4model.com/diagrams/checklist) to check readability.
5. **Walk a real scenario through it.** Check the arrows against code and deployment evidence with someone responsible for the system. Correct the drawing where it disagrees with reality; record any unresolved question separately.
6. **Store and review it with the project.** Keep an editable source in version control. Choose a tool the team can edit and render reliably; the [C4 tooling guide](https://c4model.com/tooling) covers whiteboards, visual editors, and diagrams or models as code. Review a view in the same change that alters a relationship it describes.

For example, a shop's context view can show **Customer → Shop → Payment provider**. Its container view opens the Shop boundary and shows **Browser app → Backend app → Orders database**, with the backend calling the external payment provider. The labels should say what each interaction does, not merely "uses".

## Skill skeleton to iterate on

The existing skills already cover interviewing, domain language, module design, prototyping, planning, implementation, review, and retrospectives. Start by routing them through the stages above. The following are **proposed skills**, not installed commands. Add one only after a pilot shows that a repeatable procedure is missing; a project-specific command belongs in the application's tooling instead.

| Proposed skill | Trigger | Minimum procedure | Output and completion test |
| --- | --- | --- | --- |
| `project-readiness` | New application or unfamiliar repo before the first build | Inspect local run commands, checks, CI, deployment, recovery, and observable signals; identify missing capabilities and assign owners. | Short readiness record with working commands and explicit gaps. A fresh contributor can run checks and explain how a revision reaches users. |
| `architecture-views` | New application, changed system relationship, or a design question the existing views cannot answer | Choose the view from its question; gather evidence; sketch; label and review relationships; save editable source; link it from the relevant project docs. | Reviewed view that answers its stated question, agrees with known behavior, and marks unresolved claims. |
| `release-verify` | Reviewed revision is approved for a target environment | Identify revision and change risk; check migration and recovery steps; execute the application's release procedure; confirm deployed revision, acceptance behavior, and relevant signals; record result. | Release evidence tied to the revision, including what was checked and any follow-up. |

The first pilot should use the workflow without creating these skills. Run one bounded task with an independent acceptance check, and record correctness, rework, elapsed time, token use, and human interruptions, as the [v2 pilot](v2-workflow-pilot.md) proposes. If the same gap recurs, turn the relevant row into a skill with examples and an outcome check. Keep [`guide-me`](../skills/engineering/guide-me/SKILL.md) as the router when a proposed skill is eventually promoted.
