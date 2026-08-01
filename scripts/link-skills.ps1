# Links every skill in this repo into the local agent skill directories:
#   ~/.claude/skills  - Claude Code
#   ~/.codex/skills   - Codex
#
# Each entry is a Windows junction into this repo, so an edit here is live in the
# next session and a `git pull` updates every installed skill at once. Junctions
# are used rather than symlinks because `ln -s` under Git Bash on Windows silently
# creates real directory copies.
#
# Re-run after adding, renaming, or removing a skill.

$ErrorActionPreference = 'Stop'

$repo = Split-Path -Parent $PSScriptRoot
$skillsRoot = Join-Path $repo 'skills'

if (-not (Test-Path $skillsRoot)) {
    throw "No skills directory found at $skillsRoot"
}

# Flat layout (skills/<name>/SKILL.md) plus one extra level for future buckets
# (skills/<bucket>/<name>/SKILL.md).
$found = @(Get-ChildItem $skillsRoot -Recurse -Depth 1 -Filter 'SKILL.md' -File)
if ($found.Count -eq 0) {
    throw "No SKILL.md files found under $skillsRoot"
}

$skills = @($found | ForEach-Object {
    [PSCustomObject]@{
        Name   = $_.Directory.Name
        Source = $_.Directory.FullName
    }
})

$destinations = @(
    (Join-Path $HOME '.claude\skills'),
    (Join-Path $HOME '.codex\skills')
)

foreach ($dest in $destinations) {
    # If the destination itself is a link pointing into this repo, linking each
    # skill would write the junctions back into our own working tree.
    if (Test-Path $dest) {
        $destItem = Get-Item $dest -Force
        if ($destItem.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            $resolved = $destItem.Target
            if ($resolved -and ($resolved -like "$repo*")) {
                throw "$dest is a link into this repo ($resolved). Remove it and re-run."
            }
        }
    }
    else {
        New-Item -ItemType Directory -Path $dest -Force | Out-Null
    }

    Write-Host ""
    Write-Host "-> $dest"

    foreach ($skill in $skills) {
        $target = Join-Path $dest $skill.Name

        if (Test-Path $target) {
            $existing = Get-Item $target -Force
            if ($existing.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                # Delete the link only, never the directory it points at.
                $existing.Delete()
            }
            else {
                Write-Host "   replacing real directory $($skill.Name) (this repo wins)"
                Remove-Item $target -Recurse -Force
            }
        }

        New-Item -ItemType Junction -Path $target -Value $skill.Source | Out-Null
        Write-Host "   linked $($skill.Name)"
    }
}

Write-Host ""
Write-Host "Linked $($skills.Count) skill(s) into $($destinations.Count) director(ies)."
