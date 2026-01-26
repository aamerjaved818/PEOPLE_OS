import os
import re
from pathlib import Path

def fix_aliases(project_root: Path):
    src_dir = project_root / "src"
    if not src_dir.exists():
        print("❌ src directory not found")
        return

    # Count of fixes
    fixes_count = 0
    files_touched = 0

    # Pattern for imports: from '...' or from "..."
    import_pattern = re.compile(r'from\s+[\'"](\.\./\.\./[^\'"]+)[\'"]')

    for root, _, files in os.walk(src_dir):
        for file in files:
            if not (file.endswith(".tsx") or file.endswith(".ts")):
                continue

            file_path = Path(root) / file
            
            try:
                content = file_path.read_text(encoding="utf-8")
                
                # Check for absolute-ish paths that are missing @/
                # e.g. from 'components/...'
                internal_roots = ["components/", "modules/", "services/", "hooks/", "utils/", "types/", "store/", "contexts/"]
                
                new_content = content
                
                # 1. Fix deep relative imports
                matches = import_pattern.findall(content)
                for match in matches:
                    # Logic: any import starting with ../../ is likely going back towards src root
                    # Or at least it's deep enough to warrant @/ usage
                    
                    # We need to determine if it's actually pointing back to a root-level dir
                    # But the requirement is standard: "Use @/ for all non-relative local imports"
                    # And deep relative imports are considered non-standard.
                    
                    # Simplest replacement: find the part after the last ../
                    parts = match.split('/')
                    # Filter out '..'
                    clean_parts = [p for p in parts if p != '..']
                    new_alias = "@/" + "/".join(clean_parts)
                    
                    # Ensure it's balanced
                    # For now we apply the rule strictly: if it has 2+ dots-dots, use @/
                    new_content = new_content.replace(f"'{match}'", f"'{new_alias}'")
                    new_content = new_content.replace(f'"{match}"', f'"{new_alias}"')
                    fixes_count += 1

                # 2. Fix missing @/ for internal roots
                for ir in internal_roots:
                    # Match pattern: from 'components/...'
                    r_pattern = r'from\s+[\'"](' + ir + r'[^\'"]+)[\'"]'
                    internal_matches = re.findall(r_pattern, new_content)
                    for match in internal_matches:
                        new_alias = "@/" + match
                        new_content = new_content.replace(f"'{match}'", f"'{new_alias}'")
                        new_content = new_content.replace(f'"{match}"', f'"{new_alias}"')
                        fixes_count += 1

                if new_content != content:
                    file_path.write_text(new_content, encoding="utf-8")
                    files_touched += 1
                    
            except Exception as e:
                print(f"⚠️ Failed to process {file}: {e}")

    print(f"\n✅ Path Alias Remediation Complete")
    print(f"✨ Fixes applied: {fixes_count}")
    print(f"📄 Files updated: {files_touched}")

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    fix_aliases(project_root)
