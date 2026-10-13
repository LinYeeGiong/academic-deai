<#
Install the academic-deai skill for any Agent Skills compatible agent.

  .\install.ps1              # auto-detect installed agents, install for each
  .\install.ps1 -Agents      # portable location only (~\.agents\skills)
  .\install.ps1 -Claude      # Claude Code only (~\.claude\skills)
  .\install.ps1 -Project     # this repo's .agents\skills (committed, team-wide)
  .\install.ps1 -Link        # junction/symlink instead of copy (tracks git pull)
  .\install.ps1 -List        # show what would be done, change nothing

Works on Windows PowerShell 5.1 and PowerShell 7+.
#>
[CmdletBinding()]
param(
  [switch]$Agents,
  [switch]$Claude,
  [switch]$Codex,
  [switch]$Pi,
  [switch]$Cursor,
  [switch]$Gemini,
  [switch]$OpenCode,
  [switch]$Goose,
  [switch]$Project,
  [switch]$All,
  [switch]$Link,
  [switch]$List
)

$ErrorActionPreference = 'Stop'
$skill = 'academic-deai'
$src = Join-Path $PSScriptRoot "skills\$skill"

if (-not (Test-Path (Join-Path $src 'SKILL.md'))) {
  Write-Error "cannot find $src\SKILL.md"
  exit 1
}

$home_ = $env:USERPROFILE
if (-not $home_) { $home_ = $HOME }

$targets = New-Object System.Collections.Generic.List[string]
if ($Agents -or $Codex -or $Pi) { $targets.Add("$home_\.agents\skills") }
if ($Claude)   { $targets.Add("$home_\.claude\skills") }
if ($Cursor)   { $targets.Add("$home_\.cursor\skills") }
if ($Gemini)   { $targets.Add("$home_\.gemini\skills") }
if ($OpenCode) { $targets.Add("$home_\.config\opencode\skills") }
if ($Goose)    { $targets.Add("$home_\.config\goose\skills") }
if ($Project)  { $targets.Add((Join-Path $PWD '.agents\skills')) }
if ($All) {
  $targets.Add("$home_\.agents\skills")
  $targets.Add("$home_\.claude\skills")
}

# Auto-detect: always the portable location, plus any agent already configured.
if ($targets.Count -eq 0) {
  $targets.Add("$home_\.agents\skills")
  foreach ($p in @(
      @{ Dir = "$home_\.claude";          Skills = "$home_\.claude\skills" },
      @{ Dir = "$home_\.cursor";          Skills = "$home_\.cursor\skills" },
      @{ Dir = "$home_\.gemini";          Skills = "$home_\.gemini\skills" },
      @{ Dir = "$home_\.config\opencode"; Skills = "$home_\.config\opencode\skills" },
      @{ Dir = "$home_\.config\goose";    Skills = "$home_\.config\goose\skills" })) {
    if (Test-Path $p.Dir) { $targets.Add($p.Skills) }
  }
}

$mode = if ($Link) { 'link' } else { 'copy' }
Write-Host "source: $src"
Write-Host "mode:   $mode`n"

foreach ($base in ($targets | Select-Object -Unique)) {
  $dest = Join-Path $base $skill

  if ($List) {
    Write-Host "  would install -> $dest"
    continue
  }

  if (-not (Test-Path $base)) {
    New-Item -ItemType Directory -Force -Path $base | Out-Null
  }
  # Replace any previous install, including a stale link.
  if (Test-Path $dest) {
    $item = Get-Item $dest -Force
    if ($item.LinkType) { $item.Delete() } else { Remove-Item -Recurse -Force $dest }
  }

  if ($mode -eq 'link') {
    try {
      New-Item -ItemType Junction -Path $dest -Target $src -ErrorAction Stop | Out-Null
      Write-Host "  linked  -> $dest"
    } catch {
      Copy-Item -Recurse -Force $src $dest
      Write-Host "  copied  -> $dest  (junction unavailable)"
    }
  } else {
    Copy-Item -Recurse -Force $src $dest
    Write-Host "  copied  -> $dest"
  }
}

if ($List) { exit 0 }

Write-Host @'

Done. Restart your agent (or run /reload) and invoke the skill:

  Claude Code   /academic-deai
  Codex         $academic-deai
  pi            /skill:academic-deai
  others        just ask: "de-AI this paragraph" (Chinese or English)

Scanner (optional, needs Python 3.9+):
  python <skill dir>\scripts\scan.py <file> --format md
'@
