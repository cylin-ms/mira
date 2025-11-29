# GPT-5 Q&A Tool Wrapper
# Usage: .\gpt5.ps1 "Your question here"
#        .\gpt5.ps1 -Interactive
#        .\gpt5.ps1 -List
#        .\gpt5.ps1 -View "2025-11-29/session_001.json"

param(
    [Parameter(Position=0)]
    [string]$Question,
    
    [switch]$Interactive,
    [switch]$List,
    [string]$View,
    [string]$System,
    [string]$PromptFile,
    [int]$Days = 7
)

$scriptPath = Join-Path $PSScriptRoot "tools\gpt5_qa.py"

# Activate venv if exists
$venvActivate = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    . $venvActivate
}

if ($Interactive) {
    python $scriptPath
}
elseif ($List) {
    python $scriptPath --list-sessions --days $Days
}
elseif ($View) {
    python $scriptPath --view-session $View
}
elseif ($PromptFile) {
    if ($System) {
        python $scriptPath --prompt-file $PromptFile --system $System
    } else {
        python $scriptPath --prompt-file $PromptFile
    }
}
elseif ($Question) {
    if ($System) {
        python $scriptPath -q $Question --system $System
    } else {
        python $scriptPath -q $Question
    }
}
else {
    # Default to interactive mode
    python $scriptPath
}
