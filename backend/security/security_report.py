"""
Security Report Generator - Unified Security Analysis Results

Combines results from:
- OWASP Scanner
- Bandit Analyzer
- Semgrep Analyzer

Generates comprehensive security reports and dashboards
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import asyncio
from pathlib import Path

from backend.security.security_scanner import SecurityScanner, get_security_scanner
from backend.security.bandit_analyzer import BanditAnalyzer, get_bandit_analyzer
from backend.security.semgrep_analyzer import SemgrepAnalyzer, get_semgrep_analyzer


class ReportFormat(Enum):
    """Security report format"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class SecurityMetrics:
    """Aggregated security metrics"""
    total_vulnerabilities: int
    total_issues: int
    total_matches: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    risk_score: float  # 0-100
    timestamp: str


class SecurityReport:
    """Unified security report combining all scanners"""

    def __init__(self):
        self.owasp_scanner = get_security_scanner()
        self.bandit_analyzer = get_bandit_analyzer()
        self.semgrep_analyzer = get_semgrep_analyzer()
        self.metrics: Optional[SecurityMetrics] = None
        self.generated_at: Optional[str] = None

    async def generate_report(self, target_path: str = "backend") -> Dict[str, Any]:
        """
        Generate comprehensive security report
        
        Args:
            target_path: Path to analyze
            
        Returns:
            Complete security report
        """
        self.generated_at = datetime.utcnow().isoformat()
        
        # Run all scanners in parallel
        tasks = [
            self._run_owasp_scan(target_path),
            self.bandit_analyzer.analyze(),
            self.semgrep_analyzer.analyze(),
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate metrics
        self.metrics = self._calculate_metrics()
        
        return {
            'generated_at': self.generated_at,
            'target': target_path,
            'metrics': asdict(self.metrics),
            'owasp': self.owasp_scanner.get_summary(),
            'bandit': self.bandit_analyzer.get_summary(),
            'semgrep': self.semgrep_analyzer.get_summary(),
            'summary': self._generate_summary(),
        }

    async def _run_owasp_scan(self, target_path: str):
        """Run OWASP security scan on Python files"""
        target = Path(target_path)
        python_files = list(target.rglob('*.py'))
        
        # Skip common non-critical files
        exclude_patterns = ['__pycache__', '.venv', 'venv', 'test_', 'migrations']
        python_files = [
            f for f in python_files 
            if not any(pattern in str(f) for pattern in exclude_patterns)
        ]
        
        for file_path in python_files[:50]:  # Limit to first 50 files for performance
            try:
                code = file_path.read_text()
                await self.owasp_scanner.scan_python_code(code, str(file_path))
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")

    def _calculate_metrics(self) -> SecurityMetrics:
        """Calculate security metrics"""
        owasp_summary = self.owasp_scanner.get_summary()
        bandit_summary = self.bandit_analyzer.get_summary()
        semgrep_summary = self.semgrep_analyzer.get_summary()
        
        # Count by severity
        critical = (
            owasp_summary['by_level'].get('critical', 0) +
            bandit_summary['by_severity'].get('HIGH', 0) +
            semgrep_summary['by_severity'].get('CRITICAL', 0)
        )
        
        high = (
            owasp_summary['by_level'].get('high', 0) +
            semgrep_summary['by_severity'].get('ERROR', 0)
        )
        
        medium = (
            owasp_summary['by_level'].get('medium', 0) +
            semgrep_summary['by_severity'].get('WARNING', 0)
        )
        
        low = (
            owasp_summary['by_level'].get('low', 0) +
            semgrep_summary['by_severity'].get('NOTE', 0)
        )
        
        info = owasp_summary['by_level'].get('info', 0)
        
        # Calculate risk score (0-100)
        risk_score = min(
            100,
            (critical * 10 + high * 7 + medium * 4 + low * 2 + info * 0.5) / 10
        )
        
        return SecurityMetrics(
            total_vulnerabilities=owasp_summary['total_vulnerabilities'],
            total_issues=bandit_summary['total_issues'],
            total_matches=semgrep_summary['total_matches'],
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            info_count=info,
            risk_score=round(risk_score, 2),
            timestamp=self.generated_at or datetime.utcnow().isoformat(),
        )

    def _generate_summary(self) -> str:
        """Generate text summary of findings"""
        if not self.metrics:
            return "No metrics available"
        
        summary = f"""
SECURITY REPORT SUMMARY
=======================

Risk Score: {self.metrics.risk_score}/100

Vulnerability Counts:
  Critical: {self.metrics.critical_count}
  High: {self.metrics.high_count}
  Medium: {self.metrics.medium_count}
  Low: {self.metrics.low_count}
  Info: {self.metrics.info_count}

Scanner Results:
  OWASP: {self.metrics.total_vulnerabilities} vulnerabilities
  Bandit: {self.metrics.total_issues} issues
  Semgrep: {self.metrics.total_matches} matches

Generated: {self.metrics.timestamp}
"""
        return summary.strip()

    def export_json(self, report: Dict[str, Any], filepath: str = "security_report.json"):
        """Export report as JSON"""
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

    def export_markdown(self, report: Dict[str, Any], filepath: str = "security_report.md"):
        """Export report as Markdown"""
        content = f"""# Security Audit Report

Generated: {report['generated_at']}
Target: {report['target']}

## Risk Assessment

**Overall Risk Score: {report['metrics']['risk_score']}/100**

## Vulnerability Summary

| Severity | Count |
|----------|-------|
| Critical | {report['metrics']['critical_count']} |
| High | {report['metrics']['high_count']} |
| Medium | {report['metrics']['medium_count']} |
| Low | {report['metrics']['low_count']} |
| Info | {report['metrics']['info_count']} |

## OWASP Scanner Results

Total Vulnerabilities: {report['owasp']['total_vulnerabilities']}

### Breakdown by Type
"""
        for vtype, count in report['owasp']['by_level'].items():
            content += f"- {vtype}: {count}\n"

        content += "\n## Bandit Analysis Results\n\n"
        content += f"Total Issues: {report['bandit']['total_issues']}\n\n"
        content += "### Breakdown by Severity\n"
        for severity, count in report['bandit']['by_severity'].items():
            content += f"- {severity}: {count}\n"

        content += "\n## Semgrep Pattern Matches\n\n"
        content += f"Total Matches: {report['semgrep']['total_matches']}\n\n"
        content += "### Breakdown by Severity\n"
        for severity, count in report['semgrep']['by_severity'].items():
            content += f"- {severity}: {count}\n"

        content += f"\n## Summary\n\n{report['summary']}\n"

        with open(filepath, 'w') as f:
            f.write(content)

    def export_html(self, report: Dict[str, Any], filepath: str = "security_report.html"):
        """Export report as HTML"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Security Audit Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ color: #0066cc; margin-top: 30px; }}
        .risk-score {{
            font-size: 48px;
            color: #d32f2f;
            font-weight: bold;
            text-align: center;
            padding: 20px;
            background: #ffe0e0;
            border-radius: 8px;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{ background: #0066cc; color: white; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .critical {{ color: #d32f2f; font-weight: bold; }}
        .high {{ color: #f57c00; font-weight: bold; }}
        .medium {{ color: #fbc02d; }}
        .low {{ color: #388e3c; }}
        .metric {{ display: inline-block; margin: 10px 20px; text-align: center; }}
        .metric-value {{ font-size: 32px; font-weight: bold; color: #0066cc; }}
        .metric-label {{ color: #666; }}
        .footer {{ margin-top: 40px; text-align: center; color: #999; border-top: 1px solid #ddd; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Security Audit Report</h1>
        <p><strong>Generated:</strong> {report['generated_at']}</p>
        <p><strong>Target:</strong> {report['target']}</p>

        <div class="risk-score">
            Risk Score: {report['metrics']['risk_score']}/100
        </div>

        <h2>Vulnerability Summary</h2>
        <div style="display: flex; flex-wrap: wrap; justify-content: space-around;">
            <div class="metric">
                <div class="metric-value critical">{report['metrics']['critical_count']}</div>
                <div class="metric-label">Critical</div>
            </div>
            <div class="metric">
                <div class="metric-value high">{report['metrics']['high_count']}</div>
                <div class="metric-label">High</div>
            </div>
            <div class="metric">
                <div class="metric-value medium">{report['metrics']['medium_count']}</div>
                <div class="metric-label">Medium</div>
            </div>
            <div class="metric">
                <div class="metric-value low">{report['metrics']['low_count']}</div>
                <div class="metric-label">Low</div>
            </div>
            <div class="metric">
                <div class="metric-value">{report['metrics']['info_count']}</div>
                <div class="metric-label">Info</div>
            </div>
        </div>

        <h2>Scanner Results</h2>
        <table>
            <tr>
                <th>Scanner</th>
                <th>Total Issues</th>
            </tr>
            <tr>
                <td>OWASP</td>
                <td>{report['owasp']['total_vulnerabilities']}</td>
            </tr>
            <tr>
                <td>Bandit</td>
                <td>{report['bandit']['total_issues']}</td>
            </tr>
            <tr>
                <td>Semgrep</td>
                <td>{report['semgrep']['total_matches']}</td>
            </tr>
        </table>

        <div class="footer">
            <p>Security Audit Report | Generated on {report['generated_at']}</p>
        </div>
    </div>
</body>
</html>
"""
        with open(filepath, 'w') as f:
            f.write(html)


def get_security_report() -> SecurityReport:
    """Get or create security report instance"""
    if not hasattr(get_security_report, '_instance'):
        get_security_report._instance = SecurityReport()
    return get_security_report._instance
