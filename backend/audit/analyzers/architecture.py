import ast
import os
import re
import uuid
from pathlib import Path
from typing import Dict, List, Set, Tuple

from ..models import AuditFinding, DimensionScore


class ArchitectureAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.violations: List[Dict[str, str]] = []

    def analyze(self) -> Dict[str, any]:
        """
        Main entry point for the analyzer.
        Returns result dict compatible with AuditEngine.
        """
        print("    🔍 Scanning architecture dependencies...")
        self._build_dependency_graph()
        cycles = self._detect_circular_dependencies()
        # Check boundaries
        self._check_module_boundaries()
        self._check_path_aliases()
        self._check_module_internal_structure()

        # Calculate stats
        total_modules = len(self.dependency_graph)
        total_edges = sum(len(deps) for deps in self.dependency_graph.values())

        findings = []
        for cycle in cycles:
            findings.append(
                AuditFinding(
                    id=str(uuid.uuid4()),
                    dimension="Architecture",
                    severity="Major",
                    title="Circular Dependency Detected",
                    description=f"Cycle detected: {' -> '.join(cycle)}",
                    recommendation="Refactor modules to break the dependency cycle.",
                )
            )

        for violation in self.violations:
            findings.append(
                AuditFinding(
                    id=str(uuid.uuid4()),
                    dimension="Architecture",
                    severity="Major",
                    title=violation.get("title", "Architecture Violation"),
                    description=violation["description"],
                    recommendation=violation.get("recommendation", "Follow project architecture standards."),
                )
            )

        cycle_count = len(cycles)
        violation_count = len(self.violations)

        # update score calculation to include all violations
        score_val = self._calculate_score(cycle_count, violation_count)

        score = DimensionScore(
            dimension="Architecture",
            score=score_val,
            findings_count=len(findings),
            details={
                "cycle_count": cycle_count,
                "architecture_violations": violation_count,
                "modules_scanned": total_modules,
                "dependency_edges": total_edges,
            },
        )

        return {"findings": findings, "score": score}

    def _calculate_score(self, cycle_count: int, violation_count: int) -> float:
        total = cycle_count + (violation_count / 2)  # Violations count less than cycles
        if total == 0:
            return 5.0
        elif total < 3:
            return 4.0
        elif total < 6:
            return 3.0
        elif total < 10:
            return 2.0
        else:
            return 1.0

    def _build_dependency_graph(self):
        """
        Scans all .py and .ts/.tsx files to build an import graph.
        """
        for root, _, files in os.walk(self.project_root):
            if (
                "node_modules" in root
                or "venv" in root
                or ".venv" in root
                or ".env-project" in root
                or ".git" in root
                or "__pycache__" in root
                or "dist" in root
                or "build" in root
                or "scripts" in root
            ):
                continue

            for file in files:
                file_path = Path(root) / file
                if file.endswith(".py"):
                    self._parse_python_imports(file_path)
                elif file.endswith(".ts") or file.endswith(".tsx"):
                    self._parse_typescript_imports(file_path)

    def _parse_python_imports(self, file_path: Path):
        try:
            rel_path = str(file_path.relative_to(self.project_root)).replace("\\", "/")
            if rel_path not in self.dependency_graph:
                self.dependency_graph[rel_path] = set()

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.dependency_graph[rel_path].add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.dependency_graph[rel_path].add(node.module)
        except Exception:
            # Skip files that fail to parse (e.g. syntax errors)
            pass

    def _parse_typescript_imports(self, file_path: Path):
        try:
            rel_path = str(file_path.relative_to(self.project_root)).replace("\\", "/")
            if rel_path not in self.dependency_graph:
                self.dependency_graph[rel_path] = set()

            # Catch both import x from '...' and import '...'
            import_pattern = re.compile(r'import\s+.*?from\s+[\'"](.*?)[\'"]|import\s+[\'"](.*?)[\'"]')

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for match in import_pattern.finditer(content):
                import_target = match.group(1) or match.group(2)
                if import_target:
                    # Ignore external libraries (node_modules) and standard libs
                    # Only track relative paths or alias paths
                    if import_target.startswith(".") or import_target.startswith("/") or import_target.startswith("@"):
                        self.dependency_graph[rel_path].add(import_target)
        except Exception:
            pass

    def _detect_circular_dependencies(self) -> List[List[str]]:
        """
        Standard DFS cycle detection.
        Returns a list of cycles found (each cycle is a list of node names).
        """
        visited = set()
        recursion_stack = set()
        cycles = []

        # Optimization: Pre-map suffixes to keys to avoid O(N^2) in DFS
        key_map = {}
        for key in self.dependency_graph.keys():
            # For Python: 'backend/main.py' -> 'backend/main'
            if key.endswith(".py"):
                name = key[:-3]
                key_map[name] = key
            # For TS: 'src/modules/auth/index.tsx' -> 'src/modules/auth/index'
            elif key.endswith(".tsx"):
                name = key[:-4]
                key_map[name] = key
            elif key.endswith(".ts"):
                name = key[:-3]
                key_map[name] = key
            
            # Use basename too
            basename = key.split("/")[-1].split(".")[0]
            if basename not in key_map:
                key_map[basename] = key

        def dfs(node, path):
            visited.add(node)
            recursion_stack.add(node)
            path.append(node)

            if node in self.dependency_graph:
                for neighbor in self.dependency_graph[node]:
                    # Quick resolution via key_map
                    target_node = key_map.get(neighbor)
                    if not target_node:
                        # Try with .py replacement
                        target_node = key_map.get(neighbor.replace(".", "/"))

                    if target_node:
                        if target_node not in visited:
                            dfs(target_node, path)
                        elif target_node in recursion_stack:
                            # Cycle detected
                            cycle_start_index = path.index(target_node)
                            cycles.append(path[cycle_start_index:].copy())

            recursion_stack.remove(node)
            path.pop()

        for node in list(self.dependency_graph.keys()):
            if node not in visited:
                dfs(node, [])

        return cycles

    def _check_module_boundaries(self):
        """
        Enforce clean architecture module boundaries.
        """
        for source, deps in self.dependency_graph.items():
            if "src/modules/" not in source:
                continue

            try:
                source_module = source.split("src/modules/")[1].split("/")[0]
            except IndexError:
                continue

            for target in deps:
                if "src/modules/" not in target and "modules/" not in target:
                    continue

                try:
                    if "src/modules/" in target:
                        target_module = target.split("src/modules/")[1].split("/")[0]
                    else:
                        target_module = target.split("modules/")[1].split("/")[0]
                except IndexError:
                    continue

                if source_module == target_module:
                    continue

                # Violation: Importing deep into another module
                if "/components/" in target or "/utils/" in target or "/hooks/" in target:
                    self.violations.append(
                        {
                            "source": source,
                            "target": target,
                            "title": "Module Boundary Violation",
                            "description": f"Module '{source_module}' imports private internal '{target}' from '{target_module}'.",
                            "recommendation": f"Import from '@/modules/{target_module}' instead of deep internal paths."
                        }
                    )

    def _check_path_aliases(self):
        """
        Ensure imports use @/ aliases for non-relative local imports.
        """
        for source, deps in self.dependency_graph.items():
            if not source.startswith("src/"):
                continue

            for target in deps:
                # If it starts with ../../ but it's going back to src root, it should be @/
                if target.startswith("..") and target.count("../") >= 2:
                    self.violations.append({
                        "source": source,
                        "target": target,
                        "title": "Path Alias Violation",
                        "description": f"Deep relative import '{target}' found in '{source}'.",
                        "recommendation": "Use '@/' path aliases for cleaner imports."
                    })
                
                # Check for absolute-like paths that are missing @/
                if not target.startswith(".") and not target.startswith("@/") and "/" in target:
                    # Potential internal path without alias
                    if target.startswith("components/") or target.startswith("modules/") or target.startswith("services/"):
                        self.violations.append({
                            "source": source,
                            "target": target,
                            "title": "Path Alias Violation",
                            "description": f"Absolute-style import '{target}' without '@/' alias in '{source}'.",
                            "recommendation": f"Add '@/' prefix: '@/ {target}'"
                        })

    def _check_module_internal_structure(self):
        """
        Enforce standard module structure.
        """
        modules_root = self.project_root / "src" / "modules"
        if not modules_root.exists():
            return

        allowed_dirs = {"components", "hooks", "utils", "types", "submodules", "services", "config"}
        
        for module_dir in modules_root.iterdir():
            if not module_dir.is_dir():
                continue
            
            # Check for index.tsx
            if not (module_dir / "index.tsx").exists():
                 self.violations.append({
                    "source": str(module_dir),
                    "target": "index.tsx",
                    "title": "Missing Module Entry Point",
                    "description": f"Module '{module_dir.name}' is missing 'index.tsx'.",
                    "recommendation": "Add 'index.tsx' as the public entry point for the module."
                })

            # Check subdirectories
            for sub_item in module_dir.iterdir():
                if sub_item.is_dir():
                    if sub_item.name not in allowed_dirs:
                        self.violations.append({
                            "source": str(sub_item),
                            "target": sub_item.name,
                            "title": "Non-Standard Module Structure",
                            "description": f"Directory '{sub_item.name}' in module '{module_dir.name}' is not standard.",
                            "recommendation": f"Use standard directory names: {', '.join(allowed_dirs)}."
                        })
