# Project-Wide 'Both Ends' Audit Report
**Date:** 2026-01-25T13:48:03.181406
**Overall System Health Score:** 4.19 / 5.0

## UI/UX (Frontend)
- **Score**: 3.80 / 5.0
- **Metrics**:
  - hardcoded_colors: 26
  - hardcoded_spacing: 5
  - component_reuse: 48
  - accessibility_violations: 44
  - css_files: 6
  - responsive_layouts: 96
  - accessibility_files: ['D:\\Project\\PEOPLE_OS\\src\\modules\\gen-admin\\index.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\hcm\\index.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\org-audit\\index.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\payroll\\PayrollRunsManager.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\payroll\\PayslipViewer.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\payroll\\SalaryComponentsManager.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\payroll\\TaxDeductionsPortal.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\promotions\\ActionModal.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\promotions\\CreateCycleModal.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\promotions\\CreateRequestModal.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\rewards\\index.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\rewards\\RecognitionFeed.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\rewards\\UserWallet.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\self-service\\DocumentCenter.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\self-service\\index.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\self-service\\PayslipViewer.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\system-audit\\index.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\analytics\\components\\AnalyticsDashboard.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\analytics\\components\\MetricCard.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\analytics\\components\\RecruitmentFunnel.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\analytics\\components\\ReportBuilder.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\analytics\\components\\ReportDownloader.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\analytics\\components\\ReportViewer.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\analytics\\components\\TrendChart.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\gen-admin\\submodules\\AssetsSubmodule.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\gen-admin\\submodules\\ComplianceSubmodule.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\gen-admin\\submodules\\FacilitiesSubmodule.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\gen-admin\\submodules\\FleetSubmodule.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\gen-admin\\submodules\\TravelSubmodule.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\gen-admin\\submodules\\VisitorsSubmodule.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\hcm\\submodules\\employee\\EmployeeDashboard.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\hcm\\submodules\\employee\\modals\\ImportEmployeesModal.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\hcm\\submodules\\employee\\tabs\\DashboardTab.tsx', 'D:\\Project\\PEOPLE_OS\\src\\modules\\system-settings\\submodules\\LogViewer.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\analytics\\AnalyticsDashboard.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\analytics\\RecruitmentFunnel.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\analytics\\ReportBuilder.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\analytics\\ReportDownloader.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\analytics\\ScheduleManager.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\analytics\\TaskMonitor.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\analytics\\TrendChart.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\common\\DataExportButton.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\ui\\ConfirmationModal.tsx', 'D:\\Project\\PEOPLE_OS\\src\\components\\ui\\GlassCard.tsx']
- **Findings**:
  - 🟡 **Major**: 44 components lack accessibility attributes (Missing aria-labels, alt text, or other a11y features)

## Database (Schema)
- **Score**: 3.30 / 5.0
- **Metrics**:
  - foreign_keys_enforced: 0
  - indexes_count: 265
  - tables_without_indexes: 0
  - migration_files: 0
  - orphaned_records_risk: 0
- **Findings**:
  - 🟡 **Major**: Foreign keys not enforced (PRAGMA foreign_keys is not enabled in DB or Code)
  - 🔵 **Minor**: Potential Denormalization: 'core_organizations' (Table has 31 columns (threshold: 20))
  - 🔵 **Minor**: Potential Denormalization: 'hcm_employees' (Table has 54 columns (threshold: 20))
  - 🔵 **Minor**: Potential Denormalization: 'system_flags' (Table has 32 columns (threshold: 20))
  - 🔵 **Minor**: Potential Denormalization: 'payroll_settings' (Table has 22 columns (threshold: 20))
  - 🔵 **Minor**: Potential Denormalization: 'notification_settings' (Table has 33 columns (threshold: 20))
  - 🟡 **Major**: Unenforced Foreign Key: 'platform_events.entity_id' (Column 'entity_id' suggests a relation but has no FK constraint.)
  - 🟡 **Major**: Unenforced Foreign Key: 'platform_events.actor_id' (Column 'actor_id' suggests a relation but has no FK constraint.)
  - 🟡 **Major**: Unenforced Foreign Key: 'hcm_reward_point_transactions.reference_id' (Column 'reference_id' suggests a relation but has no FK constraint.)
  - 🔵 **Minor**: Potential Denormalization: 'hcm_payroll_runs' (Table has 21 columns (threshold: 20))
  - 🔵 **Minor**: Potential Denormalization: 'hcm_payroll_ledger' (Table has 33 columns (threshold: 20))
  - 🟡 **Major**: Unenforced Foreign Key: 'hcm_promotion_approvals.approver_id' (Column 'approver_id' suggests a relation but has no FK constraint.)

## API (Backend)
- **Score**: 4.70 / 5.0
- **Metrics**:
  - total_endpoints: 79
  - versioned_endpoints: 67
  - breaking_changes: 0
  - new_endpoints: 30
  - schema_size_kb: 198
- ✅ No findings.

## Architecture
- **Score**: 5.00 / 5.0
- **Metrics**:
  - cycle_count: 0
  - boundary_violations: 0
  - modules_scanned: 2838
  - dependency_edges: 16296
- ✅ No findings.

## Code Quality
- **Score**: 5.00 / 5.0
- **Metrics**:
  - typescript_errors: 0
  - eslint_errors: 0
  - python_errors: 0
  - type_coverage: 100.0
- ✅ No findings.

## Security
- **Score**: 2.50 / 5.0
- **Metrics**:
  - rbac_coverage: 200
  - exposed_secrets: 25
  - unprotected_endpoints: 0
  - rate_limited_endpoints: 0
- **Findings**:
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in dependencies.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in verify_org_super_admin_rule.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in add_org_super_admin.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in create_org_super_admin.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_block_root_creation.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_imaplib.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_nntplib.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_smtplib.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_ssl.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_urllib2.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_urllib2net.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in misc.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_security_scanning_phase2.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_security_scanning_phase2.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in force_fix_login.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in test_bcrypt_auth.py)
  - 🔴 **Critical**: Potential hardcoded secret detected (Found in verify_org_super_admin_rule.py)

## AI Layer
- **Score**: 5.00 / 5.0
- **Metrics**:
  - ai_integrations: 2
  - unpinned_models: 0
  - prompt_versioning: 2
  - input_validation: 0
  - ai_error_handling: 1
  - temperature_control: 1
  - grounding_instructions: 1
  - response_validation: 0
  - citation_extraction: 0
  - context_limits: 0
  - prompt_injection_protection: 9
  - pii_redaction: 5
  - rate_limiting: 23
  - fallback_behavior: 1160
- **Findings**:
  - 🟡 **Major**: Insufficient input validation on AI calls (Not all AI integrations validate input data (0/2))
  - 🔵 **Minor**: Incomplete AI error handling (Some AI calls lack proper error handling (1/2))
  - 🟡 **Major**: Unsafe AI Temperature Settings (Found 1 AI calls without explicit low-temperature settings (risk of hallucinations).)
  - 🟡 **Major**: Missing Grounding Instructions (Found 1 AI prompts without grounding constraints.)
  - 🟡 **Major**: Missing Response Validation (Found 2 AI calls without response validation.)
