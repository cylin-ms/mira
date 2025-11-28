"""
Shared configuration and utilities for the pipeline.

This module provides:
- API configuration (Substrate GPT-5 JJ)
- Authentication helpers
- Common file paths
- Shared data structures
- Run ID management for tracking pipeline runs
"""

import os
import json
import time
import ctypes
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# API Configuration
# ═══════════════════════════════════════════════════════════════════════════════

SUBSTRATE_ENDPOINT = "https://fe-26.qas.bing.net/chat/completions"
SUBSTRATE_RESOURCE = "https://substrate.office.com"
CLIENT_ID = "d3590ed6-52b3-4102-aeff-aad2292ab01c"
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
JJ_MODEL = "dev-gpt-5-chat-jj"

# Rate limiting
DELAY_BETWEEN_CALLS = 2  # seconds
MAX_RETRIES = 3

# Global token cache
_jj_token_cache = None


# ═══════════════════════════════════════════════════════════════════════════════
# Run ID and File Paths
# ═══════════════════════════════════════════════════════════════════════════════

# Base output directory
PIPELINE_OUTPUT_BASE = os.path.join("docs", "pipeline_runs")

# Current run state (set by initialize_run or load_run)
_current_run_id: Optional[str] = None
_current_run_dir: Optional[str] = None


