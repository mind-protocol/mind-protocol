# Reads stdin JSON, extracts the command, blocks risky dirs/patterns.
$inputJson = Get-Content -Raw
$payload   = $inputJson | ConvertFrom-Json
$command   = $payload.tool_input.command

# block both / and \ path forms, plus .env, git internals, build dirs
$blocked = 'node_modules([\\/]|$)|\.env([\\/]|$)|__pycache__([\\/]|$)|\.git([\\/]|$)|dist([\\/]|$)|build([\\/]|$)'

if ($command -match $blocked) {
  Write-Error "ERROR: Blocked directory pattern"
  exit 2
}