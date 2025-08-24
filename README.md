# Naukri Resume Headline Toggler

Automates the daily update of your Naukri resume headline by toggling a trailing period (`.`).
Maintains a persistent Chrome profile for login to avoid entering credentials every time.

---

## Features

* Automatically toggles a trailing `.` in the resume headline:

  * If the headline ends with `.`, it removes it.
  * Otherwise, it appends `.` to the end.
* Uses a **persistent Chrome profile** to maintain login sessions.
* Automatically fills login credentials if provided.
* Handles overlays and pop-ups on the Naukri profile page.
* Fully automated after initial setup.

---

## Requirements

* Python 3.10+
* [Selenium](https://pypi.org/project/selenium/)
* Chrome browser
* ChromeDriver matching your Chrome version

---

## Installation

1. Clone the repository or download the script:

```bash
git clone https://github.com/aadityaraaz/Naukri-profile-updater.git
cd Naukri-profile-updater
```

2. Install dependencies:

```bash
pip install selenium
```

3. Download the correct [ChromeDriver](https://sites.google.com/chromium.org/driver/) and place it in the script folder or add it to your PATH.

---

## Usage

```bash
python naukriProfileUpdate.py --email "your_email@example.com" --password "your_password" 
```

### Options

* `--email`: Your Naukri login email (required if not already logged in via profile).
* `--password`: Your Naukri password (required if not already logged in via profile).
* `--binary`: Optional path to your Chrome binary.

---

### First-time Run

1. If you provide credentials, the script will log in automatically.
2. A persistent Chrome profile folder `naukri_profile` will be created to maintain login.
3. For subsequent runs, you can skip email/password if the profile remains logged in.

---

## Scheduling

You can schedule this script to run daily using **Task Scheduler** on Windows or **cron** on Linux.
Ensure the persistent profile folder (`naukri_profile`) is accessible by the scheduler.

---

## Notes

* OTP or 2FA on Naukri login may block automation; manual intervention will be required in such cases.
* Make sure your ChromeDriver matches your installed Chrome version.
* Avoid changing the profile folder path once set, otherwise the session will be lost.

---

## License
This script is free to use and modify. Use responsibly.
