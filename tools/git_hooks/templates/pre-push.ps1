#!/usr/bin/env pwsh
# Prevent direct pushes from IDEs or manual usage.

if ($env:GIT_RUNNER -eq "1") {
    exit 0
}

Write-Host "❌ Push blocked. All pushes must use tool.request.git.pr (Git Runner)." -ForegroundColor Red
exit 1
