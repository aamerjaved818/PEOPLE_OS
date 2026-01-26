"""
Document Generator Service - ReportLab Implementation
Generates PDF documents using ReportLab (self-contained, no external dependencies)
"""
import os
from datetime import datetime
from typing import Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from sqlalchemy.orm import Session
from backend.domains.hcm.models import DBEmployee
from backend.domains.core.models import DBOrganization


class DocumentGenerator:
    """Service for generating PDF documents using ReportLab"""
    
    def __init__(self):
        # Output directory for generated documents
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'generated_documents')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Company name style
        self.styles.add(ParagraphStyle(
            name='CompanyName',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2563eb'),
            alignment=TA_CENTER,
            spaceAfter=6
        ))
        
        # Company details style
        self.styles.add(ParagraphStyle(
            name='CompanyDetails',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Subject style
        self.styles.add(ParagraphStyle(
            name='Subject',
            parent=self.styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=12,
            spaceBefore=12
        ))
        
        # Body text justified
        self.styles.add(ParagraphStyle(
            name='BodyJustified',
            parent=self.styles['BodyText'],
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
        
        # Date style
        self.styles.add(ParagraphStyle(
            name='DateStyle',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT,
            spaceAfter=12
        ))
    
    def _get_employee_data(self, db: Session, employee_id: str) -> dict:
        """Get employee data"""
        employee = db.query(DBEmployee).filter(DBEmployee.id == employee_id).first()
        
        if not employee:
            raise ValueError(f"Employee {employee_id} not found")
        
        return {
            'id': employee.id,
            'employee_code': employee.employee_code,
            'name': employee.name,
            'designation': employee.designation_rel.name if employee.designation_rel else 'N/A',
            'department': employee.department_rel.name if employee.department_rel else 'N/A',
            'join_date': employee.join_date,
            'status': employee.status,
            'email': employee.email,
            'phone': employee.phone,
            'gross_salary': employee.gross_salary or 0,
        }
    
    def _get_organization_data(self, db: Session, organization_id: str) -> dict:
        """Get organization data"""
        org = db.query(DBOrganization).filter(DBOrganization.id == organization_id).first()
        
        if not org:
            return {
                'name': 'People OS',
                'address': 'Corporate Office',
                'email': 'info@peopleos.com',
                'phone': '+92-XXX-XXXXXXX'
            }
        
        return {
            'name': org.name,
            'address': getattr(org, 'address', 'Corporate Office'),
            'email': getattr(org, 'email', 'info@peopleos.com'),
            'phone': getattr(org, 'phone', '+92-XXX-XXXXXXX')
        }
    
    def _create_letterhead(self, organization: dict):
        """Create letterhead elements"""
        elements = []
        
        # Company name
        elements.append(Paragraph(organization['name'], self.styles['CompanyName']))
        
        # Company details
        details = f"{organization['address']}<br/>Email: {organization['email']} | Phone: {organization['phone']}"
        elements.append(Paragraph(details, self.styles['CompanyDetails']))
        
        # Horizontal line
        elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def generate_experience_letter(
        self,
        db: Session,
        employee_id: str,
        organization_id: str,
        purpose: Optional[str] = None
    ) -> str:
        """Generate experience letter PDF"""
        employee = self._get_employee_data(db, employee_id)
        organization = self._get_organization_data(db, organization_id)
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Create PDF
        filename = f"experience_letter_{employee_id}_{int(datetime.now().timestamp())}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        elements = []
        
        # Letterhead
        elements.extend(self._create_letterhead(organization))
        
        # Date
        elements.append(Paragraph(f"Date: {current_date}", self.styles['DateStyle']))
        
        # Subject
        elements.append(Paragraph("<u>SUBJECT: TO WHOM IT MAY CONCERN</u>", self.styles['Subject']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Content
        content = f"""
        This is to certify that <b>{employee['name']}</b>, bearing Employee Code <b>{employee['employee_code']}</b>, 
        has been employed with {organization['name']} since <b>{employee['join_date']}</b>.
        """
        elements.append(Paragraph(content, self.styles['BodyJustified']))
        
        content2 = f"""
        During the tenure with us, {employee['name']} has been serving as <b>{employee['designation']}</b> 
        in the {employee['department']} department.
        """
        elements.append(Paragraph(content2, self.styles['BodyJustified']))
        
        content3 = f"""
        {employee['name']} has demonstrated professional competence, dedication, and integrity throughout the employment period. 
        The conduct and performance have been satisfactory.
        """
        elements.append(Paragraph(content3, self.styles['BodyJustified']))
        
        content4 = f"This certificate is being issued upon request for {purpose or 'official purposes'}."
        elements.append(Paragraph(content4, self.styles['BodyJustified']))
        
        content5 = f"We wish {employee['name']} all the best in future endeavors."
        elements.append(Paragraph(content5, self.styles['BodyJustified']))
        
        # Signature section
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Sincerely,", self.styles['Normal']))
        elements.append(Spacer(1, 0.8*inch))
        elements.append(Paragraph("_" * 30, self.styles['Normal']))
        elements.append(Paragraph(f"<b>Human Resources Department</b><br/>{organization['name']}", self.styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(name='Footer', parent=self.styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
        elements.append(Paragraph("This is a system-generated document. No signature is required for validation.", footer_style))
        
        doc.build(elements)
        
        return f"/uploads/generated_documents/{filename}"
    
    def generate_salary_certificate(
        self,
        db: Session,
        employee_id: str,
        organization_id: str,
        purpose: Optional[str] = None
    ) -> str:
        """Generate salary certificate PDF"""
        employee = self._get_employee_data(db, employee_id)
        organization = self._get_organization_data(db, organization_id)
        current_date = datetime.now().strftime("%B %d, %Y")
        
        filename = f"salary_certificate_{employee_id}_{int(datetime.now().timestamp())}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        elements = []
        
        # Letterhead
        elements.extend(self._create_letterhead(organization))
        
        # Date
        elements.append(Paragraph(f"Date: {current_date}", self.styles['DateStyle']))
        
        # Subject
        elements.append(Paragraph("<u>SUBJECT: SALARY CERTIFICATE</u>", self.styles['Subject']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Content
        content = f"""
        This is to certify that <b>{employee['name']}</b>, bearing Employee Code <b>{employee['employee_code']}</b>, 
        is currently employed with {organization['name']} as <b>{employee['designation']}</b> in the {employee['department']} department.
        """
        elements.append(Paragraph(content, self.styles['BodyJustified']))
        
        content2 = f"""
        The employee joined our organization on <b>{employee['join_date']}</b> and has been serving with dedication and commitment.
        """
        elements.append(Paragraph(content2, self.styles['BodyJustified']))
        
        # Salary details table
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("<b>Salary Details:</b>", self.styles['Heading3']))
        
        salary_data = [
            ['Description', 'Amount (PKR)'],
            ['Gross Monthly Salary', f"{employee['gross_salary']:,.2f}"],
            ['Annual Gross Salary', f"{employee['gross_salary'] * 12:,.2f}"]
        ]
        
        salary_table = Table(salary_data, colWidths=[3*inch, 2*inch])
        salary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(salary_table)
        
        elements.append(Spacer(1, 0.2*inch))
        content3 = f"This certificate is being issued upon the request of the employee for {purpose or 'official purposes'}."
        elements.append(Paragraph(content3, self.styles['BodyJustified']))
        
        # Signature section
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Sincerely,", self.styles['Normal']))
        elements.append(Spacer(1, 0.8*inch))
        elements.append(Paragraph("_" * 30, self.styles['Normal']))
        elements.append(Paragraph(f"<b>Human Resources Department</b><br/>{organization['name']}", self.styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(name='Footer', parent=self.styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
        elements.append(Paragraph("This is a computer-generated salary certificate and does not require a signature.", footer_style))
        
        doc.build(elements)
        
        return f"/uploads/generated_documents/{filename}"
    
    def generate_employment_verification(
        self,
        db: Session,
        employee_id: str,
        organization_id: str,
        purpose: Optional[str] = None
    ) -> str:
        """Generate employment verification PDF"""
        employee = self._get_employee_data(db, employee_id)
        organization = self._get_organization_data(db, organization_id)
        current_date = datetime.now().strftime("%B %d, %Y")
        
        filename = f"employment_verification_{employee_id}_{int(datetime.now().timestamp())}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=1*inch, bottomMargin=1*inch)
        elements = []
        
        # Letterhead
        elements.extend(self._create_letterhead(organization))
        
        # Date
        elements.append(Paragraph(f"Date: {current_date}", self.styles['DateStyle']))
        
        # Subject
        elements.append(Paragraph("<u>SUBJECT: EMPLOYMENT VERIFICATION</u>", self.styles['Subject']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Content
        content = f"This letter is to verify the employment status of <b>{employee['name']}</b> with {organization['name']}."
        elements.append(Paragraph(content, self.styles['BodyJustified']))
        
        # Employee details table
        elements.append(Spacer(1, 0.2*inch))
        employee_data = [
            ['Employee Name:', employee['name']],
            ['Employee Code:', employee['employee_code']],
            ['Designation:', employee['designation']],
            ['Department:', employee['department']],
            ['Date of Joining:', employee['join_date']],
            ['Employment Status:', employee['status']]
        ]
        
        emp_table = Table(employee_data, colWidths=[2*inch, 3.5*inch])
        emp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(emp_table)
        
        elements.append(Spacer(1, 0.2*inch))
        content2 = f"""
        {employee['name']} is currently employed with our organization in good standing. The employee has been performing duties 
        as {employee['designation']} with professionalism and dedication.
        """
        elements.append(Paragraph(content2, self.styles['BodyJustified']))
        
        content3 = f"This letter is issued as proof of employment for {purpose or 'verification purposes'}."
        elements.append(Paragraph(content3, self.styles['BodyJustified']))
        
        # Signature section
        elements.append(Spacer(1, 0.5*inch))
        elements.append(Paragraph("Sincerely,", self.styles['Normal']))
        elements.append(Spacer(1, 0.8*inch))
        elements.append(Paragraph("_" * 30, self.styles['Normal']))
        elements.append(Paragraph(f"<b>Human Resources Department</b><br/>{organization['name']}", self.styles['Normal']))
        
        # Footer
        elements.append(Spacer(1, 0.3*inch))
        footer_style = ParagraphStyle(name='Footer', parent=self.styles['Normal'], fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
        elements.append(Paragraph(f"This is an official employment verification letter issued by {organization['name']}.", footer_style))
        
        doc.build(elements)
        
        return f"/uploads/generated_documents/{filename}"
    
    def generate_payslip(
        self,
        db: Session,
        employee_id: str,
        organization_id: str,
        period_month: str,
        period_year: str
    ) -> str:
        """Generate payslip PDF"""
        from backend.domains.hcm.models import DBPayrollLedger
        
        employee = self._get_employee_data(db, employee_id)
        organization = self._get_organization_data(db, organization_id)
        
        # Get payslip data
        payslip = db.query(DBPayrollLedger).filter(
            DBPayrollLedger.employee_id == employee_id,
            DBPayrollLedger.period_month == period_month,
            DBPayrollLedger.period_year == period_year
        ).first()
        
        if not payslip:
            raise ValueError(f"Payslip not found for {period_month} {period_year}")
        
        filename = f"payslip_{employee_id}_{period_month}_{period_year}.pdf"
        output_path = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(output_path, pagesize=A4, topMargin=0.75*inch, bottomMargin=0.75*inch)
        elements = []
        
        # Letterhead
        elements.extend(self._create_letterhead(organization))
        
        # Title
        elements.append(Paragraph(f"<u>PAYSLIP - {period_month} {period_year}</u>", self.styles['Subject']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Employee Info Table
        emp_info = [
            ['Employee Name:', employee['name'], 'Employee Code:', employee['employee_code']],
            ['Designation:', employee['designation'], 'Department:', employee['department']],
            ['Payment Mode:', payslip.payment_mode or 'N/A', 'Payment Date:', payslip.payment_date or 'Pending'],
        ]
        
        emp_table = Table(emp_info, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        emp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(emp_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Earnings & Deductions side by side
        earnings_data = [
            ['EARNINGS', 'Amount (PKR)'],
            ['Basic Salary', f"{payslip.basic_salary:,.2f}"],
            ['House Rent Allowance', f"{payslip.house_rent:,.2f}"],
            ['Medical Allowance', f"{payslip.medical_allowance:,.2f}"],
            ['Transport Allowance', f"{payslip.transport_allowance:,.2f}"],
            ['Other Allowances', f"{payslip.other_allowances:,.2f}"],
            ['Overtime', f"{payslip.overtime_amount:,.2f}"],
            ['GROSS SALARY', f"{payslip.gross_salary:,.2f}"],
        ]
        
        deductions_data = [
            ['DEDUCTIONS', 'Amount (PKR)'],
            ['Income Tax', f"{payslip.income_tax:,.2f}"],
            ['EOBI', f"{payslip.eobi_deduction:,.2f}"],
            ['Social Security', f"{payslip.social_security:,.2f}"],
            ['Loan Deduction', f"{payslip.loan_deduction:,.2f}"],
            ['Other Deductions', f"{payslip.other_deductions:,.2f}"],
            ['LOP Deduction', f"{payslip.lop_amount:,.2f}"],
            ['TOTAL DEDUCTIONS', f"{payslip.total_deductions:,.2f}"],
        ]
        
        earnings_table = Table(earnings_data, colWidths=[2*inch, 1.3*inch])
        earnings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#22c55e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#dcfce7')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        deductions_table = Table(deductions_data, colWidths=[2*inch, 1.3*inch])
        deductions_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ef4444')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#fecaca')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        
        # Side by side layout
        side_by_side = Table([[earnings_table, Spacer(0.3*inch, 0), deductions_table]])
        elements.append(side_by_side)
        elements.append(Spacer(1, 0.3*inch))
        
        # Net Pay Summary
        net_pay_data = [
            ['NET SALARY PAYABLE', f"PKR {payslip.net_salary:,.2f}"]
        ]
        net_table = Table(net_pay_data, colWidths=[4*inch, 3*inch])
        net_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(net_table)
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_style = ParagraphStyle(name='PayslipFooter', parent=self.styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
        elements.append(Paragraph("This is a computer-generated payslip and does not require a signature.", footer_style))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}", footer_style))
        
        doc.build(elements)
        
        return f"/uploads/generated_documents/{filename}"
    
    def generate_document_by_type(
        self,
        db: Session,
        document_type: str,
        employee_id: str,
        organization_id: str,
        purpose: Optional[str] = None
    ) -> str:
        """Generate document based on type"""
        type_map = {
            'Experience Letter': self.generate_experience_letter,
            'Salary Certificate': self.generate_salary_certificate,
            'Employment Verification': self.generate_employment_verification,
        }
        
        generator = type_map.get(document_type)
        if not generator:
            raise ValueError(f"Unsupported document type: {document_type}")
        
        return generator(db, employee_id, organization_id, purpose)


# Global instance
document_generator = DocumentGenerator()
