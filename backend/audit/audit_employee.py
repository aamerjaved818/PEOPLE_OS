import sys
from pathlib import Path
import json

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.audit.audit_engine import run_system_audit
from backend.audit.models import AuditFinding

def audit_employee_module():
    print("[AUDIT] Starting Employee Module Audit...")
    
    # Run full system audit (reusing existing engine)
    report = run_system_audit(executed_by="Employee-Auditor", save_to_db=False)
    
    # Define scope for Employee Module
    target_paths = [
        "src/modules/employee",
        "backend/domains/hcm",
        "backend/models/employees.py" # Assuming this exists or similar
    ]
    
    target_keywords = ["employee", "hcm", "grade", "job_level", "designation"]
    
    print(f"\n[FILTER] Filtering findings for: {target_paths}")
    
    relevant_findings = []
    
    for finding in report.critical_findings + report.major_findings + report.minor_findings:
        is_relevant = False
        
        # Check if finding relates to target paths (if path info is available in description/title)
        # Most findings might be generic, so we look for keywords in title/description
        text_content = (finding.title + " " + finding.description).lower()
        
        if any(keyword in text_content for keyword in target_keywords):
            is_relevant = True
            
        if is_relevant:
            relevant_findings.append(finding)
            
    print("\n" + "=" * 50)
    print(f"📊 Employee Module Audit Report")
    print("=" * 50)
    
    if not relevant_findings:
        print("No specific issues found for Employee Module.")
    else:
        print(f"Found {len(relevant_findings)} issues:\n")
        for f in relevant_findings:
            print(f"[{f.severity.upper()}] {f.title}")
            print(f"  - {f.description}")
            print(f"  - Recommendation: {f.recommendation}")
            print("-" * 30)

if __name__ == "__main__":
    audit_employee_module()
