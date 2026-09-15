# UI Prototype

Generate several radically different UI variants in a production-excluded prototype surface. The user compares them, combines useful ideas, and keeps the decision rather than shipping the prototype.

If the question is about logic or state rather than appearance, use [LOGIC.md](LOGIC.md).

## Isolation first

Use the repository's approved story, preview, playground, or prototype convention when it is excluded from production builds and deployments. Otherwise create a clearly named isolated prototype entry point that is not registered as a production route.

Do not modify an existing production page, route table, shared manifest, or deployment configuration to mount variants unless the repository already provides a production-excluded hook or the user explicitly authorizes the integration and understands the cleanup obligation.

Use synthetic fixtures by default. Reproduce real density and states with representative shapes, not production data or credentials. Real read-only data requires explicit authorization and repository policy support; real mutations are outside a UI prototype.

## Process

### 1. State the question and pick variants

Write down the visual decision the prototype must answer and its isolation/cleanup boundary. Default to three variants and cap at five.

### 2. Make variants structurally different

Vary information hierarchy, layout, and primary affordance—not only color or copy. Use the project's component and styling system when that can be imported without coupling the prototype into production registration.

Name variants clearly, such as `VariantA`, `VariantB`, and `VariantC`. Use fixture cases that show empty, typical, dense, error, and permission states relevant to the question.

### 3. Add a local switcher

Use a query parameter or prototype-local control so variants are shareable and reload-stable. The switcher must be visibly outside the proposed design and must exist only inside the isolated prototype surface.

Support previous/next controls and keyboard navigation without intercepting input, textarea, or editable-element keystrokes. Render the current variant name and the representative fixture being viewed.

### 4. Hand it over

Provide one local run command and the prototype URL or entry point. State that the surface is synthetic and production-excluded. Let the user compare variants and request combinations.

### 5. Capture the decision and clean up

Record the winning behavior, why it won, which fixture states were considered, and the prototype's limitations. Carry that decision into the source spec. Reimplement it through the production ticket, TDD, and review flow.

Retain the prototype only in an authorized evidence location or branch. Remove any temporary hook, switcher, or shared configuration before reporting cleanup complete.

## Anti-patterns

- variants that differ only in color or copy;
- sharing so much structure that alternatives cannot diverge;
- real credentials, production data, or real mutations;
- relying on a runtime-only environment check as the sole production-exclusion boundary;
- counting prototype execution as implementation or acceptance proof;
- promoting prototype code directly into a production route.
