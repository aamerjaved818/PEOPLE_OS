"""
Semgrep Integration Module - Static Analysis & Pattern Matching

Integrates with Semgrep for:
- Custom security rule matching
- OWASP pattern detection
- Code quality issues
- 100+ built-in rules
- Custom rule support
"""

import json
import subprocess
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path
import asyncio


class SemgrepSeverity(Enum):
    """Semgrep severity levels"""
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    NOTE = "NOTE"


@dataclass
class SemgrepMatch:
    """Semgrep pattern match result"""
    rule_id: str
    message: str
    severity: SemgrepSeverity
    path: str
    start_line: int
    end_line: int
    start_col: int
    end_col: int
    code_snippet: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'rule_id': self.rule_id,
            'message': self.message,
            'severity': self.severity.value,
            'path': self.path,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'start_col': self.start_col,
            'end_col': self.end_col,
            'code_snippet': self.code_snippet,
            'metadata': self.metadata or {},
        }


class SemgrepAnalyzer:
    """Wrapper for Semgrep static analysis"""

    def __init__(self, target_path: str = "backend", config: Optional[str] = None):
        self.target_path = target_path
        self.config = config or "p/security-audit"  # Default Semgrep ruleset
        self.matches: List[SemgrepMatch] = []
        self.errors: List[str] = []
        self.metrics: Dict[str, Any] = {}

    async def analyze(self) -> List[SemgrepMatch]:
        """
        Run Semgrep analysis on target path
        
        Args:
            None - uses initialized target_path
            
        Returns:
            List of pattern matches
        """
        self.matches = []
        self.errors = []
        
        # Build semgrep command
        cmd = [
            'semgrep',
            '--config', self.config,
            '--json',
            '--quiet',
            self.target_path,
        ]
        
        try:
            result = await self._run_semgrep(cmd)
            if result:
                self._parse_semgrep_output(result)
        except Exception as e:
            self.errors.append(str(e))
        
        return self.matches

    async def _run_semgrep(self, cmd: List[str]) -> Optional[str]:
        """Run semgrep command asynchronously"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=60.0
            )
            return stdout.decode('utf-8')
        except asyncio.TimeoutError:
            self.errors.append("Semgrep analysis timeout")
            return None
        except FileNotFoundError:
            self.errors.append("Semgrep not installed. Install with: pip install semgrep")
            return None

    def _parse_semgrep_output(self, output: str):
        """Parse Semgrep JSON output"""
        try:
            data = json.loads(output)
            
            # Process results
            for result in data.get('results', []):
                try:
                    severity = SemgrepSeverity[result.get('extra', {}).get('severity', 'WARNING')]
                except KeyError:
                    severity = SemgrepSeverity.WARNING
                
                match = SemgrepMatch(
                    rule_id=result.get('check_id', 'unknown'),
                    message=result.get('extra', {}).get('message', result.get('message', '')),
                    severity=severity,
                    path=result.get('path', 'unknown'),
                    start_line=result.get('start', {}).get('line', 0),
                    end_line=result.get('end', {}).get('line', 0),
                    start_col=result.get('start', {}).get('col', 0),
                    end_col=result.get('end', {}).get('col', 0),
                    metadata=result.get('extra', {}),
                )
                self.matches.append(match)
        except json.JSONDecodeError:
            self.errors.append("Failed to parse Semgrep output")

    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        by_severity = {severity.value: 0 for severity in SemgrepSeverity}
        by_rule = {}
        
        for match in self.matches:
            by_severity[match.severity.value] += 1
            by_rule[match.rule_id] = by_rule.get(match.rule_id, 0) + 1
        
        return {
            'total_matches': len(self.matches),
            'by_severity': by_severity,
            'by_rule': by_rule,
            'errors': self.errors,
            'matches': [m.to_dict() for m in self.matches],
        }


def get_semgrep_analyzer(target_path: str = "backend", config: Optional[str] = None) -> SemgrepAnalyzer:
    """Get or create Semgrep analyzer instance"""
    key = f"semgrep_{target_path}_{config}"
    if not hasattr(get_semgrep_analyzer, '_instances'):
        get_semgrep_analyzer._instances = {}
    
    if key not in get_semgrep_analyzer._instances:
        get_semgrep_analyzer._instances[key] = SemgrepAnalyzer(target_path, config)
    
    return get_semgrep_analyzer._instances[key]
