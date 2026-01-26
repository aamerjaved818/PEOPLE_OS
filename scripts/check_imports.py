import os
import re

def check_imports():
    files_to_check = [
        "d:/Project/PEOPLE_OS/src/AuthenticatedApp.tsx",
        "d:/Project/PEOPLE_OS/src/App.tsx"
    ]
    src_dir = "d:/Project/PEOPLE_OS/src"
    
    for file_path in files_to_check:
        print(f"--- Checking {file_path} ---")
        if not os.path.exists(file_path):
            print(f"Error: {file_path} not found")
            continue

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex for imports
    # const Module = React.lazy(() => import('./modules/dashboard'));
    # import { ... } from './contexts/RBACContext';
    imports = re.findall(r"from ['\"]([^'\"]+)['\"]", content)
    lazy_imports = re.findall(r"import\(['\"]([^'\"]+)['\"]\)", content)
    
    all_imports = set(imports + lazy_imports)
    
    for imp in all_imports:
        if imp.startswith('.'):
            # Check relative path
            target = os.path.join(os.path.dirname(file_path), imp)
            
            # Potential extensions
            possible_files = [
                target + ".tsx",
                target + ".ts",
                target + ".js",
                target + ".jsx",
                os.path.join(target, "index.tsx"),
                os.path.join(target, "index.ts"),
            ]
            
            exists = any(os.path.exists(f) for f in possible_files)
            if not exists:
                print(f"MISSING: {imp} -> {target}")
        elif imp.startswith('@/'):
            # Check alias path
            target = os.path.join(src_dir, imp[2:])
            possible_files = [
                target + ".tsx",
                target + ".ts",
                target + ".js",
                target + ".jsx",
                os.path.join(target, "index.tsx"),
                os.path.join(target, "index.ts"),
            ]
            exists = any(os.path.exists(f) for f in possible_files)
            if not exists:
                print(f"MISSING ALIAS: {imp} -> {target}")
        else:
            # Likely a node_module
            pass

if __name__ == "__main__":
    check_imports()
