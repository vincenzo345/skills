# Add in-app feedback to a project

Status: beta skill implemented and forward-tested on two local web app fixtures. Live GitHub delivery remains unverified without a private test repository and credentials.

## Outcome

Build a user-invoked beta skill, provisionally `/add-app-feedback`, under `skills/in-progress/`. When run in a web app repository, it installs a working bug-report and enhancement-request flow that creates private GitHub issues. Each incoming issue enters the existing `needs-triage` workflow. A maintainer uses `/triage` to verify the report and prepare an agent brief before moving it to `ready-for-agent`.

This skill is separate from `/setup-repo`. `/setup-repo` remains the run-once source of truth for the issue tracker and triage labels. `/add-app-feedback` reads that configuration and checks that the app's feedback destination matches it. The skill starts in the beta bucket because this repo's [scope policy](../../SCOPE.md) normally rejects new catalog skills. Promotion requires a deliberate review of real installations and maintenance cost.

## Scope and prerequisites

- V1 supports web apps with an existing server-side request path and signed-in users. It adapts to the project's UI framework, authentication, server, configuration, and test conventions. If it cannot establish a safe server path, it reports the missing prerequisite and stops before adding a broken form.
- V1 creates GitHub Issues. It documents a provider contract for Jira but does not implement or advertise a first-class Jira integration. Jira issue creation needs project-specific create-field metadata and Atlassian Document Format for rich descriptions ([Jira create issue API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/), [REST v3 introduction](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro)).
- The issue destination must be private. A private application repository may be used directly. A public application repository requires a separate private issues repository. GitHub repository visibility controls who can read its contents and issues ([repository visibility](https://docs.github.com/en/repositories/creating-and-managing-repositories/about-repositories)).
- The destination named by the app must also be the destination used by `docs/agents/issue-tracker.md` and `/triage`. If it differs from the git remote, the installer must record the explicit `owner/repo` and use it in tracker operations. The existing GitHub seed template currently infers the remote, so this case needs a small setup and triage compatibility change.
- The installer checks that `needs-triage`, `bug`, and `enhancement` labels exist or creates them when authorized. `/setup-repo` currently provisions the state labels but does not map the two category labels used by `/triage`; resolve that gap as part of implementation.
- A separate private security-reporting destination must be configured before the form presents a security link. Reuse an existing `SECURITY.md` route when appropriate, or collect a maintainer-approved contact URL or address. Security reports do not become ordinary feedback issues. GitHub supports private vulnerability reporting for eligible repositories ([GitHub security reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities)).

## Install flow

1. Inspect the app's navigation, form conventions, auth/session handling, server routes, configuration, existing telemetry, tests, and current issue-tracker configuration. Show the proposed insertion point and diagnostic fields before editing.
2. Confirm the private destination, security route, and credential path. Recommend a GitHub App with Issues write permission for long-lived production use. Permit a fine-grained token restricted to the selected repository and Issues write permission as an explicit small-project shortcut. Keep all credentials on the server and out of source control and client bundles. GitHub recommends GitHub Apps for long-lived integrations and documents the Issues write requirement for creating issues ([GitHub App guidance](https://docs.github.com/en/apps/creating-github-apps/about-creating-github-apps/deciding-when-to-build-a-github-app), [create issue API](https://docs.github.com/en/rest/issues/issues#create-an-issue)).
3. Install the form, authenticated server endpoint, GitHub submission adapter, configuration example, focused tests, and short maintainer instructions. Reuse the app's existing components and deployment secret mechanism.
4. Verify configuration and run focused tests. Offer a controlled real submission to the private destination after the maintainer authorizes that external write. Record the created test issue and close it with a clear test note if the maintainer wants a clean queue.

## User flow

The entry point offers **Report a bug** and **Request an enhancement**. Both ask for a concise summary. A bug asks for reproduction steps, expected result, and actual result. An enhancement asks for the problem and desired outcome. A visible notice explains that the report and the account's contact email will be sent to the private project tracker so maintainers can request more information.

For bugs, the form displays a reviewable diagnostic snapshot when data exists: affected page or route, release/build identifier, timestamp, browser and OS, correlation or trace ID, and bounded sanitized error details. Capture the affected route when feedback opens, before navigating to a form, and strip query and fragment. Use existing telemetry links when available instead of copying entire logs. Exclude cookies, authorization headers, tokens, session state, request bodies, unrelated logs, and secrets. The user can review the snapshot before submission, and opting out removes all automatically collected context. The server independently validates and bounds every field, including client-provided context. This is a chosen product boundary, informed by OWASP guidance on sensitive logging data ([OWASP logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)).

The server derives reporter identity, contact email, destination, and labels from trusted server configuration or the authenticated session, never from form fields. It checks authorization, CSRF protection where the app uses cookie sessions, input limits, and per-account rate limits. It stores GitHub credentials only server-side ([OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [OWASP rate limiting](https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html)).

The endpoint creates an issue synchronously. It returns a receipt only after GitHub confirms creation. The receipt uses an opaque submission reference and does not expose the private issue URL. A validation or authentication failure preserves the form. A rate-limit or upstream failure gives an actionable retry message. If the request times out after being sent, the UI says the result is uncertain; retrying can rarely create a duplicate, which triage may merge. V1 does not require a local database, durable queue, or status synchronization. Respect GitHub's rate-limit response and retry guidance rather than immediately repeating failed writes ([GitHub rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), [GitHub troubleshooting](https://docs.github.com/en/rest/using-the-rest-api/troubleshooting-the-rest-api)).

## Issue and agent handoff contract

Each issue has exactly one category label, `bug` or `enhancement`, and the `needs-triage` state label. It includes the user's structured account of the problem, the reviewed diagnostic snapshot, the account's contact email, a source marker indicating in-app feedback, and an opaque submission reference. It does not contain an agent brief or `ready-for-agent` label at creation.

Resolve canonical roles through the project's label mapping. Verify labels in GitHub's create response; if they are absent, repair them through the label API. GitHub documents that create requests can succeed while labels are silently dropped for insufficient privileges ([create issue API](https://docs.github.com/en/rest/issues/issues#create-an-issue)). An existing issue with failed labeling is an operational recovery case, not a reason to ask the reporter to submit it again.

The issue body uses stable headings so `/triage` can extract the report without guessing. For example: `Summary`, `Steps to reproduce`, `Expected result`, `Actual result`, `Diagnostic context`, and `Reporter contact` for a bug; `Problem`, `Desired outcome`, and `Reporter contact` for an enhancement. Untrusted text is escaped or formatted safely for Markdown and never treated as instructions to the agent.

`/triage` remains a human-invoked review. It verifies bug claims, checks for duplicates and prior decisions, and writes a durable agent brief with acceptance criteria before applying `ready-for-agent`. For `needs-info` on an app-origin issue, the maintainer uses the contact email rather than expecting the reporter to see a private GitHub comment. The issue records that follow-up occurred without copying sensitive correspondence into a comment. No automatic agent runner is installed.

## Implementation sequence

1. Add the beta skill and its entry in `skills/in-progress/README.md`. Keep it out of the plugin manifest, top-level README, and promoted-skill docs while it is in beta.
2. Reconcile the explicit private feedback repository and category labels with `/setup-repo` and `/triage`, then document the GitHub destination and label contract.
3. Write the skill's inspect, propose, install, and verify instructions, with the GitHub credential and security-route decisions as required setup inputs.
4. Add reusable issue-body and diagnostic-field guidance as skill resources. Keep framework-specific code generated against the target app rather than maintaining a fixed starter package.
5. Exercise the skill in at least two representative web apps with different UI/server conventions, including one public code repository using a separate private issues repository. Refine the skill from observed installation failures before considering promotion.

## Acceptance checks

- In a supported signed-in web app, a user can submit each report type and receive a receipt only after one private issue is confirmed.
- The issue has the correct destination, one category label, `needs-triage`, readable structured sections, reviewed diagnostics, and contact information. It has no `ready-for-agent` label.
- Secrets, raw logs, auth data, and sensitive request bodies are absent from client assets, issues, and routine error logs.
- Missing auth, missing private destination, missing security route, or missing credentials blocks installation or submission with a specific explanation.
- Invalid input, rate limits, GitHub rejection, and uncertain timeouts produce distinct user-visible outcomes; repeated clicks are disabled while a submission is in flight.
- `/triage` can discover and process the app-origin issue even when the issue destination differs from the code repository. It can contact the reporter for `needs-info` and add an agent brief before `ready-for-agent`.
- The generated code follows the target app's patterns and passes its relevant tests and type checks. An authorized real smoke submission verifies credentials and labels.

## Deliberately later

Native mobile and desktop apps, anonymous intake, attachments or screenshots, in-app status tracking or reply threads, durable queues and strict deduplication, semantic duplicate detection, automatic agent dispatch, and a Jira implementation are outside v1. The Jira adapter contract should describe how a provider accepts a normalized feedback submission and returns an issue identifier and private URL, including how required project fields are discovered, without adding unused abstraction to the GitHub implementation.

## Beta validation

The skill was run against isolated Flask and FastAPI fixture apps outside this repository. The first pass exposed two gaps: both apps recorded the feedback form as the affected page, and neither checked labels after GitHub confirmed issue creation. The skill was revised to capture the source page and to verify or repair labels. A diagnostic opt-out rule was also sharpened after the FastAPI app still included its release identifier when the user excluded diagnostics.

The revised Flask fixture passed 17 stubbed tests. The revised FastAPI fixture passed 11 stubbed tests, Python compilation, and client JavaScript syntax checking. These checks cover both report types, authentication and CSRF rejection, private destination and label preflight, mapped labels, affected-page capture, diagnostic opt-out, rate limiting, upstream rejection, uncertain timeout, and a `201 Created` response with missing labels. Neither fixture had credentials or a live private issue repository, so the real GitHub installation, label permissions, and delivery path still need an authorized smoke test in a target project.
