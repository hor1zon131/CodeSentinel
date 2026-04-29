"""
CodeSentinel Agent - Multi-Agent Code Review & Auto-Fix System
Uses Anthropic Claude with tool_use for deep code analysis
"""

import anthropic
import ast
import subprocess
import os
import json
from pathlib import Path
from typing import Optional

client = anthropic.Anthropic()
MODEL = "claude-opus-4-5"

# ─────────────────────────── Tools Definition ────────────────────────────────

TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a source code file",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to the file to read"}
            },
            "required": ["filepath"]
        }
    },
    {
        "name": "analyze_syntax",
        "description": "Analyze Python syntax and detect errors in the code",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code to analyze"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "run_linter",
        "description": "Run pyflakes linter on code snippet to detect issues",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Python source code to lint"},
                "filename": {"type": "string", "description": "Filename for context", "default": "snippet.py"}
            },
            "required": ["code"]
        }
    },
    {
        "name": "apply_fix",
        "description": "Write the fixed code to a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "filepath": {"type": "string", "description": "Path to write the fixed code"},
                "code": {"type": "string", "description": "Fixed source code to write"}
            },
            "required": ["filepath", "code"]
        }
    },
    {
        "name": "generate_report",
        "description": "Generate a structured JSON review report",
        "input_schema": {
            "type": "object",
            "properties": {
                "issues": {
                    "type": "array",
                    "description": "List of issues found",
                    "items": {
                        "type": "object",
                        "properties": {
                            "severity": {"type": "string", "enum": ["critical", "warning", "info"]},
                            "line": {"type": "integer"},
                            "description": {"type": "string"},
                            "suggestion": {"type": "string"}
                        }
                    }
                },
                "summary": {"type": "string"},
                "score": {"type": "integer", "description": "Code quality score 0-100"}
            },
            "required": ["issues", "summary", "score"]
        }
    }
]

# ─────────────────────────── Tool Implementations ────────────────────────────

def read_file(filepath: str) -> str:
    try:
        return Path(filepath).read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {e}"

def analyze_syntax(code: str) -> dict:
    try:
        ast.parse(code)
        return {"valid": True, "errors": []}
    except SyntaxError as e:
        return {
            "valid": False,
            "errors": [{"line": e.lineno, "message": str(e.msg), "text": e.text}]
        }

def run_linter(code: str, filename: str = "snippet.py") -> str:
    tmp = Path(f"/tmp/{filename}")
    tmp.write_text(code)
    try:
        result = subprocess.run(
            ["python", "-m", "pyflakes", str(tmp)],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout + result.stderr
        return output.replace(str(tmp), filename) if output.strip() else "No issues found by linter."
    except FileNotFoundError:
        # pyflakes not installed, do basic checks
        issues = []
        for i, line in enumerate(code.splitlines(), 1):
            if "import *" in line:
                issues.append(f"{filename}:{i}: wildcard import detected")
            if line.strip().startswith("except:") and "except:" == line.strip():
                issues.append(f"{filename}:{i}: bare except clause")
        return "\n".join(issues) if issues else "Linter not available; basic checks passed."
    except Exception as e:
        return f"Linter error: {e}"

def apply_fix(filepath: str, code: str) -> str:
    try:
        Path(filepath).write_text(code, encoding="utf-8")
        return f"✅ Fixed code written to {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"

def generate_report(issues: list, summary: str, score: int) -> str:
    report = {
        "summary": summary,
        "quality_score": score,
        "total_issues": len(issues),
        "issues": issues
    }
    return json.dumps(report, indent=2, ensure_ascii=False)

# ─────────────────────────── Tool Dispatcher ─────────────────────────────────

def dispatch_tool(name: str, inputs: dict) -> str:
    if name == "read_file":
        return read_file(inputs["filepath"])
    elif name == "analyze_syntax":
        return json.dumps(analyze_syntax(inputs["code"]))
    elif name == "run_linter":
        return run_linter(inputs["code"], inputs.get("filename", "snippet.py"))
    elif name == "apply_fix":
        return apply_fix(inputs["filepath"], inputs["code"])
    elif name == "generate_report":
        return generate_report(inputs["issues"], inputs["summary"], inputs["score"])
    else:
        return f"Unknown tool: {name}"

# ─────────────────────────── Agentic Loop ────────────────────────────────────

def run_agent(code_or_path: str, auto_fix: bool = False) -> dict:
    """
    Run the multi-step code review agent.
    Returns dict with report and optionally fixed code.
    """
    # Determine if input is a file path or raw code
    if os.path.isfile(code_or_path):
        user_message = f"Please review the code in the file: {code_or_path}"
        if auto_fix:
            user_message += f"\nAfter reviewing, apply fixes and save back to: {code_or_path}"
    else:
        user_message = f"Please review this Python code:\n\n```python\n{code_or_path}\n```"
        if auto_fix:
            user_message += "\nAfter reviewing, provide the fixed version."

    messages = [{"role": "user", "content": user_message}]

    system_prompt = """You are CodeSentinel, an expert Python code review agent.
Your job is to:
1. Read and understand the code thoroughly
2. Analyze it for syntax errors, logic issues, security vulnerabilities, and style problems
3. Run the linter to catch additional issues
4. Generate a detailed structured report with a quality score
5. If requested, apply fixes automatically

Be thorough, precise, and always explain WHY something is an issue.
Use your tools in a logical sequence to provide the best analysis."""

    print("🤖 CodeSentinel Agent starting...\n")
    final_report = None
    iterations = 0
    max_iterations = 10

    while iterations < max_iterations:
        iterations += 1
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        # Collect assistant message
        assistant_content = response.content
        messages.append({"role": "assistant", "content": assistant_content})

        if response.stop_reason == "end_turn":
            # Extract final text
            for block in assistant_content:
                if hasattr(block, "text"):
                    print(f"✅ Agent complete:\n{block.text}")
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in assistant_content:
                if block.type == "tool_use":
                    print(f"🔧 Using tool: {block.name}({list(block.input.keys())})")
                    result = dispatch_tool(block.name, block.input)

                    # Capture report if generated
                    if block.name == "generate_report":
                        try:
                            final_report = json.loads(result)
                        except Exception:
                            pass

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return {
        "report": final_report,
        "messages": len(messages),
        "iterations": iterations
    }

# ─────────────────────────── CLI Entry Point ─────────────────────────────────

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python code_review_agent.py <file_or_code> [--fix]")
        sys.exit(1)

    target = sys.argv[1]
    auto_fix = "--fix" in sys.argv

    result = run_agent(target, auto_fix=auto_fix)
    if result["report"]:
        print("\n📊 Final Report:")
        print(json.dumps(result["report"], indent=2, ensure_ascii=False))
