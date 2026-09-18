#!/usr/bin/env node
"use strict";

// One-shot diagnosis preflight for Claude Code PreToolUse. It blocks the first
// investigative tool call with the prerequisites that prevent expensive late
// corrections. The denial marker in the transcript makes the retry pass.

const fs = require("fs");

const INVESTIGATIVE_TOOLS = new Set([
  "agent", "bash", "glob", "grep", "read", "task", "webfetch", "websearch",
]);
const DIAGNOSIS_PATTERN =
  /\b(?:diagnos(?:e|is|ing)|debug|slow(?:ly)?|broken|failing|fails?|performance(?:\s+regression)?)\b/i;
const WORKBENCH_PATTERN = /(?:^|[\s/])workbench\b/i;
const ENVIRONMENT_PATTERN = /\b(?:local(?:ly)?|deployed|deployment|production|prod|staging|stage|test\s+(?:environment|deployment|app)|development\s+(?:environment|server))\b/i;
const PROVENANCE_PATTERN = /\b(?:commit|revision|source\s+snapshot|deployed\s+(?:version|revision))\b/i;
const JOURNEY_PATTERN = /\b(?:journey|seam|endpoint|request\s+path|page[- ]preview)\b/i;
const FIXTURE_PATTERN = /\b(?:fixture|sample|synthetic|customer\s+(?:data|document))\b/i;
const CACHE_STATE_PATTERN = /\b(?:cache|cached|cold|warm)\b/i;
const MARKER = "DIAGNOSIS_PREFLIGHT_V1";
const WORKBENCH_ABSTRACTION_MARKER = "WORKBENCH_ABSTRACTION_V1";
const BENCHMARK_PATTERN = /(?:perf_counter|timeit\s*\(|benchmark|(?:^|[\/\\\s])bench\.py\b|hyperfine)/i;
const BOUNDED_BENCHMARK_PATTERN = /BENCHMARK_BUDGET_SECONDS=120[\s\S]*\btimeout\s+(?:120s?|2m)\b/i;
const SINGLE_JOURNEY_PATTERN = /\bjourney\b/i;
const WORKBENCH_INTERNAL_PATTERN = /(?:workbench[\/\\](?:references|schemas)[\/\\]|find\s+[^\r\n]*workbench[^\r\n]*(?:-name|glob)[^\r\n]*json|workbench\.py\s+(?:--help|[a-z-]+\s+--help)|prepare-(?:handoff|routing)\.py)/i;
const WORKBENCH_HELPER_INVOCATION = /prepare-(?:handoff|routing)\.py[\s\S]*--input\b[\s\S]*--output\b/i;
const DIRECT_LIFECYCLE_PATTERN = /workbench\.py\s+(?:capture-intake|route-and-start|accept-handoff|advance-stage)\b/i;

function textContent(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(textContent).join("\n");
  if (value && typeof value === "object") {
    return ["message", "text", "content", "name", "skill", "command", "args", "file_path", "description"]
      .filter((key) => Object.prototype.hasOwnProperty.call(value, key))
      .map((key) => textContent(value[key]))
      .join("\n");
  }
  return "";
}

function readEntries(value) {
  if (typeof value !== "string" || !value) return [];
  try {
    return fs.readFileSync(value, "utf8").split(/\r?\n/).filter((line) => line.trim())
      .map((line) => JSON.parse(line)).filter((item) => item && typeof item === "object");
  } catch (_) {
    return [];
  }
}

function isHumanRequest(entry) {
  if (entry.type !== "user" || entry.isMeta) return false;
  const content = entry.message && entry.message.content;
  return !(Array.isArray(content) && content.some(
    (item) => item && typeof item === "object" && item.type === "tool_result"
  ));
}

function latestRequest(entries) {
  for (let index = entries.length - 1; index >= 0; index -= 1) {
    if (isHumanRequest(entries[index])) {
      return { index, text: textContent(entries[index].message && entries[index].message.content) };
    }
  }
  return null;
}

function interactiveAnswerText(entry) {
  if (!entry || entry.type !== "user") return "";
  const answers = entry.toolUseResult && entry.toolUseResult.answers;
  if (answers && typeof answers === "object" && !Array.isArray(answers)) {
    return Object.values(answers).filter((value) => typeof value === "string").join("\n");
  }
  const content = entry.message && entry.message.content;
  if (!Array.isArray(content)) return "";
  return content.filter((item) =>
    item && item.type === "tool_result" && typeof item.content === "string" &&
    /^Your questions have been answered:/i.test(item.content)
  ).map((item) => item.content).join("\n");
}

function loaded(entries, start, skill) {
  return entries.slice(start).some((entry) => {
    const text = textContent(entry).toLowerCase();
    return text.includes(skill) && (
      entry.isMeta || text.includes("base directory for this skill") ||
      text.includes("<command-name>") || text.replace(/\s/g, "").includes('"name":"skill"')
    );
  });
}

function deny(reason) {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason: `${MARKER}: ${reason}`,
    },
  }));
}

