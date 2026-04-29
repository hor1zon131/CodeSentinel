# 🛡️ CodeSentinel — Multi-Agent Code Review & Auto-Fix System

> An AI-powered code review system built with Anthropic Claude, using multi-agent collaboration and tool_use to automatically detect, explain, and fix code issues.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Anthropic Claude](https://img.shields.io/badge/powered%20by-Claude%20claude--opus--4--5-orange)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

- **🔍 Deep Code Analysis** — Detects bugs, security vulnerabilities, style issues, and logic errors
- **🤖 Multi-Agent Pipeline** — Specialized agents collaborate: Reviewer → Fixer → Explainer
- **🔧 Auto-Fix** — Automatically rewrites and saves corrected code
- **📊 Quality Score** — Returns a 0–100 code quality score with detailed issue breakdown
- **🛠️ Tool Use** — Uses Claude's `tool_use` feature for structured, reliable outputs
- **⚡ Agentic Loop** — Iterative reasoning with up to 10 tool-use steps per review

---

## 🏗️ Architecture

```
User Input (file or raw code)
        │
        ▼
┌─────────────────────────────────────────┐
│           Orchestrator                  │
│  (multi_agent_orchestrator.py)          │
└───────┬─────────────────────────────────┘
        │
   ┌────▼────┐    ┌──────────┐    ┌───────────┐
   │Reviewer │───▶│  Fixer   │───▶│ Explainer │
   │ Agent   │    │  Agent   │    │  Agent    │
   └─────────┘    └──────────┘    └───────────┘
        │
        ▼
  Tools Available:
  ├── read_file        ← reads source files
  ├── analyze_syntax   ← AST-based syntax check
  ├── run_linter       ← pyflakes integration
  ├── apply_fix        ← writes fixed code to disk
  └── generate_report  ← structured JSON output
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/code-sentinel.git
cd code-sentinel
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 3. Run a Review

```bash
# Review a file
python agent/code_review_agent.py examples/buggy_example.py

# Review and auto-fix
python agent/code_review_agent.py examples/buggy_example.py --fix

# Run full multi-agent pipeline demo
python agent/multi_agent_orchestrator.py
```

---

## 📖 Usage

### Single-Agent Mode (with Tool Use)

```python
from agent.code_review_agent import run_agent

result = run_agent("examples/buggy_example.py", auto_fix=True)
print(result["report"])
```

### Multi-Agent Orchestration

```python
from agent.multi_agent_orchestrator import orchestrate

code = """
def divide(a, b):
    return a / b  # no zero check

password = "admin123"  # hardcoded secret
"""

result = orchestrate(code, auto_fix=True)
print(f"Score: {result['original_score']}/100")
print(f"Fixed:\n{result['fixed_code']}")
```

---

## 🔍 What It Detects

| Category | Examples |
|----------|---------|
| 🐛 **Bugs** | Division by zero, index out of bounds, empty list crashes |
| 🔒 **Security** | SQL injection, hardcoded credentials, wildcard imports |
| 💨 **Performance** | Inefficient loops, unclosed files, unnecessary operations |
| 🎨 **Style** | Unused variables, bare except clauses, non-Pythonic patterns |
| 🧠 **Logic** | Unreachable code, swallowed exceptions, missing return values |

---

## 📊 Sample Output

```json
{
  "summary": "Code has critical security vulnerabilities and several bugs",
  "quality_score": 34,
  "total_issues": 8,
  "issues": [
    {
      "severity": "critical",
      "line": 12,
      "description": "SQL injection: user input directly in query string",
      "suggestion": "Use parameterized queries"
    },
    {
      "severity": "critical",
      "line": 4,
      "description": "Hardcoded API key exposed in source code",
      "suggestion": "Use environment variables"
    },
    {
      "severity": "warning",
      "line": 18,
      "description": "Division by zero when list is empty",
      "suggestion": "Add len(data) == 0 guard"
    }
  ]
}
```

---

## 🧠 How It Works

### Tool Use Agentic Loop

The single-agent mode uses Claude's `tool_use` to run a multi-step loop:

1. **Claude decides** which tool to call next
2. **Tool executes** (read file, lint, analyze syntax, etc.)
3. **Result returned** to Claude's context
4. **Repeat** until Claude has enough info to generate the final report

This ensures Claude doesn't hallucinate — every piece of analysis is grounded in real tool output.

### Multi-Agent Collaboration

Three specialized Claude instances work in sequence:

- **Reviewer**: Strict, focused only on finding problems → returns structured JSON
- **Fixer**: Expert developer persona → rewrites code to fix detected issues
- **Explainer**: Friendly mentor persona → writes human-readable summary

Each agent has a focused system prompt, keeping responses high-quality and on-task.

---

## 📁 Project Structure

```
code-sentinel/
├── agent/
│   ├── code_review_agent.py       # Single agent with tool_use loop
│   └── multi_agent_orchestrator.py # Multi-agent pipeline
├── examples/
│   └── buggy_example.py           # Demo file with 14 intentional bugs
├── requirements.txt
└── README.md
```

---

## 🔧 Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |

---

## 📈 Token Usage

Typical token consumption per review:

| Mode | Input Tokens | Output Tokens |
|------|-------------|---------------|
| Single file (<100 lines) | ~2,000 | ~1,500 |
| Multi-agent pipeline | ~6,000 | ~3,000 |

---

## 🤝 Contributing

PRs welcome! Ideas for extension:
- Add JavaScript/TypeScript support
- GitHub Actions integration (PR review bot)
- VS Code extension
- Web dashboard for team reviews

---

## 📄 License

MIT © 2025
