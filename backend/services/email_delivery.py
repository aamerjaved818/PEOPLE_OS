"""
Email Delivery Service
Handles report delivery via email with templates
"""

from datetime import datetime
from typing import Dict, List, Optional
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
from jinja2 import Template
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)


class EmailTemplate(BaseModel):
    """Email template model"""
    name: str
    subject: str
    html_content: str
    text_content: str


class EmailConfig(BaseModel):
    """Email configuration"""
    smtp_host: str
    smtp_port: int = 587
    use_tls: bool = True
    sender_email: EmailStr
    sender_password: str
    sender_name: str = "peopleOS eBusiness Suite"


class ReportEmailPayload(BaseModel):
    """Payload for report email"""
    schedule_id: str
    report_name: str
    report_type: str
    format: str
    recipients: List[EmailStr]
    include_summary: bool = True
    generated_at: datetime
    file_path: Optional[str] = None
    metrics_summary: Optional[Dict] = None


class EmailDeliveryService:
    """Service for sending report emails"""

    # Email templates
    TEMPLATES = {
        "report_delivery": EmailTemplate(
            name="report_delivery",
            subject="Scheduled Report: {report_name}",
            html_content="""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background-color: #3b82f6; color: white; padding: 20px; border-radius: 5px; }
                    .content { margin: 20px 0; }
                    .summary { background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 15px 0; }
                    .metric { margin: 10px 0; }
                    .metric-label { font-weight: bold; color: #1f2937; }
                    .metric-value { color: #3b82f6; font-size: 1.2em; }
                    .footer { border-top: 1px solid #e5e7eb; margin-top: 20px; padding-top: 20px; font-size: 0.9em; color: #9ca3af; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>📊 {report_name}</h1>
                        <p>Report Type: {report_type} | Format: {format}</p>
                    </div>
                    
                    <div class="content">
                        <p>Hello,</p>
                        <p>Your scheduled report <strong>{report_name}</strong> has been generated and is ready for download.</p>
                        
                        {% if include_summary and metrics_summary %}
                        <div class="summary">
                            <h3>Report Summary</h3>
                            {% for metric, value in metrics_summary.items() %}
                            <div class="metric">
                                <span class="metric-label">{{ metric }}:</span>
                                <span class="metric-value">{{ value }}</span>
                            </div>
                            {% endfor %}
                        </div>
                        {% endif %}
                        
                        <p>
                            <strong>Report Details:</strong><br>
                            Type: {report_type}<br>
                            Format: {format}<br>
                            Generated: {generated_at}<br>
                        </p>
                        
                        <p>
                            The report is attached to this email. If you have any questions or need assistance,
                            please contact your administrator.
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated message from peopleOS eBusiness Suite.</p>
                        <p>You are receiving this email because you are subscribed to scheduled reports.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            text_content="""
            {report_name}
            
            Your scheduled report {report_name} has been generated and is ready for download.
            
            Report Details:
            Type: {report_type}
            Format: {format}
            Generated: {generated_at}
            
            {% if include_summary and metrics_summary %}
            Report Summary:
            {% for metric, value in metrics_summary.items() %}
            - {{ metric }}: {{ value }}
            {% endfor %}
            {% endif %}
            
            This is an automated message from peopleOS eBusiness Suite.
            """
        ),
        "schedule_confirmation": EmailTemplate(
            name="schedule_confirmation",
            subject="Report Schedule Confirmed: {report_name}",
            html_content="""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Schedule Confirmation</h2>
                <p>Your report schedule has been created successfully.</p>
                <p>
                    <strong>Report Name:</strong> {report_name}<br>
                    <strong>Frequency:</strong> {frequency}<br>
                    <strong>First Report:</strong> {next_run}<br>
                </p>
                <p>You will receive this report via email at the scheduled time.</p>
            </body>
            </html>
            """,
            text_content="""
            Schedule Confirmation
            
            Your report schedule has been created successfully.
            
            Report Name: {report_name}
            Frequency: {frequency}
            First Report: {next_run}
            
            You will receive this report via email at the scheduled time.
            """
        ),
        "delivery_failed": EmailTemplate(
            name="delivery_failed",
            subject="Report Delivery Failed: {report_name}",
            html_content="""
            <!DOCTYPE html>
            <html>
            <body>
                <h2>Report Delivery Failed</h2>
                <p>We encountered an error while generating your scheduled report.</p>
                <p>
                    <strong>Report Name:</strong> {report_name}<br>
                    <strong>Error:</strong> {error_message}<br>
                    <strong>Time:</strong> {timestamp}<br>
                </p>
                <p>Please contact your administrator if this issue persists.</p>
            </body>
            </html>
            """,
            text_content="""
            Report Delivery Failed
            
            We encountered an error while generating your scheduled report.
            
            Report Name: {report_name}
            Error: {error_message}
            Time: {timestamp}
            
            Please contact your administrator if this issue persists.
            """
        )
    }

    def __init__(self, config: EmailConfig):
        """Initialize email service"""
        self.config = config
        logger.info(f"Email service initialized for {config.sender_email}")

    def send_report_email(
        self,
        payload: ReportEmailPayload,
        file_path: Optional[str] = None,
        retry_count: int = 3
    ) -> bool:
        """Send report via email with attachment"""
        try:
            # Create email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Scheduled Report: {payload.report_name}"
            msg["From"] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg["To"] = ", ".join(payload.recipients)

            # Render templates
            template = self.TEMPLATES["report_delivery"]
            context = {
                "report_name": payload.report_name,
                "report_type": payload.report_type,
                "format": payload.format,
                "generated_at": payload.generated_at.strftime("%Y-%m-%d %H:%M:%S"),
                "include_summary": payload.include_summary,
                "metrics_summary": payload.metrics_summary or {},
            }

            # Create text and HTML parts
            text_part = MIMEText(
                Template(template.text_content).render(**context),
                "plain"
            )
            html_part = MIMEText(
                Template(template.html_content).render(**context),
                "html"
            )

            msg.attach(text_part)
            msg.attach(html_part)

            # Attach report file if provided
            if file_path:
                self._attach_file(msg, file_path, payload.format)

            # Send email with retry logic
            for attempt in range(retry_count):
                try:
                    self._send_smtp(msg, payload.recipients)
                    logger.info(
                        f"Report email sent to {', '.join(payload.recipients)} "
                        f"for schedule {payload.schedule_id}"
                    )
                    return True
                except Exception as e:
                    if attempt < retry_count - 1:
                        logger.warning(f"Retry {attempt + 1}/{retry_count}: {e}")
                        continue
                    raise

        except Exception as e:
            logger.error(f"Failed to send report email: {e}")
            return False

    def send_confirmation_email(
        self,
        recipients: List[EmailStr],
        report_name: str,
        frequency: str,
        next_run: datetime
    ) -> bool:
        """Send schedule confirmation email"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Report Schedule Confirmed: {report_name}"
            msg["From"] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg["To"] = ", ".join(recipients)

            template = self.TEMPLATES["schedule_confirmation"]
            context = {
                "report_name": report_name,
                "frequency": frequency,
                "next_run": next_run.strftime("%Y-%m-%d %H:%M:%S"),
            }

            text_part = MIMEText(
                Template(template.text_content).render(**context),
                "plain"
            )
            html_part = MIMEText(
                Template(template.html_content).render(**context),
                "html"
            )

            msg.attach(text_part)
            msg.attach(html_part)

            self._send_smtp(msg, recipients)
            logger.info(f"Confirmation email sent to {', '.join(recipients)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send confirmation email: {e}")
            return False

    def send_failure_notification(
        self,
        recipients: List[EmailStr],
        report_name: str,
        error_message: str
    ) -> bool:
        """Send delivery failure notification"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"Report Delivery Failed: {report_name}"
            msg["From"] = f"{self.config.sender_name} <{self.config.sender_email}>"
            msg["To"] = ", ".join(recipients)

            template = self.TEMPLATES["delivery_failed"]
            context = {
                "report_name": report_name,
                "error_message": error_message,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            }

            text_part = MIMEText(
                Template(template.text_content).render(**context),
                "plain"
            )
            html_part = MIMEText(
                Template(template.html_content).render(**context),
                "html"
            )

            msg.attach(text_part)
            msg.attach(html_part)

            self._send_smtp(msg, recipients)
            logger.info(f"Failure notification sent to {', '.join(recipients)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send failure notification: {e}")
            return False

    def _attach_file(self, msg: MIMEMultipart, file_path: str, file_format: str) -> None:
        """Attach report file to email"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            filename = f"report.{file_format.lower()}"
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            msg.attach(part)
            logger.info(f"Attached file: {filename}")

        except FileNotFoundError:
            logger.error(f"Report file not found: {file_path}")
        except Exception as e:
            logger.error(f"Failed to attach file: {e}")

    def _send_smtp(self, msg: MIMEMultipart, recipients: List[EmailStr]) -> None:
        """Send email via SMTP"""
        with smtplib.SMTP(self.config.smtp_host, self.config.smtp_port) as server:
            if self.config.use_tls:
                server.starttls()
            server.login(self.config.sender_email, self.config.sender_password)
            server.sendmail(
                self.config.sender_email,
                recipients,
                msg.as_string()
            )


# Singleton instance
_email_service: Optional[EmailDeliveryService] = None


def get_email_service(config: Optional[EmailConfig] = None) -> EmailDeliveryService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        if config is None:
            raise ValueError("Email configuration required for initialization")
        _email_service = EmailDeliveryService(config)
    return _email_service
