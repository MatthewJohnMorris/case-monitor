# Standard library imports
import argparse
import json
import os
import smtplib
import sys
import xml.etree.ElementTree as ET
from datetime import datetime
from email.message import EmailMessage
import winsound

# Third-party imports
import keyring
import requests
from plyer import notification

# ----------------------
# Configuration
# ----------------------

DATA_FILE = "known_cases.json"
LOG_FILE = "new_cases_log.txt"

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL_TO = keyring.get_password("case-monitor", "email-address")
if not EMAIL_TO:
    raise RuntimeError("Target email address not found in Windows Credential Manager")
    
EMAIL_FROM = keyring.get_password("case-monitor", "gmail-address")
if not EMAIL_FROM:
    raise RuntimeError("Gmail email address not found in Windows Credential Manager")

EMAIL_PASSWORD = keyring.get_password("case-monitor", "gmail-password")
if not EMAIL_PASSWORD:
    raise RuntimeError("Gmail email password not found in Windows Credential Manager")

# Atom feed base URL
ATOM_FEED_URL = "https://caselaw.nationalarchives.gov.uk/atom.xml"

# ----------------------
# Email
# ----------------------

def send_email(subject, body):
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)

    print("Email sent:", subject)

# ----------------------
# Fetch cases from Atom feed
# ----------------------

def fetch_cases(search_query):
    params = {"query": search_query, "order": "-date", "per_page": 10}
    response = requests.get(ATOM_FEED_URL, params=params, timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "tna": "https://caselaw.nationalarchives.gov.uk"
    }

    cases = []
    for entry in root.findall("atom:entry", ns):
        title_el = entry.find("atom:title", ns)
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        date_el = entry.find("atom:published", ns)

        if title_el is None or link_el is None:
            continue

        cases.append({
            "title": title_el.text,
            "link": link_el.attrib["href"],
            "date": date_el.text if date_el is not None else "Unknown"
        })

    return cases

# ----------------------
# Storage
# ----------------------

def load_known_cases():
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_known_cases(cases):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, indent=2)

# ----------------------
# Logging
# ----------------------

def log_new_cases(new_cases):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        for case in new_cases:
            f.write(f"{datetime.now()}: {case['date']} - {case['title']} - {case['link']}\n")

# ----------------------
# Notifications
# ----------------------

def show_temporary_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=5  # seconds
    )

# ----------------------
# Alert Sound
# ----------------------

def play_alert_sound():
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

# ----------------------
# Main
# ----------------------

def main():
    parser = argparse.ArgumentParser(description="Monitor new case law documents from the National Archives.")
    parser.add_argument("query", help="Search query to monitor (required)")
    args = parser.parse_args()

    search_query = args.query
    now = datetime.now()
    print(f"[{now}] Checking for new cases with query: '{search_query}'")

    # Show temporary notification every run
    show_temporary_notification(
        "Case Monitor",
        f"Script run at {now.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    known_cases = load_known_cases()
    current_cases = fetch_cases(search_query)

    # First run
    if known_cases is None:
        save_known_cases(current_cases)
        send_email(
            subject="⚖️ Case monitoring started",
            body=(
                "Case monitoring has started successfully.\n\n"
                f"Search query: {search_query}\n"
                f"Cases currently found: {len(current_cases)}\n"
                f"Time: {now}"
            )
        )
        print("First run completed. Email sent.")
        return

    # Compare with known cases
    known_links = {case["link"] for case in known_cases}
    new_cases = [c for c in current_cases if c["link"] not in known_links]

    if new_cases:
        log_new_cases(new_cases)
        play_alert_sound()
        body_lines = [f"{len(new_cases)} new case(s) detected:\n"]
        for case in new_cases:
            body_lines.append(f"{case['date']} - {case['title']}\n{case['link']}\n")
    else:
        body_lines = ["No new cases found.\n"]

    body_lines.append(f"\nChecked at: {now}")
    send_email(
        subject="⚖️ Case Monitor Update",
        body="\n".join(body_lines)
    )

    save_known_cases(current_cases)

if __name__ == "__main__":
    main()
