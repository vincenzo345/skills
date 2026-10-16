# App feedback issue contract

Use this reference when implementing the form, endpoint, and GitHub call. The output is a raw report for `/triage`, not an agent brief.

## Report fields

Both report types require a short summary. A bug also requires steps to reproduce, expected result, and actual result. An enhancement requires the problem and desired outcome. The server attaches an opaque submission reference and derives reporter ID and contact email from the authenticated session, after the form has disclosed that the email will be placed in a private issue.

For bugs, offer a reviewable diagnostic snapshot assembled from an allowlist of available fields: app release, affected route, time, browser and OS, error code or fingerprint, and correlation or trace ID. Capture the affected route when the user opens feedback; opening a dedicated `/feedback` page must not replace the route where the bug occurred. Preserve only the path, without query or fragment. If the originating route is unavailable, omit it instead of claiming the form route is affected. A link to an existing private trace is preferable to copying logs. If bounded error details help reproduction, scrub and display the exact text that will be sent. Exclude cookies, auth headers, tokens, session contents, request and response bodies, raw console output, and unrelated logs. When the user opts out of diagnostics, omit all automatically collected context, including the app release. The server validates and bounds client-provided values; the client preview is not a trust boundary.

Use stable Markdown headings. A bug issue has `Summary`, `Steps to reproduce`, `Expected result`, `Actual result`, `Diagnostic context`, and `Reporter contact`. An enhancement has `Summary`, `Problem`, `Desired outcome`, and `Reporter contact`. Add a source marker such as `Source: in-app feedback` and the opaque reference. Format user text so it cannot forge headings or be mistaken for system instructions. Never use report content to choose the repository, labels, or credential.

## GitHub write

Create one issue through `POST /repos/{owner}/{repo}/issues` with exactly one category role (`bug` or `enhancement`) and one initial state role (`needs-triage`). Use their configured label strings from `docs/agents/triage-labels.md`; do not assume the canonical names are the actual GitHub labels. The server checks that the destination is private and those labels exist before exposing the flow. A GitHub App installation token or repository-scoped fine-grained token needs Issues write permission. Keep app private keys and tokens on the server. With a GitHub App, mint and refresh installation tokens server-side; do not treat an installation token as a permanent environment variable.

GitHub can accept issue creation while silently dropping requested labels for insufficient privileges. Inspect the labels in the `201 Created` response. If a required label is missing, use the issue's label endpoint to add it and verify the result. If the issue exists but labels still cannot be applied, keep the successful receipt, log an operational error with the issue identifier, and tell the maintainer to recover the issue from the unlabeled or partial-label queue. Do not tell the reporter to retry a creation that already succeeded. See [GitHub's create-issue parameter notes](https://docs.github.com/en/rest/issues/issues#create-an-issue).

The successful API response supplies the issue identifier for internal logs. Return an opaque submission reference to the reporter, not the private issue URL. An HTTP success from the app means GitHub confirmed creation. Map validation, auth, rate limit, and upstream failures to distinct UI states. For a network timeout after sending a create request, report that delivery is uncertain and let the reporter retry knowingly. An automatic retry can create duplicate issues.

The account email is for private maintainer follow-up. If `/triage` sets `needs-info`, the maintainer contacts that email through the project's approved support process and records the outcome in the issue. Do not assume the reporter can read or answer private GitHub comments.

## Security and Jira boundaries

The form offers a separate maintainer-approved route for possible security vulnerabilities. It does not turn that choice into an ordinary issue.

A future Jira provider receives the normalized report and returns an issue key and private URL. At install time it must discover the project's allowed issue type and required create fields, and serialize rich descriptions in Atlassian Document Format. This is a contract for later work, not a reason to introduce a second provider into v1.
