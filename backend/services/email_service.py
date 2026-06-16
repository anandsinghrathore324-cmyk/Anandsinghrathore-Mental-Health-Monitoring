"""
email_service.py — Centralised email delivery service for AIRA.

Driver: Gmail SMTP via smtplib STARTTLS (smtp.gmail.com, port 587).

Required environment variables:
    SMTP_EMAIL    — the Gmail address used to send OTPs  (e.g. youraccount@gmail.com)
    SMTP_PASSWORD — a Gmail App Password (16-char, no spaces)
                    Generate one at: Google Account → Security → 2-Step Verification → App Passwords

Why an App Password?
    Google blocks regular passwords for "less-secure apps".
    App Passwords are scoped, revocable tokens that work with smtplib.

Usage:
    from services.email_service import EmailService
    ok, err = EmailService.send_otp(to_email="user@example.com", otp_code="123456",
                                     purpose="reset")
    if not ok:
        # handle err string
"""

import logging
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple

from config import Config

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HTML Email Templates
# ---------------------------------------------------------------------------

_BASE_STYLE = (
    'font-family:"Segoe UI",Tahoma,Geneva,Verdana,sans-serif;'
    'background-color:#060813;color:#ffffff;padding:2rem;'
)


def _build_otp_html(otp_code: str, purpose: str, recipient_name: str = "") -> str:
    """Build a branded AIRA OTP email body."""
    greeting = f"Hello {recipient_name}," if recipient_name else "Hello,"

    if purpose == "signup":
        headline = "Verify your email to complete registration"
        body_copy = (
            "Welcome to AIRA Wellness! To complete your account registration and "
            "verify your email address, enter the verification code below:"
        )
        ignore_copy = "If you did not create an AIRA Wellness account, you can safely ignore this email."
    elif purpose == "login":
        headline = "Your one-time login code"
        body_copy = "Use the verification code below to log into your AIRA Wellness account:"
        ignore_copy = "If you did not request this code, you can safely ignore this email."
    else:  # "reset"
        headline = "Reset your AIRA Wellness password"
        body_copy = (
            "We received a request to reset the password for your AIRA Wellness account. "
            "Use the verification code below to continue:"
        )
        ignore_copy = (
            "If you did not request a password reset, you can safely ignore this email. "
            "No changes will be made to your account."
        )

    return f"""
<html>
<body style="{_BASE_STYLE}">
  <div style="max-width:500px;margin:0 auto;background:rgba(255,255,255,0.03);
              border:1px solid rgba(0,242,254,0.2);border-radius:16px;
              padding:2rem;box-shadow:0 0 40px rgba(0,242,254,0.05);">
    <h2 style="color:#00f2fe;text-align:center;font-weight:800;
               letter-spacing:1px;margin-bottom:1.5rem;">AIRA WELLNESS</h2>
    <p style="font-size:0.95rem;line-height:1.6;color:#a9b2c3;">{greeting}</p>
    <p style="font-size:0.95rem;line-height:1.6;color:#a9b2c3;">{headline}</p>
    <p style="font-size:0.95rem;line-height:1.6;color:#a9b2c3;">{body_copy}</p>
    <div style="background:rgba(0,242,254,0.08);border-radius:12px;
                border:1px solid rgba(0,242,254,0.3);padding:1.2rem;
                text-align:center;margin:2rem 0;">
      <span style="font-size:2.2rem;font-weight:900;letter-spacing:8px;
                   color:#00f2fe;font-family:monospace;">{otp_code}</span>
    </div>
    <p style="font-size:0.85rem;color:#ff007f;text-align:center;margin-top:1rem;">
      This verification code will expire in 5 minutes.
    </p>
    <p style="font-size:0.95rem;line-height:1.6;color:#a9b2c3;">{ignore_copy}</p>
    <p style="font-size:0.95rem;line-height:1.6;color:#a9b2c3;margin-top:1.5rem;">
      Best regards,<br>AIRA Wellness Team
    </p>
    <hr style="border:0;border-top:1px solid rgba(255,255,255,0.08);margin:2rem 0;">
    <p style="font-size:0.75rem;color:#6272a4;text-align:center;margin-bottom:0;">
      AIRA Wellness &bull; Student Mental Health &amp; Wellness Platform
    </p>
  </div>
</body>
</html>
"""


def _subject_for_purpose(purpose: str) -> str:
    return {
        "signup": "Verify Your Email Address — AIRA Wellness",
        "login":  "Your AIRA Wellness Login Code",
        "reset":  "Reset Your AIRA Wellness Password",
    }.get(purpose, "Your AIRA Wellness Verification Code")


# ---------------------------------------------------------------------------
# Gmail SMTP STARTTLS driver
# ---------------------------------------------------------------------------