def generate_run_id() -> str:
    """Generate a unique run ID with timestamp and short UUID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"run_{timestamp}_{short_uuid}"


def initialize_run(run_id: Optional[str] = None) -> str:
    """
    Initialize a new pipeline run with a unique ID and directory.
    
    Args:
        run_id: Optional custom run ID. If None, generates a new one.
        
    Returns:
        The run ID being used.
    """
    global _current_run_id, _current_run_dir
    
    _current_run_id = run_id or generate_run_id()
    _current_run_dir = os.path.join(PIPELINE_OUTPUT_BASE, _current_run_id)
    
    # Create run directory
    os.makedirs(_current_run_dir, exist_ok=True)
    
    # Save run metadata
    metadata = {
        "run_id": _current_run_id,
        "created_at": datetime.now().isoformat(),
        "status": "initialized"
    }
    with open(os.path.join(_current_run_dir, "run_metadata.json"), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return _current_run_id


def load_run(run_id: str) -> str:
    """
    Load an existing run by ID.
    
    Args:
        run_id: The run ID to load.
        
    Returns:
        The run ID if found.
        
    Raises:
        ValueError: If run ID doesn't exist.
    """
    global _current_run_id, _current_run_dir
    
    run_dir = os.path.join(PIPELINE_OUTPUT_BASE, run_id)
    if not os.path.exists(run_dir):
        raise ValueError(f"Run '{run_id}' not found in {PIPELINE_OUTPUT_BASE}")
    
    _current_run_id = run_id
    _current_run_dir = run_dir
    
    return run_id


def get_current_run_id() -> Optional[str]:
    """Get the current run ID."""
    return _current_run_id


def get_current_run_dir() -> str:
    """
    Get the current run directory, initializing if needed.
    
    Returns:
        Path to the current run directory.
    """
    global _current_run_id, _current_run_dir
    
    if _current_run_dir is None:
        initialize_run()
    
    return _current_run_dir


def list_runs() -> List[Dict[str, Any]]:
    """
    List all available pipeline runs.
    
    Returns:
        List of run metadata dictionaries sorted by creation time (newest first).
    """
    runs = []
    
    if not os.path.exists(PIPELINE_OUTPUT_BASE):
        return runs
    
    for run_id in os.listdir(PIPELINE_OUTPUT_BASE):
        run_dir = os.path.join(PIPELINE_OUTPUT_BASE, run_id)
        metadata_file = os.path.join(run_dir, "run_metadata.json")
        
        if os.path.isdir(run_dir) and os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                metadata["path"] = run_dir
                runs.append(metadata)
            except Exception:
                runs.append({
                    "run_id": run_id,
                    "path": run_dir,
                    "created_at": None,
                    "status": "unknown"
                })
    
    # Sort by creation time (newest first)
    runs.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return runs


def get_run_file(filename: str) -> str:
    """
    Get the full path to a file within the current run directory.
    
    Args:
        filename: The filename (e.g., "scenarios.json")
        
    Returns:
        Full path to the file.
    """
    return os.path.join(get_current_run_dir(), filename)


# Standard file names within a run
SCENARIOS_FILENAME = "scenarios.json"
ASSERTIONS_FILENAME = "assertions.json"
PLANS_FILENAME = "plans.json"
EVALUATION_FILENAME = "evaluation_results.json"
REPORT_FILENAME = "evaluation_report.md"

# Legacy paths (for backward compatibility during transition)
PIPELINE_OUTPUT_DIR = os.path.join("docs", "pipeline_output")
SCENARIOS_FILE = os.path.join(PIPELINE_OUTPUT_DIR, "scenarios.json")
ASSERTIONS_FILE = os.path.join(PIPELINE_OUTPUT_DIR, "assertions.json")
PLANS_FILE = os.path.join(PIPELINE_OUTPUT_DIR, "plans.json")
EVALUATION_FILE = os.path.join(PIPELINE_OUTPUT_DIR, "evaluation_results.json")
REPORT_FILE = os.path.join(PIPELINE_OUTPUT_DIR, "evaluation_report.md")

# Ensure base directories exist
os.makedirs(PIPELINE_OUTPUT_BASE, exist_ok=True)
os.makedirs(PIPELINE_OUTPUT_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════════════
# Data Structures
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SourceEntities:
    """Ground truth source data for grounding verification."""
    attendees: List[str]
    organizer: str
    meeting_date: str
    meeting_time: str
    timezone: str
    files: List[str]
    topics: List[str]
    dependencies: List[str]


@dataclass
class Scenario:
    """A meeting scenario with all context for evaluation."""
    id: str
    title: str
    date: str
    time: str
    timezone: str
    duration_minutes: int
    organizer: str
    attendees: List[str]
    context: str
    artifacts: List[str]
    dependencies: List[str]
    user_prompt: str
    source_entities: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Scenario':
        return cls(**data)


@dataclass
class StructuralAssertion:
    """
    Structural Assertion (S1-S10): Checks PRESENCE/SHAPE.
    Question: "Does the plan HAVE X?"
    
    Key Rule: No hardcoded values - only check if element EXISTS.
    """
    id: str  # e.g., "S1", "S2"
    pattern_id: str  # e.g., "S1", "S2", etc.
    text: str  # The assertion text
    level: str  # critical, expected, aspirational
    checks_for: str  # Description of what structure it checks
    
    def to_dict(self) -> Dict:
        return {**asdict(self), "layer": "structural"}


@dataclass 
class GroundingAssertion:
    """
    Grounding Assertion (G1-G5): Checks FACTUAL ACCURACY.
    Question: "Is X CORRECT vs source?"
    
    Key Rule: Must reference a source field for comparison.
    """
    id: str  # e.g., "G1", "G2"
    pattern_id: str
    text: str
    level: str
    source_field: str  # e.g., "source.ATTENDEES", "source.MEETING.StartTime"
    verification_method: str  # How to verify against source
    
    def to_dict(self) -> Dict:
        return {**asdict(self), "layer": "grounding"}


@dataclass
class AssertionSet:
    """Complete assertion set for a scenario."""
    scenario_id: str
    structural: List[StructuralAssertion]
    grounding: List[GroundingAssertion]
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "scenario_id": self.scenario_id,
            "structural": [a.to_dict() for a in self.structural],
            "grounding": [a.to_dict() for a in self.grounding],
            "generated_at": self.generated_at,
            "total_assertions": len(self.structural) + len(self.grounding)
        }


@dataclass
class WorkbackPlan:
    """A generated workback plan at a specific quality level."""
    scenario_id: str
    quality_level: str  # "perfect", "medium", "low"
    content: str  # The full plan text
    intended_structural_score: float  # Expected S-score
    intended_grounding_score: float  # Expected G-score
    deliberate_issues: List[str] = field(default_factory=list)  # For medium/low
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AssertionResult:
    """Result of evaluating a single assertion."""
    assertion_id: str
    assertion_text: str
    layer: str  # "structural" or "grounding"
    level: str  # critical, expected, aspirational
    passed: bool
    explanation: str
    supporting_spans: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PlanEvaluationResult:
    """Complete evaluation results for a plan."""
    scenario_id: str
    quality_level: str
    structural_results: List[AssertionResult]
    grounding_results: List[AssertionResult]
    structural_score: float  # % passed
    grounding_score: float  # % passed
    overall_verdict: str  # "pass", "fail_structure", "fail_grounding", "fail_both"
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "structural_results": [r.to_dict() for r in self.structural_results],
            "grounding_results": [r.to_dict() for r in self.grounding_results]
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Authentication
# ═══════════════════════════════════════════════════════════════════════════════

def get_substrate_token() -> str:
    """Get authentication token for Substrate API using MSAL broker."""
    global _jj_token_cache
    
    if _jj_token_cache:
        return _jj_token_cache
    
    try:
        import msal
    except ImportError:
        print("Error: msal[broker] not installed. Run: pip install msal[broker]")
        raise
    
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        enable_broker_on_windows=True,
    )
    
    scopes = [f"{SUBSTRATE_RESOURCE}/.default"]
    
    # Try silent auth first
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            _jj_token_cache = result["access_token"]
            return _jj_token_cache
    
    # Fall back to interactive
    print("🔐 Authenticating with Microsoft (browser may open)...")
    
    kernel32 = ctypes.windll.kernel32
    hwnd = kernel32.GetConsoleWindow()
    
    result = app.acquire_token_interactive(
        scopes,
        parent_window_handle=hwnd,
    )
    
    if "access_token" in result:
        _jj_token_cache = result["access_token"]
        return _jj_token_cache
    else:
        raise Exception(f"Authentication failed: {result.get('error_description', result)}")


# ═══════════════════════════════════════════════════════════════════════════════
# API Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def call_gpt5_api(
    prompt: str,
    system_prompt: str = None,
    temperature: float = 0.3,
    max_tokens: int = 4000,
    max_retries: int = MAX_RETRIES
) -> str:
    """
    Call Substrate GPT-5 JJ API with retry logic.
    
    Args:
        prompt: User prompt
        system_prompt: Optional system prompt
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        max_retries: Number of retries on rate limit
        
    Returns:
        Response text from the model
    """
    import requests
    
    token = get_substrate_token()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-ModelType": JJ_MODEL
    }
    
    payload = {
        "model": JJ_MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                SUBSTRATE_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            elif response.status_code == 429:
                wait_time = (attempt + 1) * 10
                print(f"  ⏳ Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise Exception(f"GPT-5 API error {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print(f"  ⏳ Request timeout, retrying...")
            time.sleep(5)
    
    raise Exception(f"GPT-5 API failed after {max_retries} retries")


def extract_json_from_response(response: str) -> Dict:
    """Extract JSON from a GPT response that may contain markdown."""
    import re
    
    # Try to find JSON in code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_str = response.strip()
    
    # Clean up common issues
    json_str = json_str.strip()
    if json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    
    return json.loads(json_str)


# ═══════════════════════════════════════════════════════════════════════════════
# File I/O Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def save_json(data: Any, filepath: str) -> None:
    """Save data to JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  💾 Saved: {filepath}")


def load_json(filepath: str) -> Any:
    """Load data from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def file_exists(filepath: str) -> bool:
    """Check if file exists."""
    return os.path.exists(filepath)
