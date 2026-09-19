param(
    [string]$ClaudeHome = (Join-Path $env:USERPROFILE ".claude"),
    [string]$SourceRoot = (Join-Path $PSScriptRoot "..\skills\claude-rigor")
)

$ErrorActionPreference = "Stop"
$source = (Resolve-Path -LiteralPath $SourceRoot).Path
$destination = Join-Path $ClaudeHome "skills\claude-rigor"
$settingsPath = Join-Path $ClaudeHome "settings.json"
$claudePath = Join-Path $ClaudeHome "CLAUDE.md"
$backupDir = Join-Path $ClaudeHome "backups"

New-Item -ItemType Directory -Force -Path $destination, $backupDir | Out-Null
Copy-Item -Path (Join-Path $source "*") -Destination $destination -Recurse -Force
$retiredPreflight = Join-Path $destination "hooks\diagnosis_preflight.js"
if (Test-Path -LiteralPath $retiredPreflight) {
    Remove-Item -LiteralPath $retiredPreflight -Force
}

function Backup-File([string]$Path, [string]$Label) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmssfff"
    Copy-Item -LiteralPath $Path -Destination (Join-Path $backupDir "$Label-$stamp") -Force
}

$removed = @()
if (Test-Path -LiteralPath $settingsPath) {
    $raw = Get-Content -Raw -LiteralPath $settingsPath
    $settings = $raw | ConvertFrom-Json
    if ($null -ne $settings.hooks) {
        foreach ($eventName in @("PreToolUse", "Stop")) {
            if ($null -eq $settings.hooks.PSObject.Properties[$eventName]) { continue }
            $groups = @($settings.hooks.$eventName)
            if ($groups.Count -eq 0) { continue }
            $kept = @()
            foreach ($group in $groups) {
                $commands = @($group.hooks | ForEach-Object { [string]$_.command })
                $legacy = $commands | Where-Object {
                    $_ -match "workbench_diagnosis_hook\.py" -or $_ -match "[\\/]\.claude[\\/]hooks[\\/]completion_guard\.py"
                }
                if ($legacy) { $removed += $legacy } else { $kept += $group }
            }
            $settings.hooks.$eventName = $kept
        }
    }
    $updated = $settings | ConvertTo-Json -Depth 100
    if ($updated.Trim() -ne $raw.Trim()) {
        Backup-File $settingsPath "settings.json.before-claude-rigor"
        Set-Content -LiteralPath $settingsPath -Value $updated -Encoding utf8
    }
}

if (Test-Path -LiteralPath $claudePath) {
    $rawClaude = Get-Content -Raw -LiteralPath $claudePath
    $personal = ($rawClaude -split "(?m)^# Operating contract\s*$", 2)[0]
    $personal = [regex]::Replace(
        $personal,
        "(?ms)^# Claude Rigor \(managed\)\s*.*?^# End Claude Rigor\s*",
        ""
    ).TrimEnd()
    $managed = @"
# Claude Rigor (managed)

Apply the mandatory engineering operating contract imported below to every software task.
@~/.claude/skills/claude-rigor/agents/rigorous-engineer.md

# End Claude Rigor
"@
    $updatedClaude = if ($personal) { "$personal`r`n`r`n$managed`r`n" } else { "$managed`r`n" }
    if ($updatedClaude -ne $rawClaude) {
        Backup-File $claudePath "CLAUDE.md.before-claude-rigor"
        Set-Content -LiteralPath $claudePath -Value $updatedClaude -Encoding utf8
    }
} else {
    $managed = @"
# Claude Rigor (managed)

Apply the mandatory engineering operating contract imported below to every software task.
@~/.claude/skills/claude-rigor/agents/rigorous-engineer.md

# End Claude Rigor
"@
    Set-Content -LiteralPath $claudePath -Value "$managed`r`n" -Encoding utf8
}

$hooks = Get-Content -Raw -LiteralPath (Join-Path $destination "hooks\hooks.json") | ConvertFrom-Json
$hookFileHashes = [ordered]@{}
foreach ($hookFile in @("hooks.json", "completion_guard.js", "read_only_network_guard.js", "workbench_new_item_guard.js", "workbench_prompt_router.js", "performance_budget_guard.js")) {
    $hookFileHashes[$hookFile] = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $destination "hooks\$hookFile")).Hash.ToLowerInvariant()
}
$preToolUseCount = if ($null -ne $hooks.hooks.PSObject.Properties["PreToolUse"]) {
    @($hooks.hooks.PreToolUse).Count
} else {
    0
}
$userPromptSubmitCount = if ($null -ne $hooks.hooks.PSObject.Properties["UserPromptSubmit"]) {
    @($hooks.hooks.UserPromptSubmit).Count
} else {
    0
}
$stopCount = if ($null -ne $hooks.hooks.PSObject.Properties["Stop"]) {
    @($hooks.hooks.Stop).Count
} else {
    0
}
[ordered]@{
    claude_home = $ClaudeHome
    installed = $destination
    removed_legacy_commands = @($removed)
    pre_tool_use = $preToolUseCount
    user_prompt_submit = $userPromptSubmitCount
    stop = $stopCount
    global_prompt_import = "~/.claude/skills/claude-rigor/agents/rigorous-engineer.md"
    prompt_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $destination "agents\rigorous-engineer.md")).Hash.ToLowerInvariant()
    hooks_sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $destination "hooks\hooks.json")).Hash.ToLowerInvariant()
    hook_file_sha256 = $hookFileHashes
} | ConvertTo-Json -Depth 10
