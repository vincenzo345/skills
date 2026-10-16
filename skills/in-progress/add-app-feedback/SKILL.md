---
name: add-app-feedback
description: Install an in-app bug report and enhancement request flow that creates private GitHub issues for triage. User-invoked.
disable-model-invocation: true
---

# Add App Feedback

Install a working feedback flow in an existing web app. Adapt to its UI, auth, server, configuration, and test conventions. A successful installation lets a signed-in user submit a bug or enhancement request and creates a private GitHub issue labelled for the project's existing triage workflow.

Read [ISSUE-CONTRACT.md](ISSUE-CONTRACT.md) before implementing the endpoint or issue body. It holds the report shape, GitHub contract, and failure behavior.

## 1. Inspect and propose

Read the target app, not just its framework name. Locate its signed-in navigation, forms, session lookup, server-side routes, CSRF and rate-limit mechanisms, release and trace identifiers, tests, and deployment secret store. Read `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md`. If the project lacks them, tell the maintainer to run `/setup-repo` first. If the app has no authenticated server path or no trusted way to reach the reporter, identify that blocker before adding UI.

Propose the UI entry point, server route, safe diagnostic fields, and issue destination. Confirm that the GitHub issue repository is private, and that it matches the repository `/triage` will query. A public code repository can use a separate private issues repository. For that case, update `docs/agents/issue-tracker.md` to name the private `owner/repo` explicitly; make every issue command and API path use it. Keep code PR discovery on the code repository or leave the PR request-surface flag off. Resolve the canonical `needs-triage`, `bug`, and `enhancement` roles through `docs/agents/triage-labels.md`; verify that those mapped label strings exist in the destination, and create missing labels if the maintainer authorizes tracker setup.

Find a private security-reporting route in `SECURITY.md` or confirm another maintainer-controlled address or URL. The form points possible vulnerability reports there. A missing route is a setup blocker, not a reason to send them to ordinary issues.

For production, recommend a GitHub App installed only on the issue repository with Issues write permission. Generate short-lived installation tokens on the server. A fine-grained personal access token restricted to that repository and Issues write permission is an explicit small-project shortcut. Show the required server-side secret names and deployment steps, but never request a secret in chat or write it into the repo.

## 2. Install

Add a discoverable **Report a bug / Request an enhancement** entry point, structured form, authenticated server endpoint, and server-side GitHub submission code. Use the app's existing components, transport, and deployment configuration. Capture the page where the user opened feedback before navigating to a form; do not substitute the form route for the affected page. Keep a reviewable diagnostic snapshot visible before submission, and send only the fields the user opted to include. Derive reporter ID and contact email from the server session; show a notice that the email goes into a private issue for follow-up. Treat all text and diagnostic fields as untrusted data, including existing telemetry output.

Use the app's established CSRF defense for cookie-authenticated writes, bound request size and field lengths, and apply a per-account submission rate limit. If the app lacks a suitable rate limiter, add the smallest production-appropriate mechanism for its deployment topology; a process-local counter is insufficient for a multi-instance app. Keep repository, labels, and credentials server-controlled. Require a private destination at configuration time and fail closed if visibility cannot be verified. Keep the GitHub token and private key out of browser bundles and routine logs.

Submit synchronously. Return a receipt with an opaque submission reference only after GitHub confirms issue creation. Preserve entered form data on failures. Distinguish invalid input, authentication, rate limiting, GitHub rejection, and an uncertain timeout after sending the request. Disable duplicate clicks while in flight. Do not claim exactly-once delivery or automatically retry an uncertain create request.

Install only this feedback path. The existing `/triage` skill remains responsible for verifying incoming issues, contacting the reporter when necessary, writing the agent brief, and applying `ready-for-agent`. Do not install an automatic agent runner or a user-facing status sync.

## 3. Verify and hand off

Run the app's relevant checks and exercise both report types and the failure paths with a stubbed GitHub API. Check that the built client contains no tracker credential. Verify the issue body, category and state labels, privacy guard, affected-page capture, diagnostic opt-out, consent notice, and receipt timing. Test a timeout separately from a confirmed rejection, and test a `201 Created` response with missing labels. If a live test is appropriate, ask before creating a test issue in the private repository, then report its URL to the maintainer.

Document the UI entry point, deployment secrets, private destination, security route, rate-limit mechanism, and how a maintainer runs `/triage` on app-origin issues. For `needs-info`, use the issue's private contact email; a GitHub comment alone will not reach an app user without repository access. Finish only when the installed flow works in the target app or a named external prerequisite prevents live verification.

## Scope

V1 targets signed-in web apps and private GitHub Issues. Jira is a future provider: its adapter must accept the same normalized report and return a private issue identifier and URL, while discovering project-specific required fields. Do not add a speculative Jira client or provider abstraction to the GitHub installation. Attachments, anonymous intake, mobile clients, user status pages, durable queues, and automatic agent dispatch are later work.
