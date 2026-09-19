#!/usr/bin/env node
"use strict";

// Prevent an answer/options investigation from probing a deployed application
// when the request did not authorize external mutation. GET is not inherently
// read-only: handlers may warm caches, enqueue work, or write audit state.

const fs = require("fs");
const path = require("path");

const READ_ONLY = /\b(?:investigate|diagnos(?:e|is)|review|audit|assess|explain|give\s+me\s+options|what\s+are\s+my\s+options)\b/i;
const CHANGE_AUTH = /\b(?:implement|apply\s+(?:the|a|this)\s+(?:fix|change)|modify\s+(?:the|this)|deploy|ship\s+(?:the|this)|make\s+the\s+change)\b/i;
const EXPLICIT_LIVE_AUTH = /\b(?:authorize|you\s+may|permission\s+to)\b[^.\n]{0,100}\b(?:probe|exercise|call|request)\b[^.\n]{0,100}\b(?:deployed|live|production|staging|test\s+app)\b/i;
const DIRECT_REQUEST = /\b(?:curl|wget|invoke-webrequest|invoke-restmethod|iwr|irm)\b[^\n]*(?:https?:\/\/)(?!localhost\b|127\.0\.0\.1\b|\[::1\])/i;
const MUTATING_AWS = /\baws\s+\S+\s+(?:invoke|put-|create-|update-|delete-|start-execution|send-message|publish|run-task)\b/i;
const ACTIVE_SCRIPT = /(?:https?:\/\/(?!localhost\b|127\.0\.0\.1\b|\[::1\])|\blogin\s*\(|\brequests\.(?:get|post|put|patch|delete|request)\s*\(|\bhttpx\.|\burlopen\s*\(|\bfetch\s*\(|\bpage\.goto\s*\(|\bbrowser_navigate\b)/i;
const ACTIVE_INLINE = /(?:https?:\/\/(?!localhost\b|127\.0\.0\.1\b|\[::1\])|\blogin\s*\(|\brequests\.(?:get|post|put|patch|delete|request)\s*\(|\bhttpx\.|\burlopen\s*\(|\bfetch\s*\()/i;
const MARKER = "READ_ONLY_NETWORK_GUARD_V1";

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
    return textContent(content);
  }
  return "";
}

function candidateScripts(command, cwd) {
  let base = cwd;
  const cd = command.match(/\bcd\s+["']([^"']+)["']/i);
  if (cd) base = cd[1];
  const found = [];
  const pattern = /\b(?:python(?:3)?|py|node)\s+(?:-[^\s]+\s+)*(?:["']([^"']+\.(?:py|js|ts))["']|([^\s;&|"']+\.(?:py|js|ts)))/gi;
  for (const match of command.matchAll(pattern)) {
    const raw = match[1] || match[2];
    const resolved = path.resolve(base || ".", raw);
    if (fs.existsSync(resolved) && fs.statSync(resolved).isFile()) found.push(resolved);
  }
  return found;
}

function deny() {
  process.stdout.write(JSON.stringify({
    hookSpecificOutput: {
      hookEventName: "PreToolUse",
      permissionDecision: "deny",
      permissionDecisionReason:
        `${MARKER}: this answer/options request is read-only, but the command can exercise a deployed application and create side effects such as cache entries, queues, counters, or audit records. ` +
        "Use repository evidence and passive telemetry, or obtain explicit authorization for the live probe. GET and ordinary application usage are not exemptions.",
    },
  }));
}

let input = "";
process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => { input += chunk; });
process.stdin.on("end", () => {
  try {
    const payload = JSON.parse(input);
    if (!payload || payload.hook_event_name !== "PreToolUse") return;
    const tool = String(payload.tool_name || "").split(".").pop().toLowerCase();
    if (tool !== "bash") return;
    const request = latestRequest(readEntries(payload.transcript_path));
    if (!READ_ONLY.test(request) || CHANGE_AUTH.test(request) || EXPLICIT_LIVE_AUTH.test(request)) return;
    const command = payload.tool_input && String(payload.tool_input.command || "");
    if (DIRECT_REQUEST.test(command) || MUTATING_AWS.test(command)) { deny(); return; }
    if (/\b(?:python(?:3)?|py|node)\b[^\n]*\s-(?:c|e)\b/i.test(command) && ACTIVE_INLINE.test(command)) { deny(); return; }
    for (const script of candidateScripts(command, payload.cwd)) {
      if (ACTIVE_SCRIPT.test(fs.readFileSync(script, "utf8"))) { deny(); return; }
    }
  } catch (_) {
    // Malformed input fails open so the harness cannot disable tools globally.
  }
});
