"""
email_service.py — Centralised email delivery service for AIRA.

Driver: Brevo (formerly Sendinblue) transactional email REST API.
        Communicates over HTTPS (port 443) — works on ALL hosting platforms
        including Render free tier where SMTP ports 25/465/587 are blocked.

Why Brevo instead of Gmail SMTP?
    Render.com free tier blocks outbound TCP on ports 25, 465, and 587.
    The error [Errno 101] Network is unreachable is the Render kernel dropping
    the TCP SYN packet before it leaves the host. Brevo's API uses HTTPS
    (port 443) which is never blocked.

Why Brevo instead of Resend?
    Brevo only requires verifying a single SENDER EMAIL ADDRESS.
    No domain ownership, no DNS records, no TXT/DKIM/DMARC setup needed.
    Resend requires full domain verification before you can send to arbitrary users.

Free tier limits:
    300 emails/day · 9,000 emails/month · No credit card required.

Required environment variables:
    BREVO_API_KEY      — API key from Brevo dashboard (Transactional → API Keys)
    BREVO_FROM_EMAIL   — the verified sender email on your Brevo account
    BREVO_FROM_NAME    — display name (optional, defaults to "AIRA Wellness")

Usage:
    from services.email_service import EmailService
    ok, err = EmailService.send_otp(to_email="user@example.com", otp_code="123456",
                                     purpose="reset")
    if not ok:
        # handle err string
"""

import logging
import os
from typing import Tuple

import requests

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
# Brevo REST API driver  (HTTPS port 443 — works on Render free tier)
# ---------------------------------------------------------------------------

_BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _send_via_brevo(
    to_email: str,
    subject: str,
    html_body: str,
) -> Tuple[bool, str]:
    """Send email through the Brevo transactional email REST API.

    Uses HTTPS (port 443) — never blocked on Render free tier.
    Works for any recipient email with no domain verification required.

    Returns:
        (True, "")           on success
        (False, reason_str)  on failure
    """
    api_key    = os.getenv("BREVO_API_KEY", "").strip()
    from_email = os.getenv("BREVO_FROM_EMAIL", "").strip()
    from_name  = os.getenv("BREVO_FROM_NAME", "AIRA Wellness").strip()

    if not api_key:
        logger.error("[EMAIL BREVO] BREVO_API_KEY environment variable is not set.")
        return False, "BREVO_API_KEY environment variable is not set."

    if not from_email:
        logger.error("[EMAIL BREVO] BREVO_FROM_EMAIL environment variable is not set.")
        return False, "BREVO_FROM_EMAIL environment variable is not set."

    payload = {
        "sender": {"name": from_name, "email": from_email},
        "to":     [{"email": to_email}],
        "subject": subject,
        "htmlContent": html_body,
    }

    headers = {
        "accept":       "application/json",
        "api-key":      api_key,
        "content-type": "application/json",
    }

    logger.info("[EMAIL BREVO] Sending via Brevo API | to=%s | subject=%s", to_email, subject)

    try:
        resp = requests.post(
            _BREVO_API_URL,
            json=payload,
            headers=headers,
            timeout=15,
        )
    except requests.exceptions.Timeout:
        logger.error("[EMAIL BREVO] Request timed out after 15 seconds.")
        return False, "Brevo API request timed out."
    except requests.exceptions.ConnectionError as exc:
        logger.error("[EMAIL BREVO] Connection error: %s", exc)
        return False, f"Could not reach Brevo API: {exc}"

    # 201 Created is the normal success response from Brevo
    if resp.status_code in (200, 201):
        try:
            msg_id = resp.json().get("messageId", "unknown")
        except Exception:
            msg_id = "unknown"
        logger.info("[EMAIL BREVO] Accepted by Brevo. messageId=%s → %s", msg_id, to_email)
        return True, ""

    # Error path
    try:
        err_detail = resp.json().get("message") or resp.text
    except Exception:
        err_detail = resp.text or f"HTTP {resp.status_code}"

    logger.error(
        "[EMAIL BREVO] API rejected request. status=%s error=%s → %s",
        resp.status_code, err_detail, to_email,
    )
    return False, f"Brevo API error ({resp.status_code}): {err_detail}"


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class EmailService:
    """Brevo-based email delivery facade for AIRA OTP flows.

    Sends via Brevo REST API (HTTPS port 443).
    Works on Render free tier — no SMTP port restrictions apply.
    Works for any recipient email — no domain verification required.
    """

    @staticmethod
    def send_otp(
        to_email: str,
        otp_code: str,
        purpose: str = "reset",
        recipient_name: str = "",
    ) -> Tuple[bool, str]:
        """Send an OTP verification email via Brevo.

        Args:
            to_email:       recipient's email address
            otp_code:       6-digit OTP string
            purpose:        "signup" | "login" | "reset"
            recipient_name: optional display name for personalisation

        Returns:
            (True,  "")           on success
            (False, error_reason) on failure
        """
        subject   = _subject_for_purpose(purpose)
        html_body = _build_otp_html(otp_code, purpose, recipient_name)

        logger.info(
            "[EMAIL] Dispatching OTP via Brevo | purpose=%s | to=%s",
            purpose, to_email,
        )
        return _send_via_brevo(to_email, subject, html_body)

    @staticmethod
    def is_configured() -> bool:
        """Return True if Brevo credentials are set and non-empty."""
        return bool(
            os.getenv("BREVO_API_KEY", "").strip() and
            os.getenv("BREVO_FROM_EMAIL", "").strip()
        )
