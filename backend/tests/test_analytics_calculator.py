"""
Unit tests for Analytics Calculator and Enhanced Reports
Tests real metric calculations and report generation
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from backend.domains.hcm import models as hcm_models
from backend.domains.core import models as core_models
from backend.services.analytics_calculator import AnalyticsCalculator
from backend.services.analytics_service import AnalyticsService
from backend.services.enhanced_report_generator import EnhancedReportGenerator


@pytest.fixture(scope="function")
def test_db():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    core_models.Base.metadata.create_all(engine)
    hcm_models.Base.metadata.create_all(engine)
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db
    db.close()


@pytest.fixture
def test_org_id():
    return "test_org_001"


@pytest.fixture
def sample_data(test_db, test_org_id):
    """Create sample test data"""
    
    # Create organization
    org = core_models.DBOrganization(
        id=test_org_id,
        name="Test Organization",
        country="US"
    )
    test_db.add(org)
    test_db.commit()
    
    # Create departments
    dept_sales = core_models.DBDepartment(
        id="dept_001",
        organization_id=test_org_id,
        name="Sales",
        code="SALES"
    )
    dept_hr = core_models.DBDepartment(
        id="dept_002",
        organization_id=test_org_id,
        name="Human Resources",
        code="HR"
    )
    dept_eng = core_models.DBDepartment(
        id="dept_003",
        organization_id=test_org_id,
        name="Engineering",
        code="ENG"
    )
    test_db.add_all([dept_sales, dept_hr, dept_eng])
    test_db.commit()
    
    # Create grades
    grade1 = hcm_models.DBGrade(
        id="grade_001",
        organization_id=test_org_id,
        name="Junior",
        code="JR"
    )
    grade2 = hcm_models.DBGrade(
        id="grade_002",
        organization_id=test_org_id,
        name="Senior",
        code="SR"
    )
    test_db.add_all([grade1, grade2])
    test_db.commit()
    
    # Create designations
    desig_mgr = hcm_models.DBDesignation(
        id="desig_001",
        organization_id=test_org_id,
        name="Manager",
        code="MGR",
        grade_id="grade_002"
    )
    desig_sr_eng = hcm_models.DBDesignation(
        id="desig_002",
        organization_id=test_org_id,
        name="Senior Engineer",
        code="SENG",
        grade_id="grade_002"
    )
    test_db.add_all([desig_mgr, desig_sr_eng])
    test_db.commit()
    
    # Create employees
    employees = []
    for i in range(1, 26):  # 25 employees
        emp = hcm_models.DBEmployee(
            id=f"emp_{i:03d}",
            organization_id=test_org_id,
            code=f"E{i:04d}",
            name=f"Employee {i}",
            email=f"emp{i}@test.com",
            phone=f"+1234567890{i%10}",
            gender="Male" if i % 2 == 0 else "Female",
            date_of_birth=datetime(1990 + i%30, 1, 1),
            date_of_joining=datetime.now() - timedelta(days=365 - i*10),
            designation_id="desig_001" if i % 3 == 0 else "desig_002",
            department_id="dept_001" if i % 3 == 0 else ("dept_002" if i % 3 == 1 else "dept_003"),
            status="Active",
            gross_salary=50000 + i*1000,
        )
        employees.append(emp)
    
    test_db.add_all(employees)
    test_db.commit()
    
    # Create candidates
    candidates = []
    stages = ["Applied", "Shortlisted", "Interview", "Offer", "Joined"]
    for i in range(1, 16):  # 15 candidates
        cand = hcm_models.DBCandidate(
            id=f"cand_{i:03d}",
            organization_id=test_org_id,
            name=f"Candidate {i}",
            email=f"cand{i}@test.com",
            phone=f"+9876543210{i%10}",
            applied_date=datetime.now() - timedelta(days=30*i),
            current_stage=stages[i % len(stages)],
        )
        candidates.append(cand)
    
    test_db.add_all(candidates)
    test_db.commit()
    
    return test_db


class TestAnalyticsCalculator:
    """Test analytics calculations"""
    
    def test_calculate_total_employees(self, sample_data, test_org_id):
        """Test total employee count"""
        count = AnalyticsCalculator.calculate_total_employees(sample_data, test_org_id, "Active")
        assert count == 25
    
    def test_calculate_employees_by_department(self, sample_data, test_org_id):
        """Test department distribution"""
        dist = AnalyticsCalculator.calculate_employees_by_department(sample_data, test_org_id)
        assert len(dist) > 0
        total = sum(d['value'] for d in dist)
        assert total == 25
    
    def test_calculate_employees_by_gender(self, sample_data, test_org_id):
        """Test gender distribution"""
        dist = AnalyticsCalculator.calculate_employees_by_gender(sample_data, test_org_id)
        assert len(dist) > 0
        total = sum(d['value'] for d in dist)
        assert total == 25
    
    def test_calculate_headcount_trends(self, sample_data, test_org_id):
        """Test headcount trends calculation"""
        trends = AnalyticsCalculator.calculate_headcount_trends(sample_data, test_org_id, 6)
        assert len(trends) == 6
        assert all('name' in t and 'count' in t and 'liability' in t for t in trends)
        # Headcount should be non-decreasing (since employees only join, not leave)
        for i in range(1, len(trends)):
            assert trends[i]['count'] >= trends[i-1]['count']
    
    def test_calculate_new_hires(self, sample_data, test_org_id):
        """Test new hires calculation"""
        new_hires = AnalyticsCalculator.calculate_new_hires(sample_data, test_org_id, 30)
        assert isinstance(new_hires, int)
        assert new_hires >= 0
    
    def test_calculate_turnover_rate(self, sample_data, test_org_id):
        """Test turnover rate calculation"""
        turnover = AnalyticsCalculator.calculate_turnover_rate(sample_data, test_org_id, 12)
        assert 'left_count' in turnover
        assert 'turnover_rate' in turnover
        assert turnover['turnover_rate'] >= 0
    
    def test_calculate_retention_rate(self, sample_data, test_org_id):
        """Test retention rate calculation"""
        retention = AnalyticsCalculator.calculate_retention_rate(sample_data, test_org_id)
        assert 0 <= retention <= 100
        # All employees are active, so retention should be 100%
        assert retention == 100.0
    
    def test_calculate_recruitment_funnel(self, sample_data, test_org_id):
        """Test recruitment funnel"""
        funnel = AnalyticsCalculator.calculate_recruitment_funnel(sample_data, test_org_id)
        assert len(funnel) > 0
        total_candidates = sum(f['value'] for f in funnel)
        assert total_candidates == 15
    
    def test_calculate_dashboard_metrics(self, sample_data, test_org_id):
        """Test complete dashboard metrics"""
        metrics = AnalyticsCalculator.calculate_dashboard_metrics(sample_data, test_org_id)
        
        # Verify all expected keys exist
        expected_keys = [
            'workforce_velocity', 'retention_vector', 'turnover_rate',
            'total_active_employees', 'total_employees',
            'department_distribution', 'gender_distribution',
            'headcount_trends', 'recruitment_funnel'
        ]
        
        for key in expected_keys:
            assert key in metrics, f"Missing key: {key}"
        
        # Verify data types
        assert isinstance(metrics['total_active_employees'], int)
        assert isinstance(metrics['department_distribution'], list)
        assert isinstance(metrics['headcount_trends'], list)


class TestAnalyticsService:
    """Test analytics service endpoints"""
    
    def test_get_dashboard_summary(self, sample_data, test_org_id):
        """Test dashboard summary endpoint"""
        summary = AnalyticsService.get_dashboard_summary(sample_data, test_org_id)
        
        assert 'workforce_velocity' in summary
        assert 'retention_vector' in summary
        assert 'total_active_employees' in summary
        assert summary['total_active_employees'] == 25
    
    def test_get_headcount_trends(self, sample_data, test_org_id):
        """Test headcount trends endpoint"""
        trends = AnalyticsService.get_headcount_trends(sample_data, test_org_id)
        
        assert isinstance(trends, list)
        assert len(trends) == 6
        assert all('name' in t and 'count' in t for t in trends)
    
    def test_get_recruitment_funnel(self, sample_data, test_org_id):
        """Test recruitment funnel endpoint"""
        funnel = AnalyticsService.get_recruitment_funnel(sample_data, test_org_id)
        
        assert isinstance(funnel, list)
        total = sum(f['value'] for f in funnel)
        assert total == 15
    
    def test_get_engagement_data(self, sample_data, test_org_id):
        """Test engagement data endpoint"""
        engagement = AnalyticsService.get_engagement_data(sample_data, test_org_id)
        
        assert isinstance(engagement, list)
        assert len(engagement) == 5  # 5 weekdays
        assert all('name' in e and 'engagement' in e for e in engagement)


class TestEnhancedReportGenerator:
    """Test report generation"""
    
    def test_generate_workforce_report_pdf(self, sample_data, test_org_id):
        """Test PDF report generation"""
        pdf_buffer = EnhancedReportGenerator.generate_workforce_report_pdf(sample_data, test_org_id)
        
        assert pdf_buffer is not None
        content = pdf_buffer.getvalue()
        assert len(content) > 0
        assert b'%PDF' in content  # PDF signature
    
    def test_generate_workforce_report_excel(self, sample_data, test_org_id):
        """Test Excel report generation"""
        excel_buffer = EnhancedReportGenerator.generate_workforce_report_excel(sample_data, test_org_id)
        
        assert excel_buffer is not None
        content = excel_buffer.getvalue()
        assert len(content) > 0
        # Excel files start with PK (ZIP archive)
        assert b'PK' in content[:2]
    
    def test_generate_recruitment_report_pdf(self, sample_data, test_org_id):
        """Test recruitment report PDF"""
        pdf_buffer = EnhancedReportGenerator.generate_recruitment_report_pdf(sample_data, test_org_id)
        
        assert pdf_buffer is not None
        content = pdf_buffer.getvalue()
        assert len(content) > 0
        assert b'%PDF' in content
    
    def test_generate_payroll_report_pdf(self, sample_data, test_org_id):
        """Test payroll report PDF"""
        pdf_buffer = EnhancedReportGenerator.generate_payroll_report_pdf(sample_data, test_org_id)
        
        assert pdf_buffer is not None
        content = pdf_buffer.getvalue()
        assert len(content) > 0
        assert b'%PDF' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
