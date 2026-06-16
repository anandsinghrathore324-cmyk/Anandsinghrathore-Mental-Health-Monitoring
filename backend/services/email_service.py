"""
email_service.py — Centralised, production-ready email delivery service for AIRA.

Primary driver  : Resend HTTP API  (works on Render free tier — uses HTTPS port 443)
Local fallback  : smtplib STARTTLS (used only when RESEND_API_KEY is absent)

Why Resend instead of Gmail SMTP?
  Render.com blocks outbound TCP on ports 25, 465, and 587 for ALL free-tier
  services to prevent spam abuse.  The error "[Errno 101] Network is unreachable"
  is Render's kernel dropping the SYN packet before it ever leaves the host.
  Resend communicates entirely over HTTPS (port 443), which Render never blocks.

Usage:
    from services.email_service import EmailService
    ok, err = EmailService.send_otp(to_email="user@example.com", otp_code="123456",
                                     purpose="reset")
    if not ok:
        # handle err string
"""

import logging
import os
import smtplib
import socket
import time
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
# Resend HTTP API driver  (primary — works on Render free tier)
# ---------------------------------------------------------------------------

def _send_via_resend(
    to_email: str,
    subject: str,
    html_body: str,
) -> Tuple[bool, str]:
    """Send email through the Resend REST API over HTTPS (port 443).

    Returns:
        (True, "")          on success
        (False, reason_str) on failure
    """
    api_key = os.getenv("RESEND_API_KEY", "").strip()
    if not api_key:
        return False, "RESEND_API_KEY environment variable is not set."

    from_address = os.getenv("RESEND_FROM_ADDRESS", "").strip()
    if not from_address:
        return False, "RESEND_FROM_ADDRESS environment variable is not set."

    import requests  # already in requirements.txt

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "from": from_address,
        "to":   [to_email],
        "subject": subject,
        "html": html_body,
    }

    logger.info("[EMAIL] Sending via Resend API to: %s | subject: %s", to_email, subject)

    try:
        resp = requests.post(
            "https://api.resend.com/emails",
            json=payload,
            headers=headers,
            timeout=15,
        )
    except requests.exceptions.Timeout:
        return False, "Resend API request timed out after 15 seconds."
    except requests.exceptions.ConnectionError as exc:
        return False, f"Could not reach Resend API: {exc}"

    if resp.status_code in (200, 201):
        data = resp.json()
        email_id = data.get("id", "unknown")
        logger.info("[EMAIL] Resend accepted message. id=%s → %s", email_id, to_email)
        return True, ""

    try:
        err_detail = resp.json().get("message") or resp.text
    except Exception:
        err_detail = resp.text or f"HTTP {resp.status_code}"

    logger.error(
        "[EMAIL] Resend API rejected request. status=%s error=%s → %s",
        resp.status_code, err_detail, to_email,
    )
    return False, f"Resend API error ({resp.status_code}): {err_detail}"


# ---------------------------------------------------------------------------
# smtplib STARTTLS driver  (local development fallback only)
# ---------------------------------------------------------------------------

