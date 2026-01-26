import io
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from sqlalchemy.orm import Session
from backend.services.analytics_service import AnalyticsService

class ReportService:
    @staticmethod
    def generate_workforce_pdf(db: Session, organization_id: str) -> bytes:
        summary = AnalyticsService.get_dashboard_summary(db, organization_id)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "peopleOS eBusiness Suite - Workforce Analytics Report", 0, 1, "C")
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, "C")
        pdf.ln(10)
        
        # Summary Section
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "1. Executive Summary", 0, 1)
        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 8, f"- Total Active Employees: {summary['total_active_employees']}", 0, 1)
        pdf.cell(0, 8, f"- Total Candidates in Pipeline: {summary['total_candidates']}", 0, 1)
        pdf.cell(0, 8, f"- Workforce Velocity: {summary['workforce_velocity']}", 0, 1)
        pdf.cell(0, 8, f"- Retention Vector: {summary['retention_vector']}", 0, 1)
        pdf.ln(5)
        
        # Department Distribution
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "2. Departmental Distribution", 0, 1)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(90, 8, "Department", 1)
        pdf.cell(40, 8, "Count", 1)
        pdf.ln()
        pdf.set_font("Arial", "", 10)
        for dept in summary["department_distribution"]:
            pdf.cell(90, 8, dept["name"], 1)
            pdf.cell(40, 8, str(int(dept["value"])), 1)
            pdf.ln()
            
        return pdf.output(dest='S').encode('latin-1')

    @staticmethod
    def generate_workforce_excel(db: Session, organization_id: str) -> bytes:
        summary = AnalyticsService.get_dashboard_summary(db, organization_id)
        
        # Create multiple dataframes for a rich Excel report
        df_dept = pd.DataFrame(summary["department_distribution"])
        df_gender = pd.DataFrame(summary["gender_distribution"])
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_dept.to_excel(writer, sheet_name='Department Distribution', index=False)
            df_gender.to_excel(writer, sheet_name='Gender Distribution', index=False)
            
            # Add a summary sheet
            summary_data = {
                "Metric": ["Total Active Employees", "Total Candidates", "Workforce Velocity", "Retention Vector"],
                "Value": [
                    summary["total_active_employees"],
                    summary["total_candidates"],
                    summary["workforce_velocity"],
                    summary["retention_vector"]
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Executive Summary', index=False)
            
        return output.getvalue()
