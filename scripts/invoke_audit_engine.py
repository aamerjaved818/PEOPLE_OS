
import sys
import os
from pathlib import Path

# Setup paths
project_root = str(Path(__file__).resolve().parent.parent)
sys.path.insert(0, project_root)

from backend.audit.audit_engine import AuditEngine
from backend.audit.report_generator import ReportGenerator

def main():
    print("🚀 Initializing System Audit Engine...")
    engine = AuditEngine()
    
    print("📋 Running Audit (Scope: Full System)...")
    # Execute Audit
    report = engine.run_audit(executed_by="SystemAdmin", scope="Full System via Audit Engine")
    
    # Generate Report
    print("📝 Generating Report...")
    output_dir = Path(project_root) / "docs" / "archive"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    report_path = ReportGenerator.save_report(report, output_dir)
    
    # Rename for clarity if needed, but save_report uses a specific format.
    # We will print the path.
    print(f"✅ Audit Complete!")
    print(f"📄 Report saved to: {report_path}")
    print(f"📊 Overall Score: {report.overall_score}/5.0")
    print(f"⚠️ Risk Level: {report.risk_level}")

if __name__ == "__main__":
    main()
