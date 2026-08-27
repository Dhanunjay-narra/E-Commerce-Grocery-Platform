"""Comprehensive Codebase Expansion Script for FreshCart Platform.
Generates complete, production-grade domain modules, frontend components, and mobile architecture.
"""
import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def write_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    ensure_dir(os.path.dirname(full_path))
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"  [+] Wrote {rel_path} ({len(content.splitlines()):,} lines)")

print("[*] Starting Full Production Codebase Generation...")
