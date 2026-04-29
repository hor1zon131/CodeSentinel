"""
Example: Python file with intentional bugs for CodeSentinel demo
Run: python code_review_agent.py examples/buggy_example.py --fix
"""

import os, sys, json
from pathlib import *

# ── Bug 1: Wildcard import (above) ──────────────────────────────────────────

DATABASE_PASSWORD = "super_secret_123"   # Bug 2: Hardcoded credential
API_KEY = "sk-1234567890abcdef"          # Bug 3: Hardcoded API key


def divide_numbers(a, b):
    return a / b                          # Bug 4: No zero-division guard


def calculate_stats(data):
    total = 0
    for item in data:
        total = total + item
    average = total / len(data)           # Bug 5: Crashes on empty list
    maximum = max(data)
    minimum = min(data)
    return {"avg": average, "max": maximum, "min": minimum}


def fetch_user(user_id):
    # Bug 6: SQL injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return query


def read_config(path):
    f = open(path)                        # Bug 7: File not closed (use 'with')
    content = f.read()
    return content


def process_items(items):
    results = []
    for i in range(len(items)):           # Bug 8: Not Pythonic, use enumerate
        item = items[i]
        try:
            processed = int(item) * 2
            results.append(processed)
        except:                           # Bug 9: Bare except
            pass                          # Bug 10: Silently swallows errors
    return results


def send_email(to, subject, body):
    # Bug 11: Unused parameter `body`
    print(f"Sending email to {to}: {subject}")
    return True


unused_constant = 42                      # Bug 12: Unused variable
another_unused = "hello"                  # Bug 13: Unused variable


class DataProcessor:
    def __init__(self):
        self.data = []
        self.cache = {}

    def add(self, item):
        self.data.append(item)

    def get_by_index(self, index):
        return self.data[index]            # Bug 14: No bounds check

    def clear(self):
        self.data = []
        self.cache = {}


if __name__ == "__main__":
    dp = DataProcessor()
    dp.add(10)
    dp.add(20)
    print(dp.get_by_index(0))
    print(calculate_stats([1, 2, 3]))
