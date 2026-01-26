"""
Security Scanner Module - OWASP Top 10 Detection

Detects and reports on OWASP Top 10 vulnerabilities:
1. Broken Access Control
2. Cryptographic Failures
3. Injection (SQL, NoSQL, Command)
4. Insecure Design
5. Security Misconfiguration
6. Vulnerable & Outdated Components
7. Authentication Failures
8. Software & Data Integrity Failures
9. Logging & Monitoring Failures
10. Server-Side Request Forgery (SSRF)
"""

import re
import ast
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
from enum import Enum
from datetime import datetime
import asyncio
import inspect


class VulnerabilityLevel(Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(Enum):
    """OWASP Top 10 vulnerability categories"""
    BROKEN_ACCESS_CONTROL = "broken_access_control"
    CRYPTOGRAPHIC_FAILURES = "cryptographic_failures"
    INJECTION = "injection"
    INSECURE_DESIGN = "insecure_design"
    SECURITY_MISCONFIGURATION = "security_misconfiguration"
    VULNERABLE_COMPONENTS = "vulnerable_components"
    AUTH_FAILURES = "auth_failures"
    INTEGRITY_FAILURES = "integrity_failures"
    LOGGING_FAILURES = "logging_failures"
    SSRF = "ssrf"


@dataclass
class Vulnerability:
    """Detected vulnerability record"""
    type: VulnerabilityType
    level: VulnerabilityLevel
    title: str
    description: str
    file: Optional[str] = None
    line: Optional[int] = None
    code_snippet: Optional[str] = None
    recommendation: Optional[str] = None
    cwe: Optional[str] = None  # Common Weakness Enumeration

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'type': self.type.value,
            'level': self.level.value,
            'title': self.title,
            'description': self.description,
            'file': self.file,
            'line': self.line,
            'code_snippet': self.code_snippet,
            'recommendation': self.recommendation,
            'cwe': self.cwe,
        }


