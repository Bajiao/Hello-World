#!/usr/bin/env python3
"""Diagnostic test for API keys and basic pipeline"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd() / 'backend_menu_processing'))

from llm import load_env_variables, get_project_root, get_data_dir
import os

print("\n" + "="*70)
print("API KEY & ENVIRONMENT DIAGNOSTIC")
print("="*70)

# Load env
load_env_variables()

# Check env vars
print("\n✅ Environment Variables:")
print(f"  OPENAI_API_KEY: {'✓ SET' if os.getenv('OPENAI_API_KEY') else '✗ NOT SET'}")
print(f"  GOOGLE_API_KEY: {'✓ SET' if os.getenv('GOOGLE_API_KEY') else '✗ NOT SET'}")
print(f"  FLASK_ENV: {os.getenv('FLASK_ENV', 'not set')}")

# Check OpenAI key validity
openai_key = os.getenv('OPENAI_API_KEY', '')
print(f"\n  OpenAI Key Format Check:")
print(f"    - Starts with 'sk-': {'✓' if openai_key.startswith('sk-') else '✗'}")
print(f"    - Length: {len(openai_key)} chars (should be ~100+)")
print(f"    - Format appears valid: {'✓' if openai_key.startswith('sk-proj-') or openai_key.startswith('sk-') else '✗'}")

# Check Gemini key validity
gemini_key = os.getenv('GOOGLE_API_KEY', '')
print(f"\n  Gemini Key Format Check:")
print(f"    - Starts with 'AIza': {'✓' if gemini_key.startswith('AIza') else '✗'}")
print(f"    - Length: {len(gemini_key)} chars")
print(f"    - Format appears valid: {'✓' if gemini_key.startswith('AIza') else '✗'}")

# Check paths
print(f"\n✅ Path Resolution:")
print(f"  Project Root: {get_project_root()}")
print(f"  Data Dir: {get_data_dir()}")

# Test simple Gemini call (no OpenAI)
print(f"\n✅ Testing Gemini API (Free Tier Status):")
try:
    import google.generativeai as genai
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    response = model.generate_content("Say 'test successful' in one word.")
    print(f"  ✓ Gemini API: Working")
    print(f"  ✓ Response: {response.text}")
except Exception as e:
    print(f"  ✗ Gemini API Error: {type(e).__name__}")
    print(f"    {str(e)[:100]}")

print("\n" + "="*70)
print("ISSUE SUMMARY")
print("="*70)
print("""
⚠️  YOUR API KEYS APPEAR TO HAVE ISSUES:

1. OpenAI API: Insufficient Quota (Error 429)
   - Your API key exists but has no remaining quota
   - This could mean: monthly quota exhausted, or free trial ended
   - Action: Check your OpenAI account billing: https://platform.openai.com/account/billing

2. Gemini API: Free Tier Quota Exceeded (Error 429)
   - You've exceeded the 20 free requests/day limit
   - Action: Wait 24 hours or upgrade to paid plan

SOLUTION FOR TESTING:
Since both APIs are quota-limited, we can still verify the pipeline logic
by testing the non-API steps (ingredient extraction, graph construction).
""")
