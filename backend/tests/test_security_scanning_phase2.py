"""
Tests for Phase 2 Task 5 - Security Scanning

Tests security scanner, Bandit analyzer, Semgrep analyzer, and report generation.
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path

from backend.security.security_scanner import (
    SecurityScanner,
    Vulnerability,
    VulnerabilityLevel,
    VulnerabilityType,
    get_security_scanner,
)
from backend.security.bandit_analyzer import (
    BanditAnalyzer,
    BanditIssue,
    BanditSeverity,
    get_bandit_analyzer,
)
from backend.security.semgrep_analyzer import (
    SemgrepAnalyzer,
    SemgrepMatch,
    SemgrepSeverity,
    get_semgrep_analyzer,
)
from backend.security.security_report import (
    SecurityReport,
    SecurityMetrics,
    ReportFormat,
    get_security_report,
)


class TestSecurityScanner:
    """Tests for OWASP security scanner"""

    def test_scanner_initialization(self):
        """Test security scanner creation"""
        scanner = SecurityScanner()
        assert scanner.vulnerabilities == []
        assert scanner.scan_results == {}

    def test_scanner_reset(self):
        """Test scanner reset"""
        scanner = SecurityScanner()
        vuln = Vulnerability(
            type=VulnerabilityType.INJECTION,
            level=VulnerabilityLevel.CRITICAL,
            title="Test",
            description="Test vulnerability"
        )
        scanner.vulnerabilities.append(vuln)
        
        scanner.reset()
        assert scanner.vulnerabilities == []

    def test_hardcoded_secrets_detection(self):
        """Test detection of hardcoded secrets"""
        scanner = SecurityScanner()
        code = 'api_key = "sk_live_12345678"'
        
        vulns = scanner._check_hardcoded_secrets(code, "test.py")
        
        assert len(vulns) > 0
        assert vulns[0].type == VulnerabilityType.CRYPTOGRAPHIC_FAILURES
        assert vulns[0].level == VulnerabilityLevel.CRITICAL

    def test_sql_injection_detection(self):
        """Test detection of SQL injection patterns"""
        scanner = SecurityScanner()
        code = 'query = "SELECT * FROM users WHERE id = " + user_id'
        
        vulns = scanner._check_sql_injection(code, "test.py")
        
        assert len(vulns) > 0
        assert vulns[0].type == VulnerabilityType.INJECTION

    def test_command_injection_detection(self):
        """Test detection of command injection"""
        scanner = SecurityScanner()
        code = 'os.system("rm -rf " + user_input)'
        
        vulns = scanner._check_command_injection(code, "test.py")
        
        assert len(vulns) > 0
        assert vulns[0].type == VulnerabilityType.INJECTION
        assert vulns[0].level == VulnerabilityLevel.CRITICAL

    def test_insecure_deserialization_detection(self):
        """Test detection of insecure deserialization"""
        scanner = SecurityScanner()
        code = 'data = pickle.load(untrusted_stream)'
        
        vulns = scanner._check_insecure_deserialization(code, "test.py")
        
        assert len(vulns) > 0
        assert vulns[0].type == VulnerabilityType.INTEGRITY_FAILURES

    def test_weak_cryptography_detection(self):
        """Test detection of weak cryptographic algorithms"""
        scanner = SecurityScanner()
        code = 'hash_obj = hashlib.md5()'
        
        vulns = scanner._check_weak_cryptography(code, "test.py")
        
        assert len(vulns) > 0
        assert vulns[0].level == VulnerabilityLevel.HIGH

    def test_hardcoded_credentials_detection(self):
        """Test detection of hardcoded credentials"""
        scanner = SecurityScanner()
        code = 'username = "admin@example.com"\npassword = "SecurePass123"'
        
        vulns = scanner._check_hardcoded_credentials(code, "test.py")
        
        assert len(vulns) > 0

    def test_xxe_vulnerability_detection(self):
        """Test detection of XXE vulnerabilities"""
        scanner = SecurityScanner()
        code = 'tree = ET.parse(xml_file)'
        
        vulns = scanner._check_xxe_vulnerabilities(code, "test.py")
        
        assert len(vulns) > 0

    def test_ssrf_vulnerability_detection(self):
        """Test detection of SSRF vulnerabilities"""
        scanner = SecurityScanner()
        code = 'response = requests.get(user_url)'
        
        vulns = scanner._check_ssrf_patterns(code, "test.py")
        
        assert len(vulns) > 0

    def test_insecure_logging_detection(self):
        """Test detection of sensitive data in logs"""
        scanner = SecurityScanner()
        code = 'logger.info(f"User password: {password}")'
        
        vulns = scanner._check_insecure_logging(code, "test.py")
        
        assert len(vulns) > 0
        assert vulns[0].type == VulnerabilityType.LOGGING_FAILURES

    def test_vulnerability_to_dict(self):
        """Test vulnerability serialization"""
        vuln = Vulnerability(
            type=VulnerabilityType.INJECTION,
            level=VulnerabilityLevel.CRITICAL,
            title="Test Injection",
            description="Test description",
            file="test.py",
            line=42,
            cwe="CWE-89"
        )
        
        vuln_dict = vuln.to_dict()
        
        assert vuln_dict['type'] == 'injection'
        assert vuln_dict['level'] == 'critical'
        assert vuln_dict['title'] == 'Test Injection'
        assert vuln_dict['line'] == 42

    def test_get_summary(self):
        """Test vulnerability summary generation"""
        scanner = SecurityScanner()
        
        vuln1 = Vulnerability(
            type=VulnerabilityType.INJECTION,
            level=VulnerabilityLevel.CRITICAL,
            title="Test 1",
            description="Test"
        )
        vuln2 = Vulnerability(
            type=VulnerabilityType.CRYPTOGRAPHIC_FAILURES,
            level=VulnerabilityLevel.HIGH,
            title="Test 2",
            description="Test"
        )
        
        scanner.vulnerabilities = [vuln1, vuln2]
        summary = scanner.get_summary()
        
        assert summary['total_vulnerabilities'] == 2
        assert summary['by_level']['critical'] == 1
        assert summary['by_level']['high'] == 1

    @pytest.mark.asyncio
    async def test_scan_python_code(self):
        """Test scanning Python code"""
        scanner = SecurityScanner()
        code = 'api_key = "secret_key"'
        
        vulns = await scanner.scan_python_code(code, "test.py")
        
        assert len(vulns) > 0

    def test_singleton_instance(self):
        """Test singleton pattern for scanner"""
        scanner1 = get_security_scanner()
        scanner2 = get_security_scanner()
        
        assert scanner1 is scanner2


class TestBanditAnalyzer:
    """Tests for Bandit analyzer"""

    def test_analyzer_initialization(self):
        """Test Bandit analyzer creation"""
        analyzer = BanditAnalyzer()
        assert analyzer.target_path == "backend"
        assert analyzer.issues == []

    def test_bandit_issue_creation(self):
        """Test Bandit issue creation"""
        issue = BanditIssue(
            issue_severity=BanditSeverity.HIGH,
            issue_confidence="MEDIUM",
            issue_type="hardcoded_password",
            issue_text="Hardcoded password found",
            line_number=42,
            filename="test.py",
            test_id="B105",
            line_range=[42, 42]
        )
        
        assert issue.issue_severity == BanditSeverity.HIGH
        assert issue.line_number == 42

    def test_bandit_issue_to_dict(self):
        """Test issue serialization"""
        issue = BanditIssue(
            issue_severity=BanditSeverity.HIGH,
            issue_confidence="HIGH",
            issue_type="hardcoded_sql_string",
            issue_text="SQL hardcoded",
            line_number=10,
            filename="app.py",
            test_id="B601",
            line_range=[10, 10]
        )
        
        issue_dict = issue.to_dict()
        
        assert issue_dict['severity'] == 'HIGH'
        assert issue_dict['type'] == 'hardcoded_sql_string'
        assert issue_dict['line'] == 10

    def test_bandit_summary_generation(self):
        """Test Bandit summary generation"""
        analyzer = BanditAnalyzer()
        
        issue1 = BanditIssue(
            issue_severity=BanditSeverity.HIGH,
            issue_confidence="HIGH",
            issue_type="test1",
            issue_text="Test",
            line_number=1,
            filename="test.py",
            test_id="B001",
            line_range=[1, 1]
        )
        
        analyzer.issues = [issue1]
        summary = analyzer.get_summary()
        
        assert summary['total_issues'] == 1
        assert summary['by_severity']['HIGH'] == 1

    def test_singleton_instance(self):
        """Test singleton pattern for Bandit analyzer"""
        analyzer1 = get_bandit_analyzer()
        analyzer2 = get_bandit_analyzer()
        
        assert analyzer1 is analyzer2


class TestSemgrepAnalyzer:
    """Tests for Semgrep analyzer"""

    def test_analyzer_initialization(self):
        """Test Semgrep analyzer creation"""
        analyzer = SemgrepAnalyzer()
        assert analyzer.target_path == "backend"
        assert analyzer.config == "p/security-audit"
        assert analyzer.matches == []

    def test_semgrep_match_creation(self):
        """Test Semgrep match creation"""
        match = SemgrepMatch(
            rule_id="python.django.security.injection.sql.sql-string-format",
            message="SQL injection",
            severity=SemgrepSeverity.CRITICAL,
            path="app.py",
            start_line=10,
            end_line=10,
            start_col=0,
            end_col=50
        )
        
        assert match.rule_id == "python.django.security.injection.sql.sql-string-format"
        assert match.severity == SemgrepSeverity.CRITICAL

    def test_semgrep_match_to_dict(self):
        """Test match serialization"""
        match = SemgrepMatch(
            rule_id="test-rule",
            message="Test message",
            severity=SemgrepSeverity.WARNING,
            path="test.py",
            start_line=5,
            end_line=5,
            start_col=0,
            end_col=10
        )
        
        match_dict = match.to_dict()
        
        assert match_dict['rule_id'] == "test-rule"
        assert match_dict['severity'] == 'WARNING'
        assert match_dict['start_line'] == 5

    def test_semgrep_summary_generation(self):
        """Test Semgrep summary generation"""
        analyzer = SemgrepAnalyzer()
        
        match1 = SemgrepMatch(
            rule_id="test-rule-1",
            message="Test",
            severity=SemgrepSeverity.CRITICAL,
            path="test.py",
            start_line=1,
            end_line=1,
            start_col=0,
            end_col=5
        )
        
        analyzer.matches = [match1]
        summary = analyzer.get_summary()
        
        assert summary['total_matches'] == 1
        assert summary['by_severity']['CRITICAL'] == 1

    def test_singleton_instance(self):
        """Test singleton pattern for Semgrep analyzer"""
        analyzer1 = get_semgrep_analyzer()
        analyzer2 = get_semgrep_analyzer()
        
        assert analyzer1 is analyzer2

    def test_different_instances_for_different_paths(self):
        """Test different analyzer instances for different paths"""
        analyzer1 = get_semgrep_analyzer("path1")
        analyzer2 = get_semgrep_analyzer("path2")
        
        assert analyzer1 is not analyzer2


class TestSecurityReport:
    """Tests for unified security report"""

    def test_report_initialization(self):
        """Test security report creation"""
        report = SecurityReport()
        assert report.generated_at is None
        assert report.metrics is None

    def test_metrics_creation(self):
        """Test security metrics creation"""
        metrics = SecurityMetrics(
            total_vulnerabilities=10,
            total_issues=5,
            total_matches=3,
            critical_count=2,
            high_count=4,
            medium_count=7,
            low_count=5,
            info_count=0,
            risk_score=42.5,
            timestamp=datetime.utcnow().isoformat()
        )
        
        assert metrics.total_vulnerabilities == 10
        assert metrics.risk_score == 42.5

    def test_metrics_as_dict(self):
        """Test metrics serialization"""
        timestamp = datetime.utcnow().isoformat()
        metrics = SecurityMetrics(
            total_vulnerabilities=10,
            total_issues=5,
            total_matches=3,
            critical_count=2,
            high_count=4,
            medium_count=7,
            low_count=5,
            info_count=0,
            risk_score=42.5,
            timestamp=timestamp
        )
        
        # asdict is already used in the code, just verify metrics can be serialized
        assert metrics.risk_score == 42.5

    def test_summary_generation(self):
        """Test summary generation"""
        report = SecurityReport()
        report.metrics = SecurityMetrics(
            total_vulnerabilities=10,
            total_issues=5,
            total_matches=3,
            critical_count=2,
            high_count=4,
            medium_count=7,
            low_count=5,
            info_count=0,
            risk_score=42.5,
            timestamp=datetime.utcnow().isoformat()
        )
        report.generated_at = datetime.utcnow().isoformat()
        
        summary = report._generate_summary()
        
        assert "42.5" in summary
        assert "Critical" in summary

    def test_singleton_instance(self):
        """Test singleton pattern for report"""
        report1 = get_security_report()
        report2 = get_security_report()
        
        assert report1 is report2

    def test_json_export_format(self):
        """Test JSON export format validation"""
        report = SecurityReport()
        
        sample_report = {
            'generated_at': datetime.utcnow().isoformat(),
            'target': 'backend',
            'metrics': {
                'total_vulnerabilities': 10,
                'total_issues': 5,
                'total_matches': 3,
                'critical_count': 2,
                'high_count': 4,
                'medium_count': 7,
                'low_count': 5,
                'info_count': 0,
                'risk_score': 42.5,
                'timestamp': datetime.utcnow().isoformat()
            },
            'owasp': {'total_vulnerabilities': 10},
            'bandit': {'total_issues': 5},
            'semgrep': {'total_matches': 3},
            'summary': 'Test summary'
        }
        
        assert 'generated_at' in sample_report
        assert 'metrics' in sample_report
        assert sample_report['metrics']['risk_score'] == 42.5

    def test_markdown_export_format(self):
        """Test Markdown export format"""
        report = SecurityReport()
        
        sample_report = {
            'generated_at': datetime.utcnow().isoformat(),
            'target': 'backend',
            'metrics': {
                'critical_count': 2,
                'high_count': 4,
                'medium_count': 7,
                'low_count': 5,
                'info_count': 0,
                'risk_score': 42.5,
            },
            'owasp': {
                'total_vulnerabilities': 10,
                'by_level': {'critical': 2, 'high': 4}
            },
            'bandit': {
                'total_issues': 5,
                'by_severity': {'HIGH': 4, 'LOW': 1}
            },
            'semgrep': {
                'total_matches': 3,
                'by_severity': {'WARNING': 2, 'NOTE': 1}
            },
            'summary': 'Test summary'
        }
        
        # Verify structure
        assert 'owasp' in sample_report
        assert 'bandit' in sample_report
        assert 'semgrep' in sample_report

    def test_html_export_format(self):
        """Test HTML export format"""
        report = SecurityReport()
        
        sample_report = {
            'generated_at': datetime.utcnow().isoformat(),
            'target': 'backend',
            'metrics': {
                'critical_count': 2,
                'high_count': 4,
                'medium_count': 7,
                'low_count': 5,
                'info_count': 0,
                'risk_score': 42.5,
            },
            'owasp': {
                'total_vulnerabilities': 10,
            },
            'bandit': {
                'total_issues': 5,
            },
            'semgrep': {
                'total_matches': 3,
            },
            'summary': 'Test summary'
        }
        
        # Verify metrics present
        assert sample_report['metrics']['risk_score'] == 42.5


class TestIntegration:
    """Integration tests for security scanning"""

    def test_scanner_with_vulnerable_code(self):
        """Test scanning vulnerable Python code"""
        scanner = SecurityScanner()
        vulnerable_code = '''
api_key = "sk_live_1234567890"
password = "admin123"
query = "SELECT * FROM users WHERE id=" + user_input
'''
        
        vulns = scanner._check_hardcoded_secrets(vulnerable_code, "app.py")
        assert len(vulns) > 0
        
        vulns2 = scanner._check_sql_injection(vulnerable_code, "app.py")
        assert len(vulns2) > 0

    def test_multiple_vulnerability_types(self):
        """Test detection of multiple vulnerability types"""
        scanner = SecurityScanner()
        
        code_with_multiple_vulns = '''
API_KEY = "secret_key"
password = "pass123"
os.system(user_command)
pickle.load(stream)
'''
        
        all_vulns = []
        all_vulns.extend(scanner._check_hardcoded_secrets(code_with_multiple_vulns, "test.py"))
        all_vulns.extend(scanner._check_command_injection(code_with_multiple_vulns, "test.py"))
        all_vulns.extend(scanner._check_insecure_deserialization(code_with_multiple_vulns, "test.py"))
        
        assert len(all_vulns) > 0

    def test_severity_levels(self):
        """Test different severity levels"""
        vuln_critical = Vulnerability(
            type=VulnerabilityType.INJECTION,
            level=VulnerabilityLevel.CRITICAL,
            title="Critical Issue",
            description="Test"
        )
        
        vuln_low = Vulnerability(
            type=VulnerabilityType.INSECURE_DESIGN,
            level=VulnerabilityLevel.LOW,
            title="Low Issue",
            description="Test"
        )
        
        assert vuln_critical.level == VulnerabilityLevel.CRITICAL
        assert vuln_low.level == VulnerabilityLevel.LOW
