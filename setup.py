#!/usr/bin/env python3
"""
Interactive setup wizard for Gemini Instagram Bot.
Run:  python setup.py
"""

import os
import sys
import subprocess


# ── ANSI colours ──────────────────────────────────────────
def _c(code, text): return f"\033[{code}m{text}\033[0m"
def bold(t):   return _c("1", t)
def green(t):  return _c("32", t)
def yellow(t): return _c("33", t)
def cyan(t):   return _c("36", t)
def red(t):    return _c("31", t)
def dim(t):    return _c("2", t)


BANNER = f"""
{cyan('╔══════════════════════════════════════════════════════╗')}
{cyan('║')}   {bold('Gemini Instagram Bot — Setup Wizard')}                {cyan('║')}
{cyan('║')}   {dim('by @mudassaraiai-collab')}                              {cyan('║')}
{cyan('╚══════════════════════════════════════════════════════╝')}
"""

PLACEHOLDERS = {
    "your_gemini_api_key_here",
    "your_instagram_access_token_here",
    "your_imgbb_api_key_here",
}


# ── Helpers ───────────────────────────────────────────────

def load_env(path=".env"):
    values = {}
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    values[k.strip()] = v.strip()
    return values


def write_env(values, path=".env"):
    lines = [
        "# ── Instagram / Gemini / ImgBB ──────────────────────",
        "",
        "# Gemini API Key — https://aistudio.google.com/app/apikey",
        f"GEMINI_API_KEY={values.get('GEMINI_API_KEY', '')}",
        "",
        "# Instagram Business Account ID",
        f"IG_USER_ID={values.get('IG_USER_ID', '')}",
        "",
        "# Meta Long-Lived Access Token",
        f"IG_ACCESS_TOKEN={values.get('IG_ACCESS_TOKEN', '')}",
        "",
        "# ImgBB API Key — https://api.imgbb.com",
        f"IMGBB_API_KEY={values.get('IMGBB_API_KEY', '')}",
        "",
        "# ── Email notifications (Rediffmail SMTP) ────────────",
        "",
        f"EMAIL_FROM={values.get('EMAIL_FROM', '')}",
        f"EMAIL_PASSWORD={values.get('EMAIL_PASSWORD', '')}",
        f"EMAIL_TO={values.get('EMAIL_TO', '')}",
        f"SMTP_HOST={values.get('SMTP_HOST', 'smtp.rediffmail.com')}",
        f"SMTP_PORT={values.get('SMTP_PORT', '465')}",
        "",
    ]
    with open(path, "w") as f:
        f.write("\n".join(lines))


def ask(prompt, current="", secret=False):
    suffix = f" {dim(f'[current: {current[:6]}…]')}" if current else ""
    full_prompt = f"  {cyan('›')} {prompt}{suffix}: "
    try:
        if secret:
            import getpass
            val = getpass.getpass(full_prompt)
        else:
            val = input(full_prompt)
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
    return val.strip()


