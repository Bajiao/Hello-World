#!/usr/bin/env python3
"""Quick verification that test files have correct paths"""
import sys
from pathlib import Path

# Test path setup from test/ folder
test_file_path = Path(__file__)
backend_path = test_file_path.parent.parent / 'backend_menu_processing'

print("\n" + "="*70)
print("PATH VERIFICATION")
print("="*70)
print(f"Test file location: {test_file_path}")
print(f"Backend module path: {backend_path}")
print(f"Backend module exists: {backend_path.exists()}")

# Try importing
sys.path.insert(0, str(backend_path))
try:
    from llm import load_env_variables
    print("\n✅ Successfully imported llm module")
    print("✅ Test files have correct paths!")
except ImportError as e:
    print(f"\n❌ Import failed: {e}")

print("="*70 + "\n")