def _send_via_smtp(
    to_email: str,
    subject: str,
    html_body: str,
) -> Tuple[bool, str]:
    """Send email through Gmail SMTP using STARTTLS on port 587.

    Requires:
        SMTP_EMAIL    — sender Gmail address
        SMTP_PASSWORD — Gmail App Password (not the regular Gmail password)
    """
    smtp_server   = Config.SMTP_SERVER    # smtp.gmail.com
    smtp_port     = Config.SMTP_PORT      # 587
    smtp_user     = Config.SMTP_EMAIL
    smtp_password = Config.SMTP_PASSWORD

    if not smtp_user or not smtp_password:
        logger.error(
            "[EMAIL SMTP] SMTP_EMAIL or SMTP_PASSWORD is not configured. "
            "Set these environment variables before running the server."
        )
        return False, (
            "Email is not configured. "
            "Set SMTP_EMAIL and SMTP_PASSWORD environment variables."
        )

    # Build MIME message
    msg = MIMEMultipart("alternative")
    msg["From"]    = f"AIRA Wellness <{smtp_user}>"
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

    # TCP reachability pre-flight
    logger.info("[EMAIL SMTP] Pre-flight: resolving %s ...", smtp_server)
    try:
        resolved_ip = socket.gethostbyname(smtp_server)
        logger.info("[EMAIL SMTP] DNS resolved %s → %s", smtp_server, resolved_ip)
    except socket.gaierror as dns_err:
        logger.error("[EMAIL SMTP] DNS resolution failed: %s", dns_err)
        return False, f"DNS resolution failed for {smtp_server}: {dns_err}"

    try:
        test_sock = socket.create_connection((smtp_server, smtp_port), timeout=5)
        test_sock.close()
        logger.info("[EMAIL SMTP] TCP reachability OK: %s:%s", smtp_server, smtp_port)
    except OSError as tcp_err:
        logger.error(
            "[EMAIL SMTP] TCP reachability FAILED for %s:%s — %s",
            smtp_server, smtp_port, tcp_err,
        )
        return False, (
            f"Cannot reach {smtp_server}:{smtp_port} — {tcp_err}. "
            "If running on Render free tier, outbound SMTP (port 587) may be blocked. "
            "Upgrade to a paid Render plan or use a different mail provider."
        )

    # STARTTLS handshake + send
    logger.info("[EMAIL SMTP] Connecting via STARTTLS to %s:%s ...", smtp_server, smtp_port)
    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            logger.info("[EMAIL SMTP] STARTTLS handshake complete. Authenticating ...")
            server.login(smtp_user, smtp_password)
            logger.info("[EMAIL SMTP] Authenticated. Sending to %s ...", to_email)
            server.sendmail(smtp_user, to_email, msg.as_string())
            logger.info("[EMAIL SMTP] Message delivered to: %s", to_email)
        return True, ""

    except smtplib.SMTPAuthenticationError as auth_err:
        logger.error("[EMAIL SMTP] Authentication failed: %s", auth_err)
        return False, (
            "SMTP authentication failed. Make sure you are using a Gmail App Password "
            "(not your regular Gmail password). Enable 2-Step Verification first, then "
            "generate an App Password at Google Account → Security → App Passwords."
        )
    except smtplib.SMTPRecipientsRefused as rcpt_err:
        logger.error("[EMAIL SMTP] Recipient refused: %s", rcpt_err)
        return False, f"Recipient address rejected by Gmail: {rcpt_err}"
    except smtplib.SMTPException as smtp_err:
        logger.error("[EMAIL SMTP] SMTP protocol error: %s", smtp_err, exc_info=True)
        return False, f"SMTP protocol error: {smtp_err}"
    except OSError as os_err:
        logger.error("[EMAIL SMTP] OS-level network error: %s", os_err, exc_info=True)
        return False, f"Network error sending email: {os_err}"


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class EmailService:
    """Gmail SMTP email delivery service for AIRA OTP flows.

    Always uses smtplib STARTTLS (smtp.gmail.com:587).
    Set SMTP_EMAIL and SMTP_PASSWORD in your environment.
    """

    @staticmethod
    def send_otp(
        to_email: str,
        otp_code: str,
        purpose: str = "reset",
        recipient_name: str = "",
    ) -> Tuple[bool, str]:
        """Send an OTP email to any address via Gmail SMTP.

        Works for any recipient email — no domain verification required.

        Returns:
            (True,  "")           on success
            (False, error_reason) on failure
        """
        subject   = _subject_for_purpose(purpose)
        html_body = _build_otp_html(otp_code, purpose, recipient_name)

        logger.info(
            "[EMAIL] Sending OTP via Gmail SMTP | purpose=%s | to=%s",
            purpose, to_email,
        )
        return _send_via_smtp(to_email, subject, html_body)

    @staticmethod
    def is_configured() -> bool:
        """Return True if SMTP credentials are set and non-empty."""
        smtp_email    = Config.SMTP_EMAIL or ""
        smtp_password = Config.SMTP_PASSWORD or ""
        return bool(smtp_email and smtp_password)
