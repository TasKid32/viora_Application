"""
Email Service — SMTP email sending for password reset and notifications.

Uses Python's built-in smtplib for zero additional dependency approach.
Falls back gracefully when SMTP is not configured (logs warning).
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmailService:
    """SMTP email service using Python's built-in smtplib.

    Configuration via environment variables:
    - SMTP_HOST: SMTP server (e.g. smtp.gmail.com)
    - SMTP_PORT: Port (default 587 for TLS)
    - SMTP_USERNAME: Login username
    - SMTP_PASSWORD: Login password (use App Password for Gmail)
    - SMTP_FROM_EMAIL: Sender email address
    - SMTP_USE_TLS: Enable TLS (default True)
    """

    def __init__(self):
        self.host = getattr(settings, "SMTP_HOST", None)
        self.port = getattr(settings, "SMTP_PORT", 587)
        self.username = getattr(settings, "SMTP_USERNAME", None)
        self.password = getattr(settings, "SMTP_PASSWORD", None)
        self.from_email = getattr(settings, "SMTP_FROM_EMAIL", None)
        self.use_tls = getattr(settings, "SMTP_USE_TLS", True)

    @property
    def is_configured(self) -> bool:
        """Check if SMTP settings are properly configured."""
        return all([self.host, self.username, self.password, self.from_email])

    def _send_email(self, to_email: str, subject: str, html_body: str) -> bool:
        """Send an email via SMTP.

        Returns True if sent successfully, False otherwise.
        """
        if not self.is_configured:
            logger.warning(
                "SMTP not configured — email to %s not sent. "
                "Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL in .env",
                to_email,
            )
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Viora Support <{self.from_email}>"
            msg["To"] = to_email

            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.host, self.port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info("Email sent successfully to: %s", to_email)
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed — check SMTP_USERNAME/SMTP_PASSWORD")
            return False
        except smtplib.SMTPException as e:
            logger.error("SMTP error sending email to %s: %s", to_email, e)
            return False
        except Exception as e:
            logger.error("Unexpected error sending email to %s: %s", to_email, e)
            return False

    def send_password_reset(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email with a secure token link.

        Args:
            to_email: Recipient email address
            reset_token: URL-safe timed token from itsdangerous

        Returns:
            True if email was sent successfully
        """
        frontend_url = getattr(settings, "FRONTEND_URL", "http://192.168.0.105:8000")
        reset_url = f"{frontend_url}/api/auth/reset-password?token={reset_token}"

        subject = "Viora — Password Reset Request"
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Viora</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0;">Career Development Platform</p>
            </div>
            <div style="padding: 30px; background: #f9fafb; border-radius: 0 0 10px 10px;">
                <h2 style="color: #1f2937;">Password Reset</h2>
                <p style="color: #4b5563;">You requested a password reset for your Viora account.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <table align="center" cellspacing="0" cellpadding="0" border="0">
                        <tr>
                            <td align="center" bgcolor="#667eea" style="border-radius: 6px;">
                                <a href="{reset_url}" target="_blank" 
                                   style="padding: 12px 30px; color: #ffffff; text-decoration: none; font-weight: bold; display: inline-block;">
                                    Reset Password
                                </a>
                            </td>
                        </tr>
                    </table>
                </div>
                
                <p style="color: #6b7280; font-size: 14px;">
                    This link will expire in {getattr(settings, 'PASSWORD_RESET_EXPIRE_MINUTES', 30)} minutes.
                </p>
            </div>
        </body>
        </html>
        """
        return self._send_email(to_email, subject, html_body)
        return self._send_email(to_email, subject, html_body)

    def send_password_changed_notification(self, to_email: str) -> bool:
        """Notify user that their password was changed (security best practice)."""
        subject = "Viora — Password Changed Successfully"
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">Viora</h1>
            </div>
            <div style="padding: 30px; background: #f9fafb; border-radius: 0 0 10px 10px;">
                <h2 style="color: #1f2937;">Password Changed</h2>
                <p style="color: #4b5563;">
                    Your Viora account password has been changed successfully.
                </p>
                <p style="color: #ef4444; font-size: 14px;">
                    If you did not make this change, please contact support immediately.
                </p>
            </div>
        </body>
        </html>
        """
        return self._send_email(to_email, subject, html_body)


# Singleton
email_service = EmailService()
