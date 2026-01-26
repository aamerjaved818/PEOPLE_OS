"""
Bandit Integration Module - Code Security Analysis

Integrates with Bandit for detecting security issues in Python code:
- Hardcoded SQL strings
- Use of assert for validation
- Insecure hash functions
- SQL injection patterns
- Insecure random number generation
- Logging sensitive information
- Pickle usage with untrusted data
"""

import json
import subprocess
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
from pathlib import Path
import asyncio


class BanditSeverity(Enum):
    """Bandit severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class BanditIssue:
    """Bandit security issue"""
    issue_severity: BanditSeverity
    issue_confidence: str
    issue_type: str
    issue_text: str
    line_number: int
    filename: str
    test_id: str
    line_range: List[int]
    code_snippet: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'severity': self.issue_severity.value,
            'confidence': self.issue_confidence,
            'type': self.issue_type,
            'text': self.issue_text,
            'line': self.line_number,
            'filename': self.filename,
            'test_id': self.test_id,
            'line_range': self.line_range,
            'code_snippet': self.code_snippet,
        }


class BanditAnalyzer:
    """Wrapper for Bandit security analysis"""

    def __init__(self, target_path: str = "backend"):
        self.target_path = target_path
        self.issues: List[BanditIssue] = []
        self.metrics: Dict[str, Any] = {}

    async def analyze(self) -> List[BanditIssue]:
        """
        Run Bandit analysis on target path
        
        Args:
            None - uses initialized target_path
            
        Returns:
            List of detected security issues
        """
        self.issues = []
        
        # Build bandit command
        cmd = [
            'bandit',
            '-r',
            self.target_path,
            '-f', 'json',
            '--silent'
        ]
        
        try:
            result = await asyncio.create_task(self._run_bandit(cmd))
            if result:
                self._parse_bandit_output(result)
        except Exception as e:
            print(f"Bandit analysis error: {e}")
        
        return self.issues

    async def _run_bandit(self, cmd: List[str]) -> Optional[str]:
        """Run bandit command asynchronously"""
        loop = asyncio.get_event_loop()
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=30.0
            )
            return stdout.decode('utf-8')
        except asyncio.TimeoutError:
            print("Bandit analysis timeout")
            return None
        except FileNotFoundError:
            print("Bandit not installed. Install with: pip install bandit")
            return None

    def _parse_bandit_output(self, output: str):
        """Parse Bandit JSON output"""
        try:
            data = json.loads(output)
            
            # Extract metrics
            self.metrics = data.get('metrics', {})
            
            # Process results
            for result in data.get('results', []):
                try:
                    severity = BanditSeverity[result.get('severity', 'LOW')]
                except KeyError:
                    severity = BanditSeverity.LOW
                
                issue = BanditIssue(
                    issue_severity=severity,
                    issue_confidence=result.get('confidence', 'MEDIUM'),
                    issue_type=result.get('issue_type', 'Unknown'),
                    issue_text=result.get('issue_text', ''),
                    line_number=result.get('line_number', 0),
                    filename=result.get('filename', 'unknown'),
                    test_id=result.get('test_id', ''),
                    line_range=result.get('line_range', []),
                )
                self.issues.append(issue)
        except json.JSONDecodeError:
            print("Failed to parse Bandit output")

    def get_summary(self) -> Dict[str, Any]:
        """Get analysis summary"""
        by_severity = {severity.value: 0 for severity in BanditSeverity}
        by_type = {}
        
        for issue in self.issues:
            by_severity[issue.issue_severity.value] += 1
            by_type[issue.issue_type] = by_type.get(issue.issue_type, 0) + 1
        
        return {
            'total_issues': len(self.issues),
            'by_severity': by_severity,
            'by_type': by_type,
            'metrics': self.metrics,
            'issues': [issue.to_dict() for issue in self.issues],
        }


def get_bandit_analyzer(target_path: str = "backend") -> BanditAnalyzer:
    """Get or create Bandit analyzer instance"""
    if not hasattr(get_bandit_analyzer, '_instance'):
        get_bandit_analyzer._instance = BanditAnalyzer(target_path)
    return get_bandit_analyzer._instance
