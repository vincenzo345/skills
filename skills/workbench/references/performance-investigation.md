# Performance investigation

Use this method for a slow or regressed user journey. It is self-contained; an external debugging skill is optional, not a prerequisite.

## Establish the comparison before exploring

The first substantive update begins with these five lines, even when values are unknown:

```text
Environment:
Deployed revision:
Journey:
Fixture:
Cache state:
```

Use facts already supplied by the user. Inspect discoverable coordinates; do not ask the user to repeat an answer returned through an interaction tool. Unknown deployed revision, fixture, or cache state does not block an options proposal when the options and their ordering remain conditional.

For an explicit new Workbench item, create the compact routing input and call `prepare-routing.py --capture-and-start` before broad repository discovery. Do not inspect prior Workbench items first. The execution card records the five coordinates and the read-only or mutation boundary.

## Build the smallest decision-changing evidence loop

Trace one end-to-end journey: user action, client request scheduling, edge or gateway routing, server handler, data transfers, expensive work, caches, and the response consumed by the client. First define the user-visible metric precisely—for example time to first usable page, time to all prefetched pages, or interaction readiness. Do not add sequential request durations to an earlier milestone unless the UI actually waits for every request before exposing that milestone. Define a target list before searching and inspect each source once. Batch independent searches and adjacent reads into one tool call.

For a fix request, seek a repeatable baseline at the public seam before changing code. For an options-only request, do not manufacture a reproduction of an unavailable environment or representative customer workload. When the user permits bounded synthetic evidence, an ephemeral generated fixture may measure a narrow local seam; label its shape and exclusions and never generalize it to the deployed workload. Use one bounded measurement family if it can change the option order; otherwise record the smallest missing measurement. Never exercise a deployed application in a read-only investigation when a request can warm caches, enqueue work, increment counters, or create audit records.

Default bounds for one journey are 25 investigative tool calls, two fixtures, three repetitions, and 120 seconds of benchmark time. These are stop signals, not goals. Before each additional call, name the still-open decision it can change; at the bound, stop and synthesize unless that named fact is necessary for correctness. Do not delegate a single shared path; delegate only an independent evidence question whose result avoids more work than coordination costs.

## Calibrate every claim

Keep these classes distinct:

- **Observed fact:** directly read from the named source or runtime.
- **Measurement:** bounded by environment, operation, fixture, sample, and cache state.
- **Inference:** follows from evidence but was not directly observed.
- **Hypothesis:** makes a falsifiable prediction and still needs a discriminating probe.
- **Unknown:** material evidence is unavailable.

Source topology establishes possible paths, not the live path. Configuration defaults are not deployed values without deployment evidence. Opening a file or constructing a parser does not prove all content is eagerly parsed. A library's presence or reputation does not prove it is faster on this workload. Parallel client requests do not prove parallel backend execution. Aggregate telemetry is not route-specific without attribution. A before/after comparison is causal only when the operation, fixture, state, and competing variables are controlled.

Cache vocabulary must name whose first and which lifetime: first view in this browser, first request in this process, or first-ever request for the object. No known prewarmer does not prove a cache is empty; a prior request, external producer, or different deployed revision may have populated it. Carry source-snapshot and deployed-state qualifiers into the final summary instead of shortening them away.

Use `dominant`, `root cause`, `eliminates`, `only`, `guarantees`, or numeric multipliers only when evidence distinguishes all relevant alternatives. Otherwise name the premise and the measurement that would confirm it. Reconcile contradictions before acceptance—for example, an option cannot both depend on cache state and be valuable regardless of cache state.

During final review, compare every exclusive or causal label with all surviving options against the same user-visible milestone. Repository evidence that work exists or is absent establishes a mechanism, not that the mechanism explains the reported slowdown.

## Produce a decision-ready proposal

Rank conditionally when live evidence is missing. Every option includes:

- mechanism and affected seam;
- expected user-visible effect;
- engineering and recurring cost;
- risks and interactions with other options;
- premise that controls its value or sign;
- smallest proof needed before or after implementation.

Separate independent mechanisms instead of bundling them under one rank. Identify the safest reversible experiment and the smallest deployed measurement that would reorder the list. Do not call reproducibility, observability, or dependency hygiene a speed-up unless it directly changes latency.

A proof action must observe the exact branch or mechanism it claims to discriminate. A write-failure counter does not prove a read-cache miss, an aggregate request duration does not isolate rendering, and one warm trace does not eliminate cold-start exposure. If existing telemetry cannot separate the branches, name the smallest instrumentation needed instead of substituting a nearby metric.

Audit temporal causality as well as topology. Work proposed as a prerequisite must finish before the request it is meant to accelerate; work started concurrently cannot turn that same request into a cache hit unless the request is gated on completion. State whether an effect changes the first visible result, the complete prefetched window, or only a later visit.

Match the proposed measurement to its actual resolution. A browser waterfall can show request overlap, response timing, status, and bytes; aggregate function telemetry can show service-wide duration or initialization. Neither identifies an internal cache tier or divides download, parse, raster, and encode time without correlated branch markers or stage timers. Ask only for the minimum extra instrumentation needed to separate the options still in contention.

Keep an options-only artifact concise—normally under 1,500 words—and avoid duplicating its evidence in temporary files or the final answer. Draft with the harness's file-editing tool rather than shell heredocs. Review source citations, causal language, option consistency, authorization, and residual uncertainty before the one terminal `prepare-handoff.py --accept-to-proposal` call. After success, report the conditional order, missing measurement, artifact, and exact lifecycle status in at most 500 words without reopening discovery.
