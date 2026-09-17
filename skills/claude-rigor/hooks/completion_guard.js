#!/usr/bin/env node
"use strict";

// Request one task-aware skeptical review before Claude completes. Malformed
// input fails open, and stop_hook_active limits the review to once per turn.

const fs = require("fs");
const path = require("path");

const EDIT_TOOLS = new Set(["edit", "multiedit", "notebookedit", "write"]);
const INVESTIGATIVE_TOOLS = new Set([
  "bash",
  "glob",
  "grep",
  "read",
  "task",
  "webfetch",
  "websearch",
]);
const DIAGNOSIS_PATTERN =
  /\b(?:diagnos(?:e|is|ing)|debug|slow(?:ly)?|broken|failing|fails?|performance(?:\s+regression)?)\b/i;
const IMPLEMENTATION_REVIEW =
  "Before finishing, challenge the implementation once as a skeptical reviewer. " +
  "Re-read the request and inspect the final changes. Build explicit input partitions " +
  "for valid, boundary, malformed, wrong-type, and failure cases; compare every partition " +
  "with the required public contract and existing behavior. Resolve any stated judgment calls " +
  "from repository evidence instead of narrowing the contract or asking the user. Check for " +
  "missed callers, unintended files, weakened tests, silent fallbacks, and error-path regressions. " +
  "Run the narrowest meaningful verification available, fix any discovered gap, then report only " +
  "claims supported by executed evidence.";
const DIAGNOSIS_REVIEW =
  "Before finishing, challenge the diagnosis once as a skeptical reviewer. " +
  "For every quantitative claim, verify the environment, seam, fixture, execution and cache state, " +
  "sample size, and observed result. Keep aggregate service metrics bounded to service scope; do not " +
  "present them as endpoint evidence. Keep single-fixture and cross-environment measurements bounded " +
  "to what they actually represent. Classify each material claim as an observed measurement, measured " +
  "contributor, leading hypothesis, estimate, or established cause. Use root-cause or dominant-cause " +
  "language only when a discriminating intervention changed the matching end-to-end journey as " +
  "predicted. Make options atomic or label a staged bundle, state remaining unknowns, correct any " +
  "overclaim, then report only conclusions supported by the inspected evidence.";

function readEntries(value) {
  if (typeof value !== "string" || value.length === 0) return [];
  try {
    return fs
      .readFileSync(value, "utf8")
      .split(/\r?\n/)
      .filter((line) => line.trim())
      .map((line) => JSON.parse(line))
      .filter((item) => item && typeof item === "object" && !Array.isArray(item));
  } catch (_) {
    return [];
  }
}

function isHumanRequest(entry) {
  if (entry.type !== "user" || entry.isMeta) return false;
  const content = entry.message && entry.message.content;
  return !(
    Array.isArray(content) &&
    content.some((item) => item && typeof item === "object" && item.type === "tool_result")
  );
}

function textContent(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(textContent).join("\n");
  if (value && typeof value === "object") {
    return ["text", "content", "message", "name", "command", "args"]
      .filter((key) => Object.prototype.hasOwnProperty.call(value, key))
      .map((key) => textContent(value[key]))
      .join("\n");
  }
  return "";
}

function latestHumanRequest(entries) {
  let current = null;
  entries.forEach((entry, index) => {
    if (isHumanRequest(entry)) {
      current = {
        index,
        text: textContent(entry.message && entry.message.content).trim(),
      };
    }
  });
  return current;
}

function toolNamesSince(entries, start) {
  const tools = new Set();
  entries.slice(start).forEach((entry) => {
    if (entry.type !== "assistant") return;
    const content = entry.message && entry.message.content;
    if (!Array.isArray(content)) return;
    content.forEach((item) => {
      if (!item || typeof item !== "object" || item.type !== "tool_use") return;
      tools.add(String(item.name || "").split(".").pop().toLowerCase());
    });
  });
  return tools;
}

function isTaskWorkspace(value) {
  if (typeof value !== "string" || value.length === 0) return false;
  try {
    return fs.statSync(path.join(value, "TASK.md")).isFile();
  } catch (_) {
    return false;
  }
}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  input += chunk;
});
process.stdin.on("end", () => {
  try {
    const payload = JSON.parse(input);
    if (!payload || typeof payload !== "object" || payload.hook_event_name !== "Stop") return;
    if (payload.stop_hook_active === true) return;
    const entries = readEntries(payload.transcript_path);
    const request = latestHumanRequest(entries);
    const tools = toolNamesSince(entries, request ? request.index + 1 : 0);
    const diagnosis =
      request !== null &&
      DIAGNOSIS_PATTERN.test(request.text) &&
      [...tools].some((tool) => INVESTIGATIVE_TOOLS.has(tool));
    if (diagnosis) {
      process.stdout.write(JSON.stringify({ decision: "block", reason: DIAGNOSIS_REVIEW }));
      return;
    }
    const edited = [...tools].some((tool) => EDIT_TOOLS.has(tool));
    if (!edited && !isTaskWorkspace(payload.cwd)) return;
    process.stdout.write(JSON.stringify({ decision: "block", reason: IMPLEMENTATION_REVIEW }));
  } catch (_) {
    // Hooks must not prevent completion when their own input is malformed.
  }
});
