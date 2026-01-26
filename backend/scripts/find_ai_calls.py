import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.audit.ast_utils import analyze_file

def main():
    project_root = Path(__file__).parent.parent.parent
    code_files = list(project_root.rglob("*.py"))
    
    # Filter out excluded paths
    code_files = [
        f for f in code_files 
        if "node_modules" not in str(f) 
        and "venv" not in str(f) 
        and ".venv" not in str(f)
        and ".env-project" not in str(f)
        and "audit" not in str(f)
    ]
    
    print(f"Scanning {len(code_files)} files...")
    for f in code_files:
        try:
            calls, _ = analyze_file(f)
            if calls:
                print(f"\nFound {len(calls)} AI calls in {f.relative_to(project_root)}:")
                for call in calls:
                    print(f"  - Line {call.line_number}: {call.function_name} (Temp: {call.temperature}, Grounding: {call.has_grounding})")
        except Exception as e:
            # print(f"Error scanning {f}: {e}")
            pass

if __name__ == "__main__":
    main()
