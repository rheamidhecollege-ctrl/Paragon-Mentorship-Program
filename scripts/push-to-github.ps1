# After creating an empty repo on GitHub (no README), run:
#   .\scripts\push-to-github.ps1 -RepoUrl "https://github.com/YOUR_USERNAME/YOUR_REPO.git"
param(
    [Parameter(Mandatory = $true)]
    [string] $RepoUrl
)
$ErrorActionPreference = "Stop"
$git = "C:\Program Files\Git\bin\git.exe"
if (-not (Test-Path $git)) { $git = "git" }
Set-Location (Join-Path $PSScriptRoot "..")
& $git remote remove origin 2>$null
& $git remote add origin $RepoUrl
& $git push -u origin main
Write-Host "Done. Next: https://share.streamlit.io → New app → this repo → Main file: streamlit_app.py"
