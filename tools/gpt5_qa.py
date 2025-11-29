#!/usr/bin/env python3
"""
GPT-5 Q&A Tool - Interactive and batch question-answering with GPT-5 JJ

This tool provides:
- Interactive Q&A sessions with GPT-5
- Batch processing from prompt files
- Automatic logging of all Q&A pairs organized by date
- Support for system prompts and conversation context

Usage:
    # Interactive mode
    python tools/gpt5_qa.py
    
    # Single question
    python tools/gpt5_qa.py --question "What is the best practice for..."
    
    # Question from file
    python tools/gpt5_qa.py --prompt-file prompts/my_question.txt
    
    # With custom system prompt
    python tools/gpt5_qa.py --system "You are a Python expert" --question "How to..."
    
    # List recent Q&A sessions
    python tools/gpt5_qa.py --list-sessions
    
    # View a specific session
    python tools/gpt5_qa.py --view-session 2025-11-29/session_001.json

Author: Chin-Yew Lin
Date: November 29, 2025
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, Dict, List, Any

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from pipeline.config import (
    get_substrate_token,
    call_gpt5_api,
    DELAY_BETWEEN_CALLS,
)

# =============================================================================
# CONFIGURATION
# =============================================================================

GPT5_PROMPTS_DIR = os.path.join(PROJECT_ROOT, "gpt5_prompts")
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant with expertise in software development, 
data analysis, and technical documentation. Provide clear, accurate, and well-structured responses."""

# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

def get_today_dir() -> str:
    """Get today's directory path for storing Q&A sessions."""
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = os.path.join(GPT5_PROMPTS_DIR, today)
    os.makedirs(today_dir, exist_ok=True)
    return today_dir


def get_next_session_number(today_dir: str) -> int:
    """Get the next session number for today."""
    existing = [f for f in os.listdir(today_dir) if f.startswith("session_") and f.endswith(".json")]
    if not existing:
        return 1
    numbers = []
    for f in existing:
        try:
            num = int(f.replace("session_", "").replace(".json", ""))
            numbers.append(num)
        except ValueError:
            pass
    return max(numbers) + 1 if numbers else 1


def create_session(system_prompt: str = DEFAULT_SYSTEM_PROMPT) -> Dict[str, Any]:
    """Create a new Q&A session."""
    today_dir = get_today_dir()
    session_num = get_next_session_number(today_dir)
    session_id = f"session_{session_num:03d}"
    
    session = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "system_prompt": system_prompt,
        "exchanges": []
    }
    
    return session


def save_session(session: Dict[str, Any]) -> str:
    """Save session to file and return the file path."""
    today_dir = get_today_dir()
    session_file = os.path.join(today_dir, f"{session['session_id']}.json")
    
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session, f, indent=2, ensure_ascii=False)
    
    return session_file


def load_session(session_path: str) -> Optional[Dict[str, Any]]:
    """Load a session from file."""
    full_path = os.path.join(GPT5_PROMPTS_DIR, session_path)
    if not os.path.exists(full_path):
        # Try as absolute path
        full_path = session_path
    
    if not os.path.exists(full_path):
        print(f"Session not found: {session_path}")
        return None
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_sessions(days: int = 7) -> List[Dict[str, Any]]:
    """List recent sessions from the last N days."""
    sessions = []
    
    if not os.path.exists(GPT5_PROMPTS_DIR):
        return sessions
    
    # Get date directories
    date_dirs = sorted([
        d for d in os.listdir(GPT5_PROMPTS_DIR) 
        if os.path.isdir(os.path.join(GPT5_PROMPTS_DIR, d)) and d.startswith("20")
    ], reverse=True)
    
    for date_dir in date_dirs[:days]:
        dir_path = os.path.join(GPT5_PROMPTS_DIR, date_dir)
        session_files = sorted([
            f for f in os.listdir(dir_path) 
            if f.startswith("session_") and f.endswith(".json")
        ])
        
        for sf in session_files:
            session_path = os.path.join(date_dir, sf)
            session = load_session(session_path)
            if session:
                sessions.append({
                    "path": session_path,
                    "session_id": session.get("session_id"),
                    "created_at": session.get("created_at"),
                    "num_exchanges": len(session.get("exchanges", [])),
                    "first_question": session.get("exchanges", [{}])[0].get("question", "")[:80] + "..." if session.get("exchanges") else ""
                })
    
    return sessions


