"""
Multi-Agent Orchestrator for CodeSentinel
Coordinates specialized sub-agents: Reviewer, Fixer, Explainer
"""

import anthropic
import json
from typing import Optional

client = anthropic.Anthropic()
MODEL = "claude-opus-4-5"


def reviewer_agent(code: str) -> dict:
    """Sub-agent specialized in finding issues."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system="""You are a strict code reviewer. Analyze the code and return ONLY a JSON object with:
{
  "issues": [{"severity": "critical|warning|info", "line": N, "description": "...", "category": "security|performance|style|logic|bug"}],
  "score": 0-100
}
No extra text, just JSON.""",
        messages=[{"role": "user", "content": f"Review this code:\n```python\n{code}\n```"}]
    )
    try:
        text = response.content[0].text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text)
    except Exception:
        return {"issues": [], "score": 50}


def fixer_agent(code: str, issues: list) -> str:
    """Sub-agent specialized in fixing issues."""
    issues_text = "\n".join(
        f"- Line {i.get('line', '?')}: [{i['severity']}] {i['description']}"
        for i in issues
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        system="You are an expert Python developer. Return ONLY the fixed Python code, no explanations, no markdown fences.",
        messages=[{
            "role": "user",
            "content": f"Fix these issues in the code:\n{issues_text}\n\nOriginal code:\n```python\n{code}\n```"
        }]
    )
    fixed = response.content[0].text.strip()
    # Remove markdown if present
    if fixed.startswith("```python"):
        fixed = fixed[9:]
    if fixed.startswith("```"):
        fixed = fixed[3:]
    if fixed.endswith("```"):
        fixed = fixed[:-3]
    return fixed.strip()


def explainer_agent(code: str, issues: list, fixed_code: str) -> str:
    """Sub-agent that writes a human-readable explanation."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system="You are a helpful coding mentor. Write a clear, concise explanation of what was wrong and what was fixed.",
        messages=[{
            "role": "user",
            "content": f"""Original code had {len(issues)} issues. 
Issues: {json.dumps(issues, indent=2)}
Write a friendly explanation of the key problems found and the improvements made."""
        }]
    )
    return response.content[0].text


def orchestrate(code: str, auto_fix: bool = True) -> dict:
    """
    Orchestrate multiple specialized agents to review and fix code.
    
    Flow:
    1. Reviewer Agent → finds all issues
    2. Fixer Agent → applies fixes (if auto_fix=True)  
    3. Explainer Agent → generates human-readable report
    """
    print("🎯 Orchestrator: Starting multi-agent pipeline...\n")

    # Step 1: Review
    print("👁️  Agent 1 (Reviewer): Analyzing code...")
    review = reviewer_agent(code)
    issues = review.get("issues", [])
    score = review.get("score", 0)
    print(f"   Found {len(issues)} issues | Score: {score}/100\n")

    fixed_code = None
    explanation = ""

    # Step 2: Fix (if issues found)
    if auto_fix and issues:
        critical = [i for i in issues if i.get("severity") == "critical"]
        warnings = [i for i in issues if i.get("severity") == "warning"]
        print(f"🔧 Agent 2 (Fixer): Fixing {len(critical)} critical + {len(warnings)} warnings...")
        fixed_code = fixer_agent(code, issues)
        print("   Fix applied ✅\n")

    # Step 3: Explain
    print("📝 Agent 3 (Explainer): Generating explanation...")
    explanation = explainer_agent(code, issues, fixed_code or code)
    print("   Done ✅\n")

    return {
        "original_score": score,
        "issues_found": len(issues),
        "issues": issues,
        "fixed_code": fixed_code,
        "explanation": explanation,
        "pipeline": "reviewer → fixer → explainer"
    }


if __name__ == "__main__":
    # Demo with intentionally buggy code
    BUGGY_CODE = '''
import os, sys
from pathlib import *

def calculate_average(numbers):
    total = 0
    for n in numbers:
        total = total + n
    average = total / len(numbers)  # Bug: division by zero if empty list
    return average

def read_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"  # SQL injection
    password = "admin123"  # Hardcoded secret
    return query

def process_files(directory):
    files = os.listdir(directory)
    for f in files:
        try:
            data = open(f).read()  # File not closed properly
            print(data)
        except:  # Bare except
            pass

unused_variable = "this is never used"
'''

    print("=" * 60)
    print("CodeSentinel Multi-Agent Demo")
    print("=" * 60)
    print("\n📄 Input code (intentionally buggy):\n")
    print(BUGGY_CODE)
    print("\n" + "=" * 60 + "\n")

    result = orchestrate(BUGGY_CODE, auto_fix=True)

    print("\n📊 RESULTS")
    print("=" * 60)
    print(f"Quality Score: {result['original_score']}/100")
    print(f"Issues Found: {result['issues_found']}")
    print(f"\n🔍 Issues:")
    for issue in result["issues"]:
        emoji = "🔴" if issue["severity"] == "critical" else "🟡" if issue["severity"] == "warning" else "🔵"
        print(f"  {emoji} Line {issue.get('line', '?')}: {issue['description']}")

    if result["fixed_code"]:
        print(f"\n✅ Fixed Code:\n{'-'*40}\n{result['fixed_code']}")

    print(f"\n💬 Explanation:\n{result['explanation']}")
