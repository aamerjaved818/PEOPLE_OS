"""
Notification Service
Handles creating and sending notifications via email, SMS, and in-app
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.domains.hcm.models import DBNotification, DBNotificationPreference, DBEmployee
import time


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        # Email configuration (using SMTP)
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@peopleos.com")
        
        # SMS configuration (Twilio - optional)
        self.twilio_enabled = os.getenv("TWILIO_ENABLED", "false").lower() == "true"
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID", "")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN", "")
        self.twilio_phone = os.getenv("TWILIO_PHONE", "")
    
    def create_notification(
        self,
        db: Session,
        recipient_id: str,
        organization_id: str,
        notification_type: str,
        title: str,
        message: str,
        action_url: Optional[str] = None,
        sender_id: Optional[str] = None
    ) -> DBNotification:
        """Create a new in-app notification"""
        notification = DBNotification(
            id=f"NOTIF-{int(time.time() * 1000)}",
            organization_id=organization_id,
            recipient_id=recipient_id,
            sender_id=sender_id,
            type=notification_type,
            title=title,
            message=message,
            action_url=action_url,
            is_read=False,
            created_by=sender_id or "System",
            updated_by=sender_id or "System"
        )
        
        db.add(notification)
        db.commit()
        db.refresh(notification)
        
        # Get preferences and send via enabled channels
        self._send_via_channels(db, notification)
        
        return notification
    
    def _send_via_channels(self, db: Session, notification: DBNotification):
        """Send notification via configured channels based on preferences"""
        # Get user preferences
        preferences = db.query(DBNotificationPreference).filter(
            DBNotificationPreference.employee_id == notification.recipient_id,
            DBNotificationPreference.notification_type == notification.type
        ).first()
        
        # Get recipient details
        recipient = db.query(DBEmployee).filter(
            DBEmployee.id == notification.recipient_id
        ).first()
        
        if not recipient:
            return
        
        # Default preferences if not set
        email_enabled = preferences.email_enabled if preferences else True
        sms_enabled = preferences.sms_enabled if preferences else False
        
        # Send email
        if email_enabled and recipient.email:
            success = self.send_email(
                recipient.email,
                notification.title,
                notification.message,
                notification.action_url
            )
            if success:
                notification.is_sent_email = True
                db.commit()
        
        # Send SMS (if enabled and configured)
        if sms_enabled and recipient.personal_phone and self.twilio_enabled:
            success = self.send_sms(
                recipient.personal_phone,
                f"{notification.title}: {notification.message}"
            )
            if success:
                notification.is_sent_sms = True
                db.commit()
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        action_url: Optional[str] = None
    ) -> bool:
        """Send email notification"""
        if not self.smtp_user or not self.smtp_password:
            print("Email not configured - skipping email send")
            return False
        
        try:
            # Create HTML email
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #2563eb;">{subject}</h2>
                        <p>{body}</p>
                        {f'<p><a href="{action_url}" style="background-color: #2563eb; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 10px;">View Details</a></p>' if action_url else ''}
                        <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;">
                        <p style="color: #666; font-size: 12px;">This is an automated notification from People OS. Please do not reply to this email.</p>
                    </div>
                </body>
            </html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            msg.attach(MIMEText(body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            print(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_sms(self, phone: str, message: str) -> bool:
        """Send SMS notification via Twilio"""
        if not self.twilio_enabled:
            print("SMS not configured - skipping SMS send")
            return False
        
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            message = client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=phone
            )
            
            print(f"SMS sent to {phone}: {message.sid}")
            return True
            
        except Exception as e:
            print(f"Failed to send SMS: {e}")
            return False
    
    def mark_as_read(self, db: Session, notification_id: str) -> bool:
        """Mark notification as read"""
        notification = db.query(DBNotification).filter(
            DBNotification.id == notification_id
        ).first()
        
        if notification:
            notification.is_read = True
            notification.read_at = datetime.now().isoformat()
            db.commit()
            return True
        
        return False
    
    def get_unread_count(self, db: Session, employee_id: str) -> int:
        """Get unread notification count for employee"""
        return db.query(DBNotification).filter(
            DBNotification.recipient_id == employee_id,
            DBNotification.is_read == False
        ).count()
    
    def get_my_notifications(
        self,
        db: Session,
        employee_id: str,
        unread_only: bool = False,
        limit: int = 50
    ):
        """Get notifications for employee"""
        query = db.query(DBNotification).filter(
            DBNotification.recipient_id == employee_id
        )
        
        if unread_only:
            query = query.filter(DBNotification.is_read == False)
        
        notifications = query.order_by(
            DBNotification.created_at.desc()
        ).limit(limit).all()
        
        return notifications


# Global instance
notification_service = NotificationService()


# Helper functions for common notification types
def notify_leave_approved(db: Session, leave_request, approver_id: str):
    """Notify employee that leave was approved"""
    notification_service.create_notification(
        db=db,
        recipient_id=leave_request.employee_id,
        organization_id=leave_request.organization_id,
        notification_type="leave_approved",
        title="Leave Request Approved",
        message=f"Your {leave_request.type} leave request from {leave_request.start_date} to {leave_request.end_date} has been approved.",
        action_url=f"/self-service/leave-requests/{leave_request.id}",
        sender_id=approver_id
    )


def notify_document_ready(db: Session, doc_request, approver_id: str):
    """Notify employee that document is ready"""
    notification_service.create_notification(
        db=db,
        recipient_id=doc_request.employee_id,
        organization_id=doc_request.organization_id,
        notification_type="document_ready",
        title="Document Ready",
        message=f"Your requested {doc_request.document_type} is ready for download.",
        action_url=f"/self-service/documents",
        sender_id=approver_id
    )


def notify_info_update_approved(db: Session, update_request, approver_id: str):
    """Notify employee that info update was approved"""
    notification_service.create_notification(
        db=db,
        recipient_id=update_request.employee_id,
        organization_id=update_request.organization_id,
        notification_type="info_update_approved",
        title="Information Update Approved",
        message=f"Your request to update {update_request.field_name} has been approved.",
        action_url=f"/self-service/profile",
        sender_id=approver_id
    )
