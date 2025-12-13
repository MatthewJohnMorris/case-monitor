# Case Monitor

My OCD was nagging me over tracking developments in a court case, so I wrote something to periodically check for new case law documents, and email me the current status!

This is a Python script to monitor new case law documents from the [UK National Archives Find Case Law](https://caselaw.nationalarchives.gov.uk/) service - it's based on pointing ChatGPT at the interface spec that can be downloaded from https://nationalarchives.github.io/ds-find-caselaw-docs/public. The script fetches the latest judgments matching a specified search query and sends email notifications with updates.

Run it with the desired frequency via the Windows Task Scheduler, once a day or whatever.

---

## Features

* Fetches case law from the National Archives Atom feed.
* Sends email notifications via Gmail when new cases are found or if no new cases exist.
* Plays a system alert sound when new cases are detected.
* Shows a temporary desktop notification every time the script runs.
* Keeps track of known cases to detect new entries.
* **Command-line configurable search query**.

---

## Requirements

* Python 3.10+
* Packages:

  ```bash
  pip install requests plyer
  ```
* Gmail account credentials stored securely using [Windows Credential Manager](https://docs.python.org/3/library/keyring.html#using-keyring) via `keyring`.
* Also storing email addressed in the same place, although that's just so they aren't public in this script in Github.

---

## Setup

1. **Store your target email address, Gmail email address and App Password in Windows Credential Manager**:

   ```
   # The email you want to receive updates on
   venv\Scripts\python.exe -c "import keyring; keyring.set_password('case-monitor','email-address','<YOUR_EMAIL_ADDRESS>')"
   # The gmail relay - how you are sending email
   venv\Scripts\python.exe -c "import keyring; keyring.set_password('case-monitor','gmail-address','<YOUR_GMAIL_ADDRESS>')"
   venv\Scripts\python.exe -c "import keyring; keyring.set_password('case-monitor','gmail-password','<YOUR_GMAIL_PASSWORD>')"
   ```

   > Use a Gmail App Password, not your regular password, since basic authentication is disabled.

2. **Install dependencies**:

   ```bash
   pip install requests plyer
   ```

3. **Run the script** with a search query:

   ```bash
   python check_new_hearings_email.py "financial records"
   ```

   * Replace `"financial records"` with your own search query.
   * This argument is **required**.

---

## Files

* `check_new_hearings_email.py` – main script.
* `known_cases.json` – stores previously seen cases.
* `new_cases_log.txt` – logs new cases detected over time.

---

## Notifications

* Temporary desktop notification on every run.
* System alert sound for new cases.
* Emails sent to a configured address with either:

  * **New cases detected**, or
  * **No new cases** if nothing changed.

---

## Customization

* **Email recipient**:

  ```python
  EMAIL_TO = "recipient_email@example.com"
  ```
* **SMTP server/port** (Gmail defaults):

  ```python
  SMTP_SERVER = "smtp.gmail.com"
  SMTP_PORT = 587
  ```

---

## Notes

* Atom feed requests are limited to **1,000 per 5 minutes** per IP address.
* Avoid bulk or computational analysis without contacting [caselaw@nationalarchives.gov.uk](mailto:caselaw@nationalarchives.gov.uk).
* Temporary desktop notifications disappear after 5 seconds.

---

## License

Data reused under the [Open Justice Licence](https://caselaw.nationalarchives.gov.uk/open-justice-licence).






