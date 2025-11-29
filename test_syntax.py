#!/usr/bin/env python3
"""
Simple syntax check for main.py without running the full app
"""
import ast
import sys

def check_syntax(filename):
    """Check if Python file has valid syntax"""
    try:
        with open(filename, 'r') as f:
            code = f.read()
        ast.parse(code)
        print(f"✅ {filename} - Syntax is valid!")
        return True
    except SyntaxError as e:
        print(f"❌ {filename} - Syntax Error:")
        print(f"   Line {e.lineno}: {e.msg}")
        print(f"   {e.text}")
        return False
    except Exception as e:
        print(f"❌ {filename} - Error: {e}")
        return False

if __name__ == "__main__":
    files_to_check = [
        "backend/main.py",
        "backend/services/discord_service.py",
        "backend/services/prompt_template.py",
        "backend/services/gemini_service.py",
        "backend/services/youtube_service.py",
    ]
    
    all_valid = True
    for file in files_to_check:
        if not check_syntax(file):
            all_valid = False
    
    if all_valid:
        print("\n🎉 All files have valid syntax!")
        sys.exit(0)
    else:
        print("\n💥 Some files have syntax errors!")
        sys.exit(1)
