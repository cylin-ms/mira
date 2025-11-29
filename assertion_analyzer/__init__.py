"""
Assertion Analyzer - Self-contained package for WBP assertion analysis.

This package provides:
- GPT-5 based assertion classification (29 dimensions: S1-S20 + G1-G9)
- Scenario generation for assertion context
- Workback Plan (WBP) generation with S+G linkage
- WBP verification against scenario ground truth

Usage:
    # As a module - full analysis with WBP
    from assertion_analyzer import analyze_assertion, AssertionAnalyzer
    result = analyze_assertion("Your assertion text here")
    
    # Lightweight classification only (no WBP)
    from assertion_analyzer import classify_assertion
    result = classify_assertion("Your assertion text here")
    
    # From command line
    python -m assertion_analyzer "Your assertion text here"
"""

from .analyzer import (
    analyze_assertion,
    classify_assertion,
    AssertionAnalyzer,
    generate_scenario_for_assertion,
    generate_wbp_with_scenario,
    verify_wbp_against_scenario,
)

from .config import (
    call_gpt5_api,
    extract_json_from_response,
    get_substrate_token,
)

from .dimensions import (
    S_TO_G_MAP,
    G_RATIONALE_FOR_S,
    DIMENSION_NAMES,
    STRUCTURAL_DIMENSIONS,
    GROUNDING_DIMENSIONS,
)

__version__ = "2.1.0"
__all__ = [
    "analyze_assertion",
    "classify_assertion",
    "AssertionAnalyzer",
    "generate_scenario_for_assertion",
    "generate_wbp_with_scenario",
    "verify_wbp_against_scenario",
    "call_gpt5_api",
    "extract_json_from_response",
    "get_substrate_token",
    "S_TO_G_MAP",
    "G_RATIONALE_FOR_S",
    "DIMENSION_NAMES",
    "STRUCTURAL_DIMENSIONS",
    "GROUNDING_DIMENSIONS",
]
