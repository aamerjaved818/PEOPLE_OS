"""
UI/UX & Design System Compliance Analyzer
Checks design token usage, component reuse, accessibility.
"""

import re
import uuid
from typing import Dict

from ..models import AuditFinding, DimensionScore
from ..utils import calculate_score, get_project_root


class UIUXAnalyzer:
    """Analyzes UI/UX quality and design system compliance"""

    def __init__(self):
        self.project_root = get_project_root()

    def analyze(self) -> Dict:
        """Run UI/UX analysis"""
        findings = []
        metrics = {
            "hardcoded_colors": 0,
            "hardcoded_spacing": 0,
            "theme_context_usage": 0,
            "standard_component_usage": 0,
            "accessibility_violations": 0,
            "css_files": 0,
            "responsive_layouts": 0,
        }

        # Check for hardcoded styles in TSX files
        modules_dir = self.project_root / "src" / "modules"
        components_dir = self.project_root / "src" / "components"

        tsx_files = []
        if modules_dir.exists():
            tsx_files.extend(
                [
                    p
                    for p in modules_dir.rglob("*.tsx")
                    if not p.name.endswith(".test.tsx")
                    and not p.name.endswith(".spec.tsx")
                ]
            )
        if components_dir.exists():
            tsx_files.extend(
                [
                    p
                    for p in components_dir.rglob("*.tsx")
                    if not p.name.endswith(".test.tsx")
                    and not p.name.endswith(".spec.tsx")
                ]
            )

        core_components = ["Button", "Card", "Input", "Select", "Modal", "GlassCard"]

        for tsx_file in tsx_files:
            try:
                content = tsx_file.read_text(encoding="utf-8")

                # Check for hardcoded colors (hex, rgb)
                hex_colors = len(re.findall(
                    r'["\']#[0-9A-Fa-f]{3,6}["\']', content
                ))
                rgb_colors = len(re.findall(r"rgb\(", content))
                metrics["hardcoded_colors"] += hex_colors + rgb_colors

                # Check for hardcoded spacing/sizing
                content_no_tailwind = re.sub(r"\[[^\]]+\]", "", content)
                px_values = len(re.findall(r"\d+px", content_no_tailwind))
                metrics["hardcoded_spacing"] += max(0, px_values)

                # Check for theme context usage
                if "useTheme" in content or "ThemeContext" in content:
                    metrics["theme_context_usage"] += 1

                # Check for standard component usage
                for comp in core_components:
                    if f"<{comp}" in content:
                        metrics["standard_component_usage"] += 1
                        break

                # Check for basic accessibility
                if "aria-label" not in content and "alt=" not in content:
                    if "<button" in content or "<img" in content or "<input" in content:
                        metrics["accessibility_violations"] += 1

                # Check for responsive design utilities
                responsive_utils = len(
                    re.findall(r"(sm:|md:|lg:|xl:|2xl:|@media)", content)
                )
                if responsive_utils > 0:
                    metrics["responsive_layouts"] += 1

            except Exception:
                pass

        # Count CSS files
        if modules_dir.exists():
            metrics["css_files"] = len(list(modules_dir.rglob("*.css")))

        # Component reuse estimation
        if components_dir.exists():
            metrics["component_reuse"] = len(list(components_dir.rglob("*.tsx")))

        # Generate findings
        if metrics["hardcoded_colors"] > 30:
            findings.append(
                AuditFinding(
                    id=str(uuid.uuid4()),
                    dimension="UI/UX",
                    severity="Minor",
                    title=f"{metrics['hardcoded_colors']} hardcoded color values detected",
                    description="Colors should use design tokens/CSS variables from the theme palette.",
                    recommendation="Migrate hardcoded colors to '@/theme/palette' tokens.",
                )
            )

        if metrics["theme_context_usage"] < len(tsx_files) * 0.1:
            findings.append(
                AuditFinding(
                    id=str(uuid.uuid4()),
                    dimension="UI/UX",
                    severity="Major",
                    title="Low Theme Centralization",
                    description="Very few components are interacting with ThemeContext/useTheme.",
                    recommendation="Utilize useTheme hook for dynamic styling and theme consistency.",
                )
            )

        if metrics["standard_component_usage"] < len(tsx_files) * 0.1:
             findings.append(
                AuditFinding(
                    id=str(uuid.uuid4()),
                    dimension="UI/UX",
                    severity="Major",
                    title="Standard Component Underutilization",
                    description="Many components appear to use raw HTML instead of core UI components.",
                    recommendation="Replace raw HTML elements with standardized components from '@/components/ui'.",
                )
            )

        if metrics["accessibility_violations"] > 50:
            findings.append(
                AuditFinding(
                    id=str(uuid.uuid4()),
                    dimension="UI/UX",
                    severity="Major",
                    title=f"{metrics['accessibility_violations']} components lack critical accessibility attributes",
                    description="Missing aria-labels or alt text on interactive/media elements.",
                    recommendation="Add ARIA labels and alt text to improve accessibility compliance.",
                )
            )

        # Calculate score
        score = calculate_score(
            {
                "hardcoded_colors": max(0, 5 - (metrics["hardcoded_colors"] / 30)),
                "theme_centralization": min(5, (metrics["theme_context_usage"] / max(1, len(tsx_files) * 0.2)) * 5),
                "component_consistency": min(5, (metrics["standard_component_usage"] / max(1, len(tsx_files) * 0.5)) * 5),
                "accessibility": max(0, 5 - (metrics["accessibility_violations"] / 5)),
                "responsiveness": min(5, (metrics["responsive_layouts"] / max(1, len(tsx_files))) * 10),
            }
        )

        return {
            "score": DimensionScore(
                dimension="UI/UX",
                score=score,
                findings_count=len(findings),
                details=metrics,
            ),
            "findings": findings,
        }
