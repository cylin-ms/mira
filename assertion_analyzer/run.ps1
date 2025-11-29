<#
.SYNOPSIS
    Run the Assertion Analyzer in its virtual environment.

.DESCRIPTION
    This script runs the assertion_analyzer package using the virtual environment.
    If the venv doesn't exist, it will be created automatically.

.PARAMETER Assertion
    The assertion text to analyze (single mode).

.PARAMETER Batch
    Path to a text file with one assertion per line (batch mode).

.PARAMETER Context
    Optional context about the meeting/response.

.PARAMETER Json
    Output as JSON instead of formatted text.

.PARAMETER NoExamples
    Skip WBP example generation (faster, classify only).

.PARAMETER Quiet
    Reduce output verbosity.

.PARAMETER OutputDir
    Directory to save results.

.EXAMPLE
    .\run.ps1 "The plan includes task deadlines"

.EXAMPLE
    .\run.ps1 -Batch "assertions.txt" -OutputDir "./results"

.EXAMPLE
    .\run.ps1 "Tasks have owners" -NoExamples -Quiet

.EXAMPLE
    .\run.ps1 "Timeline is clear" -Json
#>

param(
    [Parameter(Position=0)]
    [string]$Assertion,
    
    [Alias("b")]
    [string]$Batch,
    
    [string]$Context,
    
    [switch]$Json,
    
    [switch]$NoExamples,
    
    [switch]$Quiet,
    
    [Alias("o")]
    [string]$OutputDir
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ScriptDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$RequirementsFile = Join-Path $ScriptDir "requirements.txt"

# Check if venv exists, create if not
if (-not (Test-Path $VenvPython)) {
    Write-Host "Virtual environment not found. Setting up..." -ForegroundColor Yellow
    
    # Create venv
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
    
    if (-not (Test-Path $VenvPython)) {
        Write-Error "Failed to create virtual environment!"
        exit 1
    }
    
    # Install dependencies
    Write-Host "Installing dependencies..."
    & $VenvPython -m pip install --upgrade pip | Out-Null
    & $VenvPython -m pip install -r $RequirementsFile
    
    Write-Host "Setup complete!" -ForegroundColor Green
    Write-Host ""
}

# Build command arguments
$Args = @("-m", "assertion_analyzer")

if ($Batch) {
    $Args += "--batch"
    $Args += $Batch
} elseif ($Assertion) {
    $Args += $Assertion
}

if ($Context) {
    $Args += "--context"
    $Args += $Context
}

if ($Json) {
    $Args += "--json"
}

if ($NoExamples) {
    $Args += "--no-examples"
}

if ($Quiet) {
    $Args += "--quiet"
}

if ($OutputDir) {
    $Args += "--output-dir"
    $Args += $OutputDir
}

# Set encoding for proper output
$env:PYTHONIOENCODING = "utf-8"

# Add the parent directory to PYTHONPATH so the package can be found
$ParentDir = Split-Path -Parent $ScriptDir
$env:PYTHONPATH = $ParentDir

# Run the analyzer
& $VenvPython $Args