def confirm(prompt, default=True):
    yn = "Y/n" if default else "y/N"
    try:
        ans = input(f"  {cyan('›')} {prompt} [{yn}]: ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        sys.exit(0)
    if not ans:
        return default
    return ans in ("y", "yes")


def section(title):
    print(f"\n{bold(title)}")
    print(dim("─" * 54))


def status(ok, msg):
    icon = green("✔") if ok else (yellow("⚠") if ok is None else red("✘"))
    print(f"    {icon}  {msg}")


# ── API smoke-tests (optional, non-fatal) ─────────────────

def _test_gemini(key):
    try:
        import google.generativeai as genai
        genai.configure(api_key=key)
        list(genai.list_models())
        return True, "Gemini API reachable"
    except ImportError:
        return None, "google-generativeai not installed yet — skipping test"
    except Exception as e:
        return False, str(e)


def _test_instagram(token):
    try:
        import requests
        r = requests.get(
            "https://graph.facebook.com/v21.0/me",
            params={"access_token": token, "fields": "id,name"},
            timeout=10,
        )
        data = r.json()
        if "id" in data:
            return True, f"Token valid — account: {data.get('name', data['id'])}"
        return False, data.get("error", {}).get("message", str(data))
    except ImportError:
        return None, "requests not installed yet — skipping test"
    except Exception as e:
        return False, str(e)


def _test_rediffmail(values):
    try:
        import smtplib, ssl
        host  = values.get("SMTP_HOST", "smtp.rediffmail.com")
        port  = int(values.get("SMTP_PORT", "465"))
        user  = values.get("EMAIL_FROM", "")
        pwd   = values.get("EMAIL_PASSWORD", "")
        ctx   = ssl.create_default_context()
        with smtplib.SMTP_SSL(host, port, context=ctx, timeout=10) as s:
            s.login(user, pwd)
        return True, f"Login OK — {user}"
    except Exception as e:
        return False, str(e)


# ── Step definitions ──────────────────────────────────────

STEPS = [
    {
        "key":      "GEMINI_API_KEY",
        "label":    "Google Gemini API Key",
        "hint":     "https://aistudio.google.com/app/apikey  →  Create API key",
        "validate": lambda v: len(v) > 10,
        "test":     _test_gemini,
    },
    {
        "key":      "IG_USER_ID",
        "label":    "Instagram Business Account ID",
        "hint":     "Meta Graph API Explorer  →  /me?fields=id\n"
                    "         (account must be Business or Creator type)",
        "validate": lambda v: v.isdigit() and len(v) > 5,
        "test":     None,
    },
    {
        "key":      "IG_ACCESS_TOKEN",
        "label":    "Meta Long-Lived Access Token",
        "hint":     "developers.facebook.com  →  Tools → Graph API Explorer\n"
                    "         Generate User Token → exchange for Long-Lived token (60 days)",
        "validate": lambda v: len(v) > 20,
        "test":     _test_instagram,
    },
    {
        "key":      "IMGBB_API_KEY",
        "label":    "ImgBB API Key",
        "hint":     "https://api.imgbb.com  →  Get API key  (free tier available)",
        "validate": lambda v: len(v) > 10,
        "test":     None,
    },
]


# ── Main wizard ───────────────────────────────────────────

def run_wizard():
    print(BANNER)
    print("This wizard creates (or updates) your " + bold(".env") + " file.\n")
    print(dim("  Press Ctrl+C at any time to quit without saving.\n"))

    existing  = load_env()
    collected = dict(existing)

    # ── Step 0: Install dependencies ──────────────────────
    section("Step 0 — Install Python dependencies")
    if confirm("Run  pip install -r requirements.txt  now?"):
        print()
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=False,
        )
        status(result.returncode == 0,
               "Dependencies installed." if result.returncode == 0
               else "pip install failed — run it manually before using the bot.")

    # ── Steps 1–4: API keys ───────────────────────────────
    for i, step in enumerate(STEPS, start=1):
        key   = step["key"]
        curr  = existing.get(key, "")
        is_placeholder = not curr or curr in PLACEHOLDERS

        section(f"Step {i} — {step['label']}")
        print(f"  {dim('Where to get it:')} {step['hint']}\n")

        while True:
            if curr and not is_placeholder:
                if confirm(f"Keep existing value ({curr[:8]}…)?"):
                    value = curr
                    break
                curr = ""

            secret = "TOKEN" in key or "KEY" in key
            value = ask(step["label"], secret=secret)
            if not value:
                print(f"  {yellow('⚠')}  Value cannot be empty.\n")
                continue
            if not step["validate"](value):
                print(f"  {yellow('⚠')}  Value looks invalid — check and try again.\n")
                continue
            break

        collected[key] = value

        if step["test"] and confirm("Test this credential now?", default=True):
            ok, msg = step["test"](value)
            status(ok, msg)

    # ── Step 5: Rediffmail email notifications ─────────────
    section("Step 5 — Email notifications via Rediffmail  (optional)")
    print(f"  {dim('Get notified by email each time a post goes live.')}\n")

    if confirm("Set up Rediffmail email notifications?", default=False):
        # Sender
        curr = existing.get("EMAIL_FROM", "")
        while True:
            if curr and "@rediffmail.com" in curr:
                if confirm(f"Keep existing sender ({curr})?"):
                    collected["EMAIL_FROM"] = curr
                    break
                curr = ""
            v = ask("Your Rediffmail address (sender)")
            if "@" not in v:
                print(f"  {yellow('⚠')}  Enter a valid email address.\n")
                continue
            collected["EMAIL_FROM"] = v
            break

        # Password
        collected["EMAIL_PASSWORD"] = ask("Rediffmail password", secret=True)

        # Recipient
        curr_to = existing.get("EMAIL_TO", collected["EMAIL_FROM"])
        v = ask("Send notifications to", current=curr_to)
        collected["EMAIL_TO"] = v or curr_to

        # SMTP settings (pre-filled for Rediffmail)
        collected.setdefault("SMTP_HOST", "smtp.rediffmail.com")
        collected.setdefault("SMTP_PORT", "465")

        if confirm("Test Rediffmail login now?", default=True):
            ok, msg = _test_rediffmail(collected)
            status(ok, msg)
    else:
        # Keep any existing email values; set empty defaults if missing
        collected.setdefault("EMAIL_FROM", "")
        collected.setdefault("EMAIL_PASSWORD", "")
        collected.setdefault("EMAIL_TO", "")
        collected.setdefault("SMTP_HOST", "smtp.rediffmail.com")
        collected.setdefault("SMTP_PORT", "465")

    # ── Write .env ────────────────────────────────────────
    section("Saving configuration")
    write_env(collected)
    status(True, ".env written successfully.")

    # ── Summary ───────────────────────────────────────────
    print(f"\n{bold('All done!')}  Start using your bot:\n")
    print(f"  {green('python generate_and_post.py --list')}   # preview the content queue")
    print(f"  {green('python generate_and_post.py')}          # auto-post the next episode")
    print()


if __name__ == "__main__":
    run_wizard()
