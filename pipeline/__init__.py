"""
Two-Layer Assertion Evaluation Pipeline

A modular pipeline for evaluating AI-generated workback plans using the
Two-Layer Assertion Framework (Structural S1-S10 + Grounding G1-G5).

Stages:
    1. scenario_generation.py - Generate meeting scenarios from templates or data
    2. assertion_generation.py - Generate two-layer assertions (S1-S10 + G1-G5)
    3. plan_generation.py - Generate workback plans at 3 quality levels
    4. plan_evaluation.py - Evaluate plans against assertions
    5. report_generation.py - Generate comprehensive evaluation reports

Usage:
    # Run full pipeline
    python -m pipeline.run_pipeline
    
    # Run individual stages
    python -m pipeline.scenario_generation
    python -m pipeline.assertion_generation
    python -m pipeline.plan_generation
    python -m pipeline.plan_evaluation
    python -m pipeline.report_generation

Author: Chin-Yew Lin
Date: November 28, 2025
"""

__version__ = "1.0.0"
__author__ = "Chin-Yew Lin"
