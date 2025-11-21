# Check if streamlit is installed
try {
    Get-Command streamlit -ErrorAction Stop | Out-Null
    Write-Host "Streamlit is already installed." -ForegroundColor Green
}
catch {
    Write-Host "Streamlit not found. Installing..." -ForegroundColor Yellow
    pip install streamlit
}

# Run the visualization app
Write-Host "Starting Output Visualization App..." -ForegroundColor Cyan
streamlit run visualize_output.py