# =============================================================================
# Q&A FUNCTIONS
# =============================================================================

def ask_gpt5(
    question: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    context: Optional[List[Dict]] = None,
    temperature: float = 0.3,
    max_tokens: int = 4000,
    verbose: bool = True
) -> str:
    """
    Ask GPT-5 a question and return the response.
    
    Args:
        question: The question to ask
        system_prompt: System prompt for context
        context: Previous Q&A exchanges for conversation context
        temperature: Model temperature (0-1)
        max_tokens: Maximum tokens in response
        verbose: Print status messages
        
    Returns:
        The GPT-5 response text
    """
    if verbose:
        print(f"\n{'='*60}")
        print(f"Question: {question[:100]}{'...' if len(question) > 100 else ''}")
        print(f"{'='*60}")
        print("Calling GPT-5...")
    
    # Build full prompt with context if provided
    full_prompt = question
    if context:
        # Include conversation history in the prompt
        history_parts = []
        for exchange in context:
            history_parts.append(f"User: {exchange.get('question', '')}")
            history_parts.append(f"Assistant: {exchange.get('answer', '')}")
        history_str = "\n\n".join(history_parts)
        full_prompt = f"Previous conversation:\n{history_str}\n\nCurrent question:\n{question}"
    
    try:
        response = call_gpt5_api(
            prompt=full_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        if verbose:
            print(f"\nResponse received ({len(response)} chars)")
        
        return response
        
    except Exception as e:
        error_msg = f"Error calling GPT-5: {str(e)}"
        if verbose:
            print(f"\n❌ {error_msg}")
        return error_msg


def interactive_session(system_prompt: str = DEFAULT_SYSTEM_PROMPT, verbose: bool = True):
    """Run an interactive Q&A session."""
    print("\n" + "="*60)
    print("GPT-5 Interactive Q&A Session")
    print("="*60)
    print(f"System prompt: {system_prompt[:80]}...")
    print("\nCommands:")
    print("  /quit or /exit - End session")
    print("  /save - Save session to file")
    print("  /clear - Clear conversation history")
    print("  /system <prompt> - Change system prompt")
    print("  /history - Show conversation history")
    print("="*60 + "\n")
    
    session = create_session(system_prompt)
    
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if not question:
                continue
            
            # Handle commands
            if question.lower() in ['/quit', '/exit']:
                if session["exchanges"]:
                    save_path = save_session(session)
                    print(f"\n✅ Session saved to: {save_path}")
                print("Goodbye!")
                break
            
            elif question.lower() == '/save':
                save_path = save_session(session)
                print(f"\n✅ Session saved to: {save_path}")
                continue
            
            elif question.lower() == '/clear':
                session["exchanges"] = []
                print("\n✅ Conversation history cleared")
                continue
            
            elif question.lower().startswith('/system '):
                new_prompt = question[8:].strip()
                session["system_prompt"] = new_prompt
                print(f"\n✅ System prompt updated to: {new_prompt[:80]}...")
                continue
            
            elif question.lower() == '/history':
                if not session["exchanges"]:
                    print("\n(No conversation history)")
                else:
                    print("\n--- Conversation History ---")
                    for i, ex in enumerate(session["exchanges"], 1):
                        print(f"\n[{i}] Q: {ex['question'][:100]}...")
                        print(f"    A: {ex['answer'][:100]}...")
                continue
            
            # Regular question
            answer = ask_gpt5(
                question=question,
                system_prompt=session["system_prompt"],
                context=session["exchanges"] if session["exchanges"] else None,
                verbose=False
            )
            
            # Store exchange
            exchange = {
                "question": question,
                "answer": answer,
                "timestamp": datetime.now().isoformat()
            }
            session["exchanges"].append(exchange)
            
            print(f"\nGPT-5: {answer}")
            
        except KeyboardInterrupt:
            print("\n\nSession interrupted.")
            if session["exchanges"]:
                save_path = save_session(session)
                print(f"✅ Session saved to: {save_path}")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def single_question(
    question: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    save: bool = True,
    verbose: bool = True
) -> str:
    """Ask a single question and optionally save to session."""
    answer = ask_gpt5(question, system_prompt, verbose=verbose)
    
    if save:
        session = create_session(system_prompt)
        session["exchanges"].append({
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })
        save_path = save_session(session)
        if verbose:
            print(f"\n✅ Saved to: {save_path}")
    
    return answer


def process_prompt_file(
    prompt_file: str,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    verbose: bool = True
) -> str:
    """Process a question from a file."""
    if not os.path.exists(prompt_file):
        print(f"❌ Prompt file not found: {prompt_file}")
        return ""
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        question = f.read().strip()
    
    if verbose:
        print(f"Loaded question from: {prompt_file}")
    
    return single_question(question, system_prompt, save=True, verbose=verbose)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="GPT-5 Q&A Tool - Interactive and batch question-answering",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/gpt5_qa.py                           # Interactive mode
  python tools/gpt5_qa.py -q "What is Python?"      # Single question
  python tools/gpt5_qa.py --prompt-file q.txt       # Question from file
  python tools/gpt5_qa.py --list-sessions           # List recent sessions
  python tools/gpt5_qa.py --view-session 2025-11-29/session_001.json
        """
    )
    
    parser.add_argument('-q', '--question', type=str, help='Single question to ask')
    parser.add_argument('-f', '--prompt-file', type=str, help='File containing the question')
    parser.add_argument('-s', '--system', type=str, default=DEFAULT_SYSTEM_PROMPT,
                        help='System prompt for context')
    parser.add_argument('--list-sessions', action='store_true', help='List recent Q&A sessions')
    parser.add_argument('--view-session', type=str, help='View a specific session')
    parser.add_argument('--days', type=int, default=7, help='Number of days to list (default: 7)')
    parser.add_argument('--no-save', action='store_true', help='Do not save single question to session')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Ensure prompts directory exists
    os.makedirs(GPT5_PROMPTS_DIR, exist_ok=True)
    
    # List sessions
    if args.list_sessions:
        sessions = list_sessions(args.days)
        if not sessions:
            print("No sessions found.")
        else:
            print(f"\n{'='*80}")
            print(f"Recent Q&A Sessions (last {args.days} days)")
            print(f"{'='*80}")
            for s in sessions:
                print(f"\n📁 {s['path']}")
                print(f"   Created: {s['created_at']}")
                print(f"   Exchanges: {s['num_exchanges']}")
                if s['first_question']:
                    print(f"   First Q: {s['first_question']}")
        return
    
    # View specific session
    if args.view_session:
        session = load_session(args.view_session)
        if session:
            print(f"\n{'='*80}")
            print(f"Session: {session['session_id']}")
            print(f"Created: {session['created_at']}")
            print(f"System Prompt: {session['system_prompt'][:100]}...")
            print(f"{'='*80}")
            
            for i, ex in enumerate(session.get('exchanges', []), 1):
                print(f"\n--- Exchange {i} ({ex.get('timestamp', 'N/A')}) ---")
                print(f"\n📝 Question:\n{ex['question']}")
                print(f"\n🤖 Answer:\n{ex['answer']}")
        return
    
    # Single question from argument
    if args.question:
        answer = single_question(
            args.question,
            args.system,
            save=not args.no_save,
            verbose=True
        )
        print(f"\n{'='*60}")
        print("Answer:")
        print(f"{'='*60}")
        print(answer)
        return
    
    # Question from file
    if args.prompt_file:
        answer = process_prompt_file(args.prompt_file, args.system, verbose=True)
        print(f"\n{'='*60}")
        print("Answer:")
        print(f"{'='*60}")
        print(answer)
        return
    
    # Default: Interactive mode
    interactive_session(args.system, verbose=True)


if __name__ == "__main__":
    main()
