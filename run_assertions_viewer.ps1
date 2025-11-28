# Run Assertions Viewer with Fluent Design
# Usage: .\run_assertions_viewer.ps1

Write-Host "Starting Assertions Viewer..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

streamlit run view_assertions.py --server.port 8502
