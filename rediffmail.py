"""
Rediffmail SMTP login and notification helper.

Credentials are read from environment variables (set in .env):
    EMAIL_FROM      — your Rediffmail address
    EMAIL_PASSWORD  — your Rediffmail password
    EMAIL_TO        — recipient address (defaults to EMAIL_FROM)
    SMTP_HOST       — defaults to smtp.rediffmail.com
    SMTP_PORT       — defaults to 465 (SSL)
"""

import os
import ssl
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.image     import MIMEImage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.rediffmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_FROM = os.getenv("EMAIL_FROM", "")
EMAIL_PASS = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO   = os.getenv("EMAIL_TO", EMAIL_FROM)


# ── Core login ────────────────────────────────────────────

def login():
    """Open an authenticated SMTP_SSL session and return it."""
    if not EMAIL_FROM or not EMAIL_PASS:
        raise ValueError(
            "EMAIL_FROM and EMAIL_PASSWORD must be set in .env to use Rediffmail."
        )
    ctx  = ssl.create_default_context()
    smtp = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx, timeout=15)
    smtp.login(EMAIL_FROM, EMAIL_PASS)
    return smtp


def is_configured():
    return bool(EMAIL_FROM and EMAIL_PASS)


# ── Notification ──────────────────────────────────────────

def send_post_notification(title: str, series: str, episode: int,
                            instagram_id: str, image_url: str = "",
                            image_path: str = ""):
    """
    Send an email notification after a post goes live on Instagram.
    Silently skips if email credentials are not configured.
    """
    if not is_configured():
        return

    subject = f"✅ New post live — {series} EP{episode}: {title}"

    html_image = ""
    if image_url:
        html_image = f'<p><img src="{image_url}" style="max-width:480px;border-radius:8px;"></p>'

    html = f"""
<html><body style="font-family:sans-serif;color:#222;max-width:600px">
  <h2 style="color:#e1306c">📸 New Instagram post is live!</h2>
  <table style="border-collapse:collapse;width:100%">
    <tr><td style="padding:6px 12px;font-weight:bold">Series</td>
        <td style="padding:6px 12px">{series}</td></tr>
    <tr style="background:#f9f9f9">
        <td style="padding:6px 12px;font-weight:bold">Episode</td>
        <td style="padding:6px 12px">{episode}</td></tr>
    <tr><td style="padding:6px 12px;font-weight:bold">Title</td>
        <td style="padding:6px 12px">{title}</td></tr>
    <tr style="background:#f9f9f9">
        <td style="padding:6px 12px;font-weight:bold">Instagram ID</td>
        <td style="padding:6px 12px"><code>{instagram_id}</code></td></tr>
  </table>
  {html_image}
  <p style="color:#888;font-size:12px;margin-top:24px">
    Sent by Gemini Instagram Bot · @maddy_4589
  </p>
</body></html>
"""

    text = (
        f"New post live!\n\n"
        f"Series:       {series}\n"
        f"Episode:      {episode}\n"
        f"Title:        {title}\n"
        f"Instagram ID: {instagram_id}\n"
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Attach the final image if a local path is provided
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            img = MIMEImage(f.read(), name=os.path.basename(image_path))
        img.add_header("Content-Disposition", "attachment",
                       filename=os.path.basename(image_path))
        msg.attach(img)

    try:
        with login() as smtp:
            smtp.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        print(f"  📧 Notification sent → {EMAIL_TO}")
    except Exception as e:
        print(f"  ⚠️  Email notification failed: {e}")


# ── CLI smoke-test ────────────────────────────────────────

if __name__ == "__main__":
    print(f"Testing Rediffmail login for {EMAIL_FROM} ...")
    try:
        with login() as smtp:
            print(f"  ✅ Login successful ({SMTP_HOST}:{SMTP_PORT})")
    except Exception as e:
        print(f"  ❌ Login failed: {e}")