class SecurityScanner:
    """Main security scanner for OWASP vulnerabilities"""

    def __init__(self):
        self.vulnerabilities: List[Vulnerability] = []
        self.scan_results: Dict[str, Any] = {}

    def reset(self):
        """Reset scanner state"""
        self.vulnerabilities = []
        self.scan_results = {}

    async def scan_python_code(self, code: str, filename: str = "unknown") -> List[Vulnerability]:
        """
        Scan Python code for security vulnerabilities
        
        Args:
            code: Python source code to scan
            filename: Filename for reference in reports
            
        Returns:
            List of detected vulnerabilities
        """
        vulns = []
        
        # Check for hardcoded secrets (Cryptographic Failures)
        vulns.extend(self._check_hardcoded_secrets(code, filename))
        
        # Check for SQL injection patterns (Injection)
        vulns.extend(self._check_sql_injection(code, filename))
        
        # Check for command injection (Injection)
        vulns.extend(self._check_command_injection(code, filename))
        
        # Check for insecure deserialization (Integrity Failures)
        vulns.extend(self._check_insecure_deserialization(code, filename))
        
        # Check for weak cryptography (Cryptographic Failures)
        vulns.extend(self._check_weak_cryptography(code, filename))
        
        # Check for hardcoded credentials (Auth Failures)
        vulns.extend(self._check_hardcoded_credentials(code, filename))
        
        # Check for XXE vulnerabilities (Injection)
        vulns.extend(self._check_xxe_vulnerabilities(code, filename))
        
        # Check for SSRF patterns (Server-Side Request Forgery)
        vulns.extend(self._check_ssrf_patterns(code, filename))
        
        # Check for missing authentication (Broken Access Control)
        vulns.extend(self._check_missing_auth(code, filename))
        
        # Check for insecure logging (Logging Failures)
        vulns.extend(self._check_insecure_logging(code, filename))
        
        self.vulnerabilities.extend(vulns)
        return vulns

    def _check_hardcoded_secrets(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for hardcoded secrets (API keys, passwords, tokens)"""
        vulns = []
        
        patterns = [
            (r'api[_-]?key\s*=\s*["\']([^"\']+)["\']', 'API Key'),
            (r'password\s*=\s*["\']([^"\']+)["\']', 'Password'),
            (r'secret\s*=\s*["\']([^"\']+)["\']', 'Secret'),
            (r'token\s*=\s*["\']([^"\']+)["\']', 'Token'),
            (r'aws[_-]?key\s*=\s*["\']([^"\']+)["\']', 'AWS Key'),
            (r'private[_-]?key\s*=\s*["\']([^"\']+)["\']', 'Private Key'),
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern, secret_type in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulns.append(Vulnerability(
                        type=VulnerabilityType.CRYPTOGRAPHIC_FAILURES,
                        level=VulnerabilityLevel.CRITICAL,
                        title=f"Hardcoded {secret_type}",
                        description=f"Hardcoded {secret_type.lower()} detected in source code",
                        file=filename,
                        line=line_num,
                        code_snippet=line.strip(),
                        recommendation=f"Use environment variables or secure vault for {secret_type.lower()}",
                        cwe="CWE-798"
                    ))
        
        return vulns

    def _check_sql_injection(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for SQL injection vulnerabilities"""
        vulns = []
        
        # SQL concatenation patterns
        sql_patterns = [
            r'(SELECT|INSERT|UPDATE|DELETE).*\+.*',
            r'(SELECT|INSERT|UPDATE|DELETE).*f["\']',
            r'\.execute\(.*\%',
            r'\.\w+\+\s*[a-zA-Z_]',
            r'["\'].*%s.*["\'].*%\s*\(',
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern in sql_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulns.append(Vulnerability(
                        type=VulnerabilityType.INJECTION,
                        level=VulnerabilityLevel.CRITICAL,
                        title="Potential SQL Injection",
                        description="SQL query appears to use string concatenation with user input",
                        file=filename,
                        line=line_num,
                        code_snippet=line.strip(),
                        recommendation="Use parameterized queries with proper escaping",
                        cwe="CWE-89"
                    ))
        
        return vulns

    def _check_command_injection(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for command injection vulnerabilities"""
        vulns = []
        
        dangerous_functions = ['os.system', 'os.popen', 'subprocess.call', 'subprocess.run', 'exec', 'eval']
        command_patterns = [
            r'os\.system\s*\(',
            r'os\.popen\s*\(',
            r'subprocess\.(call|run|Popen)\s*\(',
            r'exec\s*\(',
            r'eval\s*\(',
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern in command_patterns:
                if re.search(pattern, line):
                    # Check if using string concatenation
                    if '+' in line or 'f"' in line or "f'" in line:
                        vulns.append(Vulnerability(
                            type=VulnerabilityType.INJECTION,
                            level=VulnerabilityLevel.CRITICAL,
                            title="Potential Command Injection",
                            description="Dangerous function called with potential dynamic input",
                            file=filename,
                            line=line_num,
                            code_snippet=line.strip(),
                            recommendation="Use subprocess with shell=False and list arguments",
                            cwe="CWE-78"
                        ))
        
        return vulns

    def _check_insecure_deserialization(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for insecure deserialization patterns"""
        vulns = []
        
        patterns = [
            (r'pickle\.load', 'pickle'),
            (r'pickle\.loads', 'pickle'),
            (r'yaml\.load\s*\(', 'yaml'),
            (r'json\.load\(.*unsafe', 'json'),
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern, lib in patterns:
                if re.search(pattern, line):
                    vulns.append(Vulnerability(
                        type=VulnerabilityType.INTEGRITY_FAILURES,
                        level=VulnerabilityLevel.HIGH,
                        title=f"Insecure Deserialization ({lib})",
                        description=f"Untrusted data deserialization using {lib}",
                        file=filename,
                        line=line_num,
                        code_snippet=line.strip(),
                        recommendation=f"Use safe {lib} alternatives or validate input before deserialization",
                        cwe="CWE-502"
                    ))
        
        return vulns

    def _check_weak_cryptography(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for weak cryptographic algorithms"""
        vulns = []
        
        weak_algorithms = [
            (r'MD5', 'MD5', 'MD5'),
            (r'SHA1', 'SHA1', 'SHA1'),
            (r'DES', 'DES', 'DES'),
            (r'hashlib\.md5', 'MD5', 'MD5'),
            (r'hashlib\.sha1', 'SHA1', 'SHA1'),
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern, algo, name in weak_algorithms:
                if re.search(pattern, line, re.IGNORECASE):
                    vulns.append(Vulnerability(
                        type=VulnerabilityType.CRYPTOGRAPHIC_FAILURES,
                        level=VulnerabilityLevel.HIGH,
                        title=f"Weak Cryptographic Algorithm ({name})",
                        description=f"{name} is cryptographically weak",
                        file=filename,
                        line=line_num,
                        code_snippet=line.strip(),
                        recommendation=f"Use SHA-256 or stronger algorithms instead of {name}",
                        cwe="CWE-327"
                    ))
        
        return vulns

    def _check_hardcoded_credentials(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for hardcoded credentials"""
        vulns = []
        
        patterns = [
            (r'username\s*=\s*["\']', 'Username'),
            (r'user\s*=\s*["\']', 'User'),
            (r'passwd\s*=\s*["\']', 'Password'),
            (r'pwd\s*=\s*["\']', 'Password'),
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern, cred_type in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulns.append(Vulnerability(
                        type=VulnerabilityType.AUTH_FAILURES,
                        level=VulnerabilityLevel.HIGH,
                        title=f"Hardcoded {cred_type}",
                        description=f"Hardcoded {cred_type.lower()} found in source code",
                        file=filename,
                        line=line_num,
                        code_snippet=line.strip(),
                        recommendation="Use environment variables or secure credential management",
                        cwe="CWE-798"
                    ))
        
        return vulns

    def _check_xxe_vulnerabilities(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for XXE (XML External Entity) vulnerabilities"""
        vulns = []
        
        patterns = [
            r'xml\.etree.*ElementTree',
            r'xml\.dom.*minidom',
            r'lxml.*parse',
            r'\.parse\(',
            r'\.fromstring\(',
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern in patterns:
                if re.search(pattern, line):
                    vulns.append(Vulnerability(
                        type=VulnerabilityType.INJECTION,
                        level=VulnerabilityLevel.HIGH,
                        title="Potential XXE Vulnerability",
                        description="XML parsing without XXE protection",
                        file=filename,
                        line=line_num,
                        code_snippet=line.strip(),
                        recommendation="Disable DTD and external entity processing in XML parsers",
                        cwe="CWE-611"
                    ))
        
        return vulns

    def _check_ssrf_patterns(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for SSRF (Server-Side Request Forgery) patterns"""
        vulns = []
        
        patterns = [
            (r'requests\.(get|post|put|delete|patch|head)\s*\(', 'requests'),
            (r'urllib\.request\.urlopen', 'urllib'),
            (r'httpx\.(get|post|put|delete|patch|head)\s*\(', 'httpx'),
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern, lib in patterns:
                match = re.search(pattern, line)
                if match:
                    # Check if URL is dynamic or a variable (not a simple hardcoded string)
                    # This is a simplified check: if it contains quotes, it might be safe-ish,
                    # but if it uses a variable name or concatenation, it's risky.
                    has_concatenation = '+' in line or 'f"' in line or "f'" in line or 'format' in line
                    
                    # Look at what's inside the parentheses
                    call_content = line[match.end():]
                    if ')' in call_content:
                        args = call_content[:call_content.find(')')].strip()
                        # If args doesn't start and end with quotes, it's likely a variable
                        is_likely_variable = not ((args.startswith("'") and args.endswith("'")) or 
                                               (args.startswith('"') and args.endswith('"')))
                        
                        if has_concatenation or is_likely_variable:
                            vulns.append(Vulnerability(
                                type=VulnerabilityType.SSRF,
                                level=VulnerabilityLevel.MEDIUM,
                                title="Potential SSRF Vulnerability",
                                description=f"Unvalidated user input or variable passed to {lib}",
                                file=filename,
                                line=line_num,
                                code_snippet=line.strip(),
                                recommendation="Validate and whitelist URLs before making requests",
                                cwe="CWE-918"
                            ))
        
        return vulns

    def _check_missing_auth(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for missing authentication checks"""
        vulns = []
        
        # Check for endpoints without auth
        patterns = [
            r'@app\.get\s*\(',
            r'@app\.post\s*\(',
            r'@router\.get\s*\(',
            r'@router\.post\s*\(',
        ]
        
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            if any(re.search(p, line) for p in patterns):
                # Check if next line has Depends or security
                if line_num < len(lines):
                    next_line = lines[line_num] if line_num < len(lines) else ""
                    if 'Depends' not in next_line and 'Security' not in next_line:
                        vulns.append(Vulnerability(
                            type=VulnerabilityType.BROKEN_ACCESS_CONTROL,
                            level=VulnerabilityLevel.MEDIUM,
                            title="Missing Authentication Check",
                            description="API endpoint may be missing authentication/authorization",
                            file=filename,
                            line=line_num,
                            code_snippet=line.strip(),
                            recommendation="Add authentication/authorization checks to all endpoints",
                            cwe="CWE-306"
                        ))
        
        return vulns

    def _check_insecure_logging(self, code: str, filename: str) -> List[Vulnerability]:
        """Check for insecure logging practices"""
        vulns = []
        
        patterns = [
            (r'logger.*\.info\s*\(.*password', 'password'),
            (r'logger.*\.debug\s*\(.*token', 'token'),
            (r'print\s*\(.*password', 'password'),
            (r'print\s*\(.*secret', 'secret'),
        ]
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for pattern, secret in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    vulns.append(Vulnerability(
                        type=VulnerabilityType.LOGGING_FAILURES,
                        level=VulnerabilityLevel.HIGH,
                        title=f"Sensitive Data in Logs ({secret})",
                        description=f"Sensitive {secret} may be logged",
                        file=filename,
                        line=line_num,
                        code_snippet=line.strip(),
                        recommendation=f"Never log sensitive data like {secret}s",
                        cwe="CWE-532"
                    ))
        
        return vulns

    def get_summary(self) -> Dict[str, Any]:
        """Get vulnerability summary"""
        by_level = {}
        by_type = {}
        
        for vuln in self.vulnerabilities:
            # Count by level
            level = vuln.level.value
            by_level[level] = by_level.get(level, 0) + 1
            
            # Count by type
            vtype = vuln.type.value
            by_type[vtype] = by_type.get(vtype, 0) + 1
        
        return {
            'total_vulnerabilities': len(self.vulnerabilities),
            'by_level': by_level,
            'by_type': by_type,
            'vulnerabilities': [v.to_dict() for v in self.vulnerabilities],
        }


def get_security_scanner() -> SecurityScanner:
    """Get or create security scanner instance"""
    if not hasattr(get_security_scanner, '_instance'):
        get_security_scanner._instance = SecurityScanner()
    return get_security_scanner._instance