function hasCompleteCoordinates(value) {
  return ENVIRONMENT_PATTERN.test(value) && PROVENANCE_PATTERN.test(value) &&
    JOURNEY_PATTERN.test(value) && FIXTURE_PATTERN.test(value) && CACHE_STATE_PATTERN.test(value);
}

function executableShellText(value) {
  if (typeof value !== "string") return "";
  const kept = [];
  let delimiter = null;
  for (const line of value.split(/\r?\n/)) {
    if (delimiter !== null) {
      if (line.trim() === delimiter) delimiter = null;
      continue;
    }
    kept.push(line);
    const match = line.match(/<<-?\s*(['"]?)([A-Za-z_][A-Za-z0-9_]*)\1/);
    if (match) delimiter = match[2];
  }
  return kept.join("\n");
}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => { input += chunk; });
process.stdin.on("end", () => {
  try {
    const payload = JSON.parse(input);
    if (!payload || payload.hook_event_name !== "PreToolUse") return;
    const tool = String(payload.tool_name || "").split(".").pop().toLowerCase();
    if (!INVESTIGATIVE_TOOLS.has(tool)) return;
    const entries = readEntries(payload.transcript_path);
    const request = latestRequest(entries);
    if (!request || !DIAGNOSIS_PATTERN.test(request.text)) return;
    const after = entries.slice(request.index + 1);
    const coordinateText = [request.text, ...after.map(interactiveAnswerText)].filter(Boolean).join("\n");

    const required = [];
    if (
      WORKBENCH_PATTERN.test(request.text) &&
      !/^\s*\/workbench\b/i.test(request.text) &&
      !loaded(entries, request.index + 1, "workbench")
    ) {
      required.push("load Workbench");
    }
    if (!loaded(entries, request.index + 1, "diagnosing-bugs")) required.push("load diagnosing-bugs");
    if (!ENVIRONMENT_PATTERN.test(coordinateText)) {
      const prefix = required.length ? `${required.join(" and ")}; then ` : "";
      deny(
        `${prefix}STOP before repository investigation or routing. The observed environment is user-owned and missing. ` +
        "Ask only whether the slowdown is in local development, the deployed test environment, staging, or production. Do not invoke another tool until the user answers."
      );
      return;
    }
    const toolInput = textContent(payload.tool_input || {});
    if (tool === "agent" && SINGLE_JOURNEY_PATTERN.test(request.text)) {
      deny(
        "keep this single-journey diagnosis in the current agent. Delegation would duplicate repository context and evidence synthesis; " +
        "trace the bounded seam directly and stop when the ranking is stable."
      );
      return;
    }
    if (tool === "bash" && WORKBENCH_PATTERN.test(request.text) && DIRECT_LIFECYCLE_PATTERN.test(toolInput)) {
      deny(
        "use the compact lifecycle helpers instead of direct Workbench mutation. " +
        "Start with prepare-routing.py --capture-and-start, and record each phase with " +
        "prepare-handoff.py --accept-and-advance. Each helper validates, registers, and advances once."
      );
      return;
    }
    if (
      WORKBENCH_PATTERN.test(request.text) && WORKBENCH_INTERNAL_PATTERN.test(toolInput) &&
      !WORKBENCH_HELPER_INVOCATION.test(toolInput) &&
      !after.some((entry) => textContent(entry).includes("prepare-handoff refused:")) &&
      !after.some((entry) => textContent(entry).includes("prepare-routing refused:"))
    ) {
      deny(
        `${WORKBENCH_ABSTRACTION_MARKER}: keep the Workbench helper as an abstraction boundary. ` +
        "Do not read schema catalogs or helper implementation to author ordinary routing or phase bundles. " +
        "Use the documented compact input and run prepare-routing.py or prepare-handoff.py directly. " +
        "Repair a helper's named compact field directly. Inspect internals only after the same field-level repair fails twice."
      );
      return;
    }
    const shellCommand = tool === "bash" && payload.tool_input &&
      typeof payload.tool_input.command === "string"
      ? executableShellText(payload.tool_input.command) : "";
    if (
      tool === "bash" && BENCHMARK_PATTERN.test(shellCommand) &&
      !BOUNDED_BENCHMARK_PATTERN.test(toolInput)
    ) {
      deny(
        "bound this diagnostic benchmark before running it. Use at most two representative fixtures and three repetitions, " +
        "prefix the executable command with BENCHMARK_BUDGET_SECONDS=120, and enforce a GNU `timeout 120s` wall-clock limit. " +
        "Treat partial or timed-out results as bounded evidence; do not expand the matrix in this session."
      );
      return;
    }
    if (after.some((entry) => textContent(entry).includes(MARKER))) return;
    if (required.length === 0 && hasCompleteCoordinates(coordinateText)) return;
    const prefix = required.length ? `${required.join(" and ")}; then ` : "";
    deny(
      `${prefix}disposition environment, deployed/source revision, user journey or seam, representative fixture, and cold/warm cache state before routing or ranking. ` +
      "Inspect discoverable facts. If a user-only fact can reorder the options, preserve intake and ask that prerequisite question alone."
    );
  } catch (_) {
    // A guard that cannot understand its own input must not disable tools.
  }
});
