#!/usr/bin/env pwsh
# Enforce membrane discipline: only Git Runner commits are allowed.

$isRunner = $env:GIT_RUNNER -eq "1"
if ($isRunner) { exit 0 }

$commitMsgPath = git rev-parse --git-path COMMIT_EDITMSG 2>$null
if ($commitMsgPath -and (Test-Path $commitMsgPath)) {
    $content = Get-Content $commitMsgPath -Raw
    if ($content -match "\[git-runner\]") {
        exit 0
    }
}

Write-Host "❌ Commit blocked. Use tool.request.git.commit (Git Runner)." -ForegroundColor Red
Write-Host "   Set GIT_RUNNER=1 or include [git-runner] in the message when invoked by the runner."
exit 1
