#!/usr/bin/env node
"use strict";

// Honor an explicit Workbench start-new instruction before old lifecycle state
// can persuade the agent to resume or refuse. This guard asks no user question;
// it only directs the agent to the documented compact routing helper.

const fs = require("fs");

const WORKBENCH = /(?:^|[\s/])workbench\b/i;
const START_NEW = /(?:\b(?:start|create)\s+(?:a\s+)?new\b|\bignore\b[^.\n]{0,100}\bactive\s+work)/i;
const ROUTE_COMMAND = /prepare-routing\.py[\s\S]*--capture-and-start/i;
const ROUTE_SUCCESS = /captured-and-started/i;
const TEMP_ROUTING_WRITE = /(?:^|[\/\\])(?:tmp|\.scratch)[\/\\][^\r\n]*(?:compact|routing)[^\r\n]*\.json|(?:^|[\/\\])\.?[^\/\\\r\n]*(?:compact|routing)[^\/\\\r\n]*\.json/i;
const WORKBENCH_METHOD = /[\/\\](?:\.claude|\.agents)[\/\\]skills[\/\\]workbench[\/\\](?:SKILL\.md|references[\/\\][^\/\\]+\.md)$/i;
const BASH_METHOD_READ = /^\s*cat\s+["'][^"']*[\/\\](?:\.claude|\.agents)[\/\\]skills[\/\\]workbench[\/\\](?:SKILL\.md|references[\/\\][^"']+\.md)["']\s*$/i;
const WORKBENCH_SKILL = /(?:^|:)workbench\b/i;
const MARKER = "WORKBENCH_START_NEW_V1";

function readEntries(value) {
  if (typeof value !== "string" || !value) return [];
  try {
    return fs.readFileSync(value, "utf8").split(/\r?\n/).filter((line) => line.trim())
      .map((line) => JSON.parse(line)).filter((item) => item && typeof item === "object");
  } catch (_) { return []; }
}

function textContent(value) {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return value.map(textContent).join("\n");
  if (value && typeof value === "object") return Object.values(value).map(textContent).join("\n");
  return "";
}

function latestRequest(entries) {
  for (let index = entries.length - 1; index >= 0; index -= 1) {
    const entry = entries[index];
    if (entry.type !== "user" || entry.isMeta) continue;
    const content = entry.message && entry.message.content;
    if (Array.isArray(content) && content.some((item) => item && item.type === "tool_result")) continue;
    return { index, text: textContent(content) };
  }
  return null;
}

function deny() {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason:
        `${MARKER}: the user explicitly required a new Workbench item for this invocation. ` +
        "Do not inspect, resume, or use the identity of an existing item to reconsider that decision. " +
        "Create the compact routing JSON from the supplied request and call prepare-routing.py --capture-and-start now. Prior artifacts may be read as evidence only after the new lifecycle exists.",
    },
  }));
}

function insideWorkspace(candidate, cwd) {
  if (typeof candidate !== "string" || !candidate || typeof cwd !== "string" || !cwd) return false;
  const relative = require("path").relative(require("path").resolve(cwd), require("path").resolve(candidate));
  return relative !== ".." && !relative.startsWith(`..${require("path").sep}`) && !require("path").isAbsolute(relative);
}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => { input += chunk; });
process.stdin.on("end", () => {
  try {
    const payload = JSON.parse(input);
    if (!payload || payload.hook_event_name !== "PreToolUse") return;
    const entries = readEntries(payload.transcript_path);
    const request = latestRequest(entries);
    if (!request || !WORKBENCH.test(request.text) || !START_NEW.test(request.text)) return;
    const after = entries.slice(request.index + 1);
    if (after.some((entry) => ROUTE_SUCCESS.test(textContent(entry)))) return;

    const tool = String(payload.tool_name || "").split(".").pop().toLowerCase();
    const toolInput = textContent(payload.tool_input || {});
    // The skill owns the exact helper contract and ID format. Blocking it
    // forces the agent to guess the command this guard requires.
    if (tool === "skill" && WORKBENCH_SKILL.test(toolInput)) return;
    if (tool === "read" && WORKBENCH_METHOD.test(String(payload.tool_input && payload.tool_input.file_path || ""))) return;
    if (tool === "bash" && BASH_METHOD_READ.test(String(payload.tool_input && payload.tool_input.command || ""))) return;
    if (tool === "bash" && ROUTE_COMMAND.test(toolInput)) return;
    if (["write", "edit", "multiedit"].includes(tool) && TEMP_ROUTING_WRITE.test(toolInput)) {
      const filePath = payload.tool_input && payload.tool_input.file_path;
      if (insideWorkspace(filePath, payload.cwd)) return;
    }
    if (tool === "bash" && TEMP_ROUTING_WRITE.test(toolInput) && !/\.workbench[\/\\]work/i.test(toolInput)) return;
    deny();
  } catch (_) {
    // Malformed input fails open so the harness cannot disable tools globally.
  }
});