def _send_via_smtp(
    to_email: str,
    subject: str,
    html_body: str,
) -> Tuple[bool, str]:
    """Send email through Gmail SMTP using STARTTLS.

    This driver is intentionally used ONLY in local development
    (IS_PRODUCTION=False).  On Render free tier it will fail with
    [Errno 101] because ports 465/587 are kernel-blocked.
    """
    smtp_server   = Config.SMTP_SERVER
    smtp_port     = Config.SMTP_PORT
    smtp_user     = Config.SMTP_EMAIL
    smtp_password = Config.SMTP_PASSWORD

    if not smtp_user or not smtp_password:
        return False, "SMTP_EMAIL or SMTP_PASSWORD is not configured."

    msg = MIMEMultipart("alternative")
    msg["From"]    = smtp_user
    msg["To"]      = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))

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
        logger.info("[EMAIL SMTP] TCP reachability check passed: %s:%s", smtp_server, smtp_port)
    except OSError as tcp_err:
        logger.error(
            "[EMAIL SMTP] TCP reachability FAILED for %s:%s — %s. "
            "If running on Render free tier, SMTP ports are blocked. "
            "Set RESEND_API_KEY and RESEND_FROM_ADDRESS to use the Resend driver instead.",
            smtp_server, smtp_port, tcp_err,
        )
        return False, (
            f"[Errno {getattr(tcp_err, 'errno', '?')}] Cannot reach {smtp_server}:{smtp_port}. "
            "Render free tier blocks SMTP ports. Use Resend driver instead."
        )

    logger.info("[EMAIL SMTP] Connecting via STARTTLS to %s:%s ...", smtp_server, smtp_port)
    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            logger.info("[EMAIL SMTP] STARTTLS handshake complete. Authenticating ...")
            server.login(smtp_user, smtp_password)
            logger.info("[EMAIL SMTP] Authentication successful. Sending message ...")
            server.sendmail(smtp_user, to_email, msg.as_string())
            logger.info("[EMAIL SMTP] Message delivered successfully to: %s", to_email)
        return True, ""

    except smtplib.SMTPAuthenticationError as auth_err:
        logger.error("[EMAIL SMTP] Authentication failed: %s", auth_err)
        return False, (
            "SMTP authentication failed. Ensure you are using a Gmail App Password, "
            "not your regular Gmail password. Enable 2-FA on Google account first."
        )
    except smtplib.SMTPException as smtp_err:
        logger.error("[EMAIL SMTP] SMTP protocol error: %s", smtp_err, exc_info=True)
        return False, f"SMTP protocol error: {smtp_err}"
    except OSError as os_err:
        logger.error("[EMAIL SMTP] OS-level network error: %s", os_err, exc_info=True)
        return False, f"Network error: {os_err}"


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class EmailService:
    """Unified email delivery facade.

    Driver selection priority:
      1. Resend HTTP API — if RESEND_API_KEY env var is set  (always use in prod)
      2. smtplib STARTTLS — local dev fallback only
    """

    @staticmethod
    def send_otp(
        to_email: str,
        otp_code: str,
        purpose: str = "reset",
        recipient_name: str = "",
    ) -> Tuple[bool, str]:
        """Send an OTP email to the given address.

        Returns:
            (True,  "")           on success
            (False, error_reason) on failure
        """
        subject   = _subject_for_purpose(purpose)
        html_body = _build_otp_html(otp_code, purpose, recipient_name)

        resend_key = os.getenv("RESEND_API_KEY", "").strip()

        if resend_key:
            logger.info("[EMAIL] Driver selected: Resend (RESEND_API_KEY is set)")
            return _send_via_resend(to_email, subject, html_body)

        if Config.IS_PRODUCTION:
            logger.error(
                "[EMAIL] Production environment detected but RESEND_API_KEY is not set. "
                "Gmail SMTP will fail on Render free tier (ports 465/587 are blocked). "
                "Add RESEND_API_KEY and RESEND_FROM_ADDRESS to your Render environment variables."
            )
            return False, (
                "Email delivery is not configured for production. "
                "Set RESEND_API_KEY and RESEND_FROM_ADDRESS in Render environment variables."
            )

        logger.info("[EMAIL] Driver selected: smtplib STARTTLS (local dev fallback)")
        return _send_via_smtp(to_email, subject, html_body)

    @staticmethod
    def is_configured() -> bool:
        """Return True if at least one email delivery driver is ready."""
        resend_key  = os.getenv("RESEND_API_KEY", "").strip()
        resend_from = os.getenv("RESEND_FROM_ADDRESS", "").strip()
        if resend_key and resend_from:
            return True
        smtp_email    = Config.SMTP_EMAIL or ""
        smtp_password = Config.SMTP_PASSWORD or ""
        if smtp_email and smtp_password:
            if "your-gmail" not in smtp_email and "your-gmail" not in smtp_password:
                return True
        return False
