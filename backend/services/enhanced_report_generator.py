"""
Enhanced Report Generator - Generates professional reports in multiple formats
Replaces basic FPDF with ReportLab for better formatting and charts
"""

from datetime import datetime
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from sqlalchemy.orm import Session
from backend.services.analytics_calculator import AnalyticsCalculator
from typing import Dict, Any, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class EnhancedReportGenerator:
    """Generates professional reports using ReportLab and Excel"""
    
    COLORS = {
        'header': colors.HexColor('#1e40af'),
        'accent': colors.HexColor('#f59e0b'),
        'success': colors.HexColor('#10b981'),
        'danger': colors.HexColor('#ef4444'),
        'border': colors.HexColor('#e5e7eb'),
        'light_bg': colors.HexColor('#f3f4f6'),
    }

    @staticmethod
    def _get_styles():
        """Get custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Title style
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=EnhancedReportGenerator.COLORS['header'],
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=EnhancedReportGenerator.COLORS['header'],
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Metric label style
        styles.add(ParagraphStyle(
            name='MetricLabel',
            fontSize=11,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=4
        ))
        
        # Metric value style
        styles.add(ParagraphStyle(
            name='MetricValue',
            fontSize=18,
            textColor=EnhancedReportGenerator.COLORS['header'],
            fontName='Helvetica-Bold',
            spaceAfter=12
        ))
        
        return styles

    @staticmethod
    def generate_workforce_report_pdf(
        db: Session, organization_id: str, include_charts: bool = True
    ) -> BytesIO:
        """Generate comprehensive workforce report in PDF format"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = EnhancedReportGenerator._get_styles()
        
        # Get metrics
        metrics = AnalyticsCalculator.calculate_dashboard_metrics(db, organization_id)
        
        # Title and Date
        story.append(Paragraph("WORKFORCE ANALYTICS REPORT", styles['CustomTitle']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary - Key Metrics
        story.append(Paragraph("EXECUTIVE SUMMARY", styles['SectionHeader']))
        
        # Create metrics table
        metrics_data = [
            ["Metric", "Current Value", "Status"],
            ["Total Active Employees", str(metrics['total_active_employees']), "✓"],
            ["Retention Rate", metrics['retention_vector'], "✓"],
            ["Turnover Rate", metrics['turnover_rate'], "⚠"],
            ["Open Positions", str(metrics['open_positions']), "✓"],
            ["Monthly Payroll", f"${metrics['total_monthly_payroll']:,.0f}", "✓"],
            ["Cost per Employee", metrics['cost_per_employee'], "✓"],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2.5*inch, 2*inch, 1*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EnhancedReportGenerator.COLORS['header']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Department Distribution
        story.append(Paragraph("DEPARTMENT DISTRIBUTION", styles['SectionHeader']))
        
        dept_data = [["Department", "Employees", "% of Total"]]
        total_employees = sum(d['value'] for d in metrics['department_distribution'])
        
        for dept in metrics['department_distribution']:
            pct = (dept['value'] / total_employees * 100) if total_employees > 0 else 0
            dept_data.append([
                dept['name'],
                str(dept['value']),
                f"{pct:.1f}%"
            ])
        
        dept_table = Table(dept_data, colWidths=[3.5*inch, 1.5*inch, 1.5*inch])
        dept_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EnhancedReportGenerator.COLORS['header']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        story.append(dept_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Headcount Trends
        story.append(Paragraph("HEADCOUNT TRENDS (6 MONTHS)", styles['SectionHeader']))
        
        trend_data = [["Month", "Headcount", "Gratuity Liability"]]
        for trend in metrics['headcount_trends']:
            trend_data.append([
                trend['name'],
                str(trend['count']),
                f"${trend['liability']*1000:,.0f}"
            ])
        
        trend_table = Table(trend_data, colWidths=[2*inch, 2*inch, 2.5*inch])
        trend_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EnhancedReportGenerator.COLORS['header']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        story.append(trend_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recruitment Funnel
        story.append(Paragraph("RECRUITMENT FUNNEL", styles['SectionHeader']))
        
        funnel_data = [["Stage", "Candidates"]]
        for stage in metrics['recruitment_funnel']:
            funnel_data.append([stage['name'], str(stage['value'])])
        
        funnel_table = Table(funnel_data, colWidths=[3.5*inch, 2*inch])
        funnel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EnhancedReportGenerator.COLORS['header']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        story.append(funnel_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"<i>This report contains confidential workforce analytics. "
            f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>",
            styles['Normal']
        ))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_workforce_report_excel(
        db: Session, organization_id: str
    ) -> BytesIO:
        """Generate workforce report in Excel format with multiple sheets"""
        
        metrics = AnalyticsCalculator.calculate_dashboard_metrics(db, organization_id)
        
        # Create Excel writer
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Executive Summary
            summary_data = {
                'Metric': [
                    'Total Active Employees',
                    'Total Candidates',
                    'Open Positions',
                    'Retention Rate',
                    'Turnover Rate',
                    'New Hires (30d)',
                    'Monthly Payroll',
                    'Cost per Employee',
                    'Workforce Velocity',
                ],
                'Value': [
                    metrics['total_active_employees'],
                    metrics['total_candidates'],
                    metrics['open_positions'],
                    metrics['retention_vector'],
                    metrics['turnover_rate'],
                    metrics['new_hires_30d'],
                    f"${metrics['total_monthly_payroll']:,.2f}",
                    metrics['cost_per_employee'],
                    metrics['workforce_velocity'],
                ]
            }
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            # Sheet 2: Department Distribution
            dept_data = {
                'Department': [d['name'] for d in metrics['department_distribution']],
                'Employees': [d['value'] for d in metrics['department_distribution']],
                'Percentage': [
                    f"{(d['value'] / sum(x['value'] for x in metrics['department_distribution']) * 100):.1f}%"
                    for d in metrics['department_distribution']
                ]
            }
            df_dept = pd.DataFrame(dept_data)
            df_dept.to_excel(writer, sheet_name='Department Distribution', index=False)
            
            # Sheet 3: Gender Distribution
            gender_data = {
                'Gender': [g['name'] for g in metrics['gender_distribution']],
                'Count': [g['value'] for g in metrics['gender_distribution']],
                'Percentage': [
                    f"{(g['value'] / sum(x['value'] for x in metrics['gender_distribution']) * 100):.1f}%"
                    for g in metrics['gender_distribution']
                ]
            }
            df_gender = pd.DataFrame(gender_data)
            df_gender.to_excel(writer, sheet_name='Gender Distribution', index=False)
            
            # Sheet 4: Designation Distribution
            desig_data = {
                'Designation': [d['name'] for d in metrics['designation_distribution']],
                'Count': [d['value'] for d in metrics['designation_distribution']],
                'Percentage': [
                    f"{(d['value'] / sum(x['value'] for x in metrics['designation_distribution']) * 100):.1f}%"
                    for d in metrics['designation_distribution']
                ]
            }
            df_desig = pd.DataFrame(desig_data)
            df_desig.to_excel(writer, sheet_name='By Designation', index=False)
            
            # Sheet 5: Headcount Trends
            trends = {
                'Month': [t['name'] for t in metrics['headcount_trends']],
                'Headcount': [t['count'] for t in metrics['headcount_trends']],
                'Gratuity Liability': [t['liability'] for t in metrics['headcount_trends']],
            }
            df_trends = pd.DataFrame(trends)
            df_trends.to_excel(writer, sheet_name='Headcount Trends', index=False)
            
            # Sheet 6: Recruitment Funnel
            funnel = {
                'Stage': [s['name'] for s in metrics['recruitment_funnel']],
                'Candidates': [s['value'] for s in metrics['recruitment_funnel']],
            }
            df_funnel = pd.DataFrame(funnel)
            df_funnel.to_excel(writer, sheet_name='Recruitment Funnel', index=False)
            
            # Sheet 7: Payroll Summary
            payroll = metrics['payroll_summary']
            payroll_data = {
                'Period': [f"{payroll['period_month']}/{payroll['period_year']}"],
                'Employees Processed': [payroll['total_employees_processed']],
                'Total Gross Salary': [f"${payroll['total_gross_salary']:,.2f}"],
                'Total Deductions': [f"${payroll['total_deductions']:,.2f}"],
                'Total Net Salary': [f"${payroll['total_net_salary']:,.2f}"],
                'Average Gross': [f"${payroll['average_gross_salary']:,.2f}"],
                'Average Net': [f"${payroll['average_net_salary']:,.2f}"],
            }
            df_payroll = pd.DataFrame(payroll_data)
            df_payroll.to_excel(writer, sheet_name='Payroll Summary', index=False)
        
        output.seek(0)
        return output

    @staticmethod
    def generate_recruitment_report_pdf(db: Session, organization_id: str) -> BytesIO:
        """Generate recruitment analytics report"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = EnhancedReportGenerator._get_styles()
        
        metrics = AnalyticsCalculator.calculate_dashboard_metrics(db, organization_id)
        funnel = AnalyticsCalculator.calculate_recruitment_funnel(db, organization_id)
        
        story.append(Paragraph("RECRUITMENT ANALYTICS REPORT", styles['CustomTitle']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Recruitment Summary
        story.append(Paragraph("RECRUITMENT PIPELINE", styles['SectionHeader']))
        
        recruit_data = [
            ["Metric", "Value"],
            ["Total Candidates", str(metrics['total_candidates'])],
            ["Open Positions", str(metrics['open_positions'])],
            ["Candidates in Pipeline", str(sum(s['value'] for s in funnel))],
        ]
        
        recruit_table = Table(recruit_data, colWidths=[3*inch, 2*inch])
        recruit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EnhancedReportGenerator.COLORS['header']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(recruit_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Funnel details
        story.append(Paragraph("RECRUITMENT FUNNEL", styles['SectionHeader']))
        
        funnel_detail = [["Stage", "Candidates", "% of Total"]]
        total = sum(s['value'] for s in funnel)
        
        for stage in funnel:
            pct = (stage['value'] / total * 100) if total > 0 else 0
            funnel_detail.append([
                stage['name'],
                str(stage['value']),
                f"{pct:.1f}%"
            ])
        
        funnel_table = Table(funnel_detail, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        funnel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EnhancedReportGenerator.COLORS['success']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
        ]))
        
        story.append(funnel_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    @staticmethod
    def generate_payroll_report_pdf(db: Session, organization_id: str) -> BytesIO:
        """Generate payroll analytics report"""
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = EnhancedReportGenerator._get_styles()
        
        payroll = AnalyticsCalculator.calculate_payroll_summary(db, organization_id)
        salary_by_desig = AnalyticsCalculator.calculate_salary_by_designation(db, organization_id)
        coe = AnalyticsCalculator.calculate_cost_of_employment(db, organization_id)
        
        story.append(Paragraph("PAYROLL ANALYTICS REPORT", styles['CustomTitle']))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y')}",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.3*inch))
        
        # Period Summary
        story.append(Paragraph(f"Period: {payroll['period_month']}/{payroll['period_year']}", styles['SectionHeader']))
        
        payroll_summary = [
            ["Metric", "Amount"],
            ["Employees Processed", str(payroll['total_employees_processed'])],
            ["Total Gross Salary", f"${payroll['total_gross_salary']:,.2f}"],
            ["Total Deductions", f"${payroll['total_deductions']:,.2f}"],
            ["Total Net Salary", f"${payroll['total_net_salary']:,.2f}"],
            ["Average Gross", f"${payroll['average_gross_salary']:,.2f}"],
            ["Average Net", f"${payroll['average_net_salary']:,.2f}"],
        ]
        
        summary_table = Table(payroll_summary, colWidths=[3*inch, 2.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EnhancedReportGenerator.COLORS['header']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Salary by Designation
        story.append(Paragraph("SALARY BY DESIGNATION", styles['SectionHeader']))
        
        salary_data = [["Designation", "Average Salary", "Employee Count"]]
        for desig in salary_by_desig:
            salary_data.append([
                desig['name'],
                f"${desig['avg_salary']:,.2f}",
                str(desig['count'])
            ])
        
        salary_table = Table(salary_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        salary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EnhancedReportGenerator.COLORS['header']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        story.append(salary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Cost of Employment
        story.append(Paragraph("COST OF EMPLOYMENT ANALYSIS", styles['SectionHeader']))
        
        coe_data = [
            ["Component", "Amount"],
            ["Total Gross Salary", f"${coe['total_gross_salary']:,.2f}"],
            ["Estimated Payroll Tax (20%)", f"${coe['estimated_payroll_tax']:,.2f}"],
            ["Total Cost per Employee", f"${coe['cost_per_employee']:,.2f}"],
            ["Total Cost of Employment", f"${coe['total_cost_of_employment']:,.2f}"],
        ]
        
        coe_table = Table(coe_data, colWidths=[3*inch, 2.5*inch])
        coe_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), EnhancedReportGenerator.COLORS['danger']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fef2f2')]),
        ]))
        
        story.append(coe_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer
