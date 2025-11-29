# GPT-5 Q&A Prompts Archive

This directory stores all GPT-5 Q&A sessions organized by date.

## Directory Structure

```
gpt5_prompts/
├── README.md
├── 2025-11-29/
│   ├── session_001.json
│   ├── session_002.json
│   └── ...
├── 2025-11-30/
│   └── session_001.json
└── ...
```

## Session File Format

Each session JSON file contains:

```json
{
  "session_id": "session_001",
  "created_at": "2025-11-29T10:30:00",
  "system_prompt": "You are a helpful AI assistant...",
  "exchanges": [
    {
      "question": "Your question here",
      "answer": "GPT-5's response",
      "timestamp": "2025-11-29T10:30:15"
    }
  ]
}
```

## Usage

### Interactive Mode
```powershell
python tools/gpt5_qa.py
```

### Single Question
```powershell
python tools/gpt5_qa.py -q "What is the best practice for error handling in Python?"
```

### Question from File
```powershell
python tools/gpt5_qa.py --prompt-file my_question.txt
```

### With Custom System Prompt
```powershell
python tools/gpt5_qa.py --system "You are a Python expert" -q "How to implement a decorator?"
```

### List Recent Sessions
```powershell
python tools/gpt5_qa.py --list-sessions
python tools/gpt5_qa.py --list-sessions --days 14  # Last 14 days
```

### View a Session
```powershell
python tools/gpt5_qa.py --view-session 2025-11-29/session_001.json
```

## Interactive Commands

When in interactive mode:
- `/quit` or `/exit` - End session and save
- `/save` - Save current session
- `/clear` - Clear conversation history
- `/system <prompt>` - Change system prompt
- `/history` - Show conversation history

## Author

Chin-Yew Lin  
Created: November 29, 2025
