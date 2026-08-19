# 🔔 Ponisha Job Alert

A Python-based scraper that monitors [Ponisha](https://ponisha.ir) (an Iranian freelancing platform) for new projects matching your skills, using Selenium — and sends you a Telegram notification the moment a new one shows up.

---

## 🚀 Features

* 🔍 Scrapes project listings filtered by your registered skills on Ponisha
* 📄 Automatic pagination — collects all matching projects, not just the first page
* 🧹 Extracts title, description, required skills, deadline, bid count, and budget for each project
* 🛡️ Handles Ponisha's mobile/desktop duplicate DOM rendering (MUI) correctly
* 💾 Persists scraped projects locally (`projects.json`) keyed by a stable project ID, so re-runs never miss or duplicate a listing
* 🆕 Diffs each scrape against stored data and only notifies about **new** projects, not ones you've already seen
* 📬 Telegram notifications with correct right-to-left (RTL) rendering — Persian labels and isolated Latin/number runs so nothing gets visually scrambled
* 🔐 Persistent login session via a dedicated Chrome profile (`chrome_profile/`) — log in once, reuse the session on every future run
* ⚠️ Detects an expired session automatically and sends a dedicated Telegram alert, with a cooldown so you're not spammed on every scheduled run
* ⏰ Built-in scheduler (`scheduler.py`) for continuous, unattended scraping at a fixed interval
* 🧼 Self-healing Chrome profile handling — clears stale `SingletonLock` files left behind by crashes or force-closes, and guarantees `driver.quit()` runs on success, failure, or `Ctrl+C`
* 🖥️ `--show-browser` flag to run with a visible browser window for debugging, and `--login` to (re)authenticate manually
* 🧱 Modular and scalable project structure

---

## 🛠️ Technologies Used

* Python 3
* Selenium (web scraping and browser automation)
* `schedule` (periodic execution)
* `requests` + `python-dotenv` (Telegram notifications, config)
* JSON (local storage for scraped projects and session state)

---

## 📂 Project Structure

```
ponisha-job-alert/
│
├── main.py             # Entry point — single scrape cycle, --login and --show-browser flags
├── scraper.py           # Selenium logic: login, filtering, pagination, project extraction
├── database.py          # Local JSON storage (projects.json) and new-project diffing
├── notifier.py           # Telegram notifications (RTL-safe project alerts + session-expiry alert)
├── state.py               # Session-expiry notification cooldown tracking (state.json)
├── scheduler.py           # Runs main.py's scrape cycle on a repeating interval
├── utils.py                # Helper functions for data extraction
├── requirements.txt        # Project dependencies
├── .env.example             # Template for environment variables
├── README.md                 # Project documentation
```

---

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/Mojtaba-Shafidokht/ponisha-job-alert.git
cd ponisha-job-alert
```

2. Create and activate virtual environment:

**Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🧾 Configuration

1. Rename `.env.example` to `.env`:

**Windows:**
```powershell
Rename-Item .env.example .env
```

**Linux / macOS:**
```bash
mv .env.example .env
```

2. Create a bot via `@BotFather` on Telegram and get your token, then send it a message and get your Chat ID via `https://api.telegram.org/bot<YOUR_TOKEN_HERE>/getUpdates`.

3. Open `.env` and fill in your credentials:

```
TELEGRAM_TOKEN=your_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
TELEGRAM_PROXY=
```

> ⚠️ **Note:** `TELEGRAM_PROXY` is only needed if `api.telegram.org` is blocked in your region (e.g. Iran). Point it at a local proxy such as V2Ray/Xray (e.g. `http://127.0.0.1:10808`) so only the Telegram request is tunneled, while scraping Ponisha stays direct and fast. Leave it empty otherwise.

---

## ⚠️ ChromeDriver Requirement

This project uses Selenium to automate browser interactions.
To run the project successfully, you need a compatible version of **Google Chrome** and **ChromeDriver** installed.

1. Check your Chrome version:

```
chrome://version
```

2. Download the matching ChromeDriver:
   https://googlechromelabs.github.io/chrome-for-testing/

3. Place `chromedriver.exe` in the project directory:

```
ponisha-job-alert/
├── chromedriver.exe
```

### ❗ Important Notes

* ChromeDriver version **must match** your installed Chrome version — a mismatch (e.g. Chrome auto-updating past your driver) will throw a version error
* If ChromeDriver can't be launched from the local path, the app falls back to letting Selenium resolve it automatically
* This project currently supports **Google Chrome only**

---

## 🔐 Login

Since Ponisha requires an authenticated session to filter projects by your skills, the app uses a persistent Chrome profile (`chrome_profile/`) via Selenium's `user-data-dir`. On first run, a browser window opens for manual login; your session is then reused on future runs without logging in again.

If your session ever expires (Ponisha logs you out), the scraper detects this automatically:

* **In `--show-browser` mode:** it reopens the login page and waits up to 180 seconds for you to log in manually
* **In default headless mode:** it can't show you a login screen, so it stops the current run and sends a Telegram alert telling you to run `python main.py --login`

Session-expiry alerts are rate-limited by a cooldown (6 hours by default, tracked in `state.json`) so a headless scheduler running hourly won't spam you every cycle while you're offline.

---

## ▶️ Usage

### One-time scrape

```bash
python main.py
```

Runs a single scrape cycle: logs in (if needed), collects all matching projects, saves anything new to `projects.json`, and sends a Telegram notification for each new project found. Runs headless by default.

### Manual (re-)login

```bash
python main.py --login
```

Opens a visible browser window so you can log in (or re-log-in after a session expires), then exits. Run this once before your first scheduled run, and again any time you get a session-expiry alert.

### Debugging with a visible browser

```bash
python main.py --show-browser
```

Runs a normal scrape cycle with the Chrome window visible instead of headless — useful for spotting selector issues if Ponisha changes its page structure.

### Continuous / unattended scraping

```bash
python scheduler.py
```

`main.py` only performs a **single** scrape-and-notify cycle — it's meant for manual runs or a one-off check. To have the scraper check for new projects **repeatedly and automatically** (e.g. every hour), run `scheduler.py` instead. It runs an immediate scrape on startup, then repeats on a fixed interval using the `schedule` library, and keeps running until you stop it.

> ⚠️ **This requires your computer to stay powered on and connected to the internet the whole time** — closing your laptop or shutting down will stop the scheduler. If you want the scraper running 24/7 without keeping your own machine on, see **Running 24/7 on a VPS** below.

---

## ☁️ Running 24/7 on a VPS

Since `scheduler.py` only keeps running while the machine it's on is powered on and online, the practical way to get true non-stop monitoring is to run it on a small cloud VPS (a Linux server that stays online continuously) instead of your personal computer. General outline:

1. Provision a small Linux VPS (any provider works, since only outbound HTTP(S) is needed)
2. Install Google Chrome (headless-capable) and a matching ChromeDriver on the server
3. Clone the repo, install dependencies, and set up your `.env` and `chrome_profile/` (you'll need to complete the initial `--login` step once — either via a remote desktop/VNC session or by copying a pre-authenticated `chrome_profile/` folder from your local machine)
4. Run `scheduler.py` persistently in the background (e.g. with `tmux`/`screen`, a `systemd` service, or a process manager like `pm2`) so it survives SSH disconnects and server reboots

This is currently a manual setup rather than something automated by this repo — deployment scripts or a Dockerfile could be a good future addition.

---

## 🧠 How It Works

1. The scraper launches Chrome with a persistent user profile for session reuse, clearing any stale lock file left over from an unclean previous exit
2. It checks whether the user is already logged in; if not, it either prompts for manual login (visible mode) or reports `LoginRequiredError` (headless mode)
3. It filters projects by the user's registered skills and reads the total matching-project count to calculate the number of pages
4. It iterates through all pages, extracting title, description, skills, deadline, bid count, and budget for each project — filtering out Ponisha's duplicate mobile/desktop MUI DOM entries with `is_displayed()`
5. The freshly scraped projects are diffed against `projects.json` to find only the genuinely new ones
6. New projects trigger a Telegram message each (RTL-corrected, with Persian field labels), and the full project set is merged and saved back to `projects.json`
7. If the session had expired, a cooldown-gated login-required alert is sent instead, and the cycle exits without touching stored data
8. `driver.quit()` is guaranteed to run in a `finally` block regardless of success, failure, or keyboard interrupt

---

## 📬 Telegram Notifications

Each new project is sent as its own message, formatted with Persian field labels (عنوان پروژه, توضیحات پروژه, مهارت‌های مورد نیاز, زمان پیشنهاد, تعداد پیشنهادها, بودجه‌ی کارفرما, آدرس پروژه) and Unicode isolation markers around any embedded Latin text or numbers, so mixed Persian/English lines always render in the correct reading direction — no more scrambled words or reversed number ranges.

If your session expires, you'll instead receive a short alert telling you to run `python main.py --login`, at most once per cooldown window.

---

## 💾 Data Storage

Scraped projects are stored in `projects.json`, keyed by the stable numeric project ID extracted from each project's URL (not the title, which can vary), so re-scraping never creates duplicates:

```json
{
    "12345": {
        "title": "...",
        "description": "...",
        "skills": ["Python", "Selenium"],
        "deadline": "...",
        "bids": "...",
        "budget": "...",
        "url": "https://ponisha.ir/project/12345"
    }
}
```

Session-expiry cooldown tracking lives separately in `state.json`.

`projects.json`, `state.json`, and `chrome_profile/` are all excluded from version control (see `.gitignore`) since they're user-specific and regenerated automatically on first run.

---

## ⚠️ Notes

* This project is for educational purposes
* Ponisha's page structure may change over time, which can break the scraper's selectors — some field extractions (e.g. bid count) rely on positional/text-based fallbacks since no stable class or aria-label exists for them
* Requires a valid, logged-in Ponisha account
* Headless mode cannot show a login prompt — if your session expires while running headless (e.g. via the scheduler), you'll need to run `python main.py --login` manually to restore it
* If the program is force-closed (not via `Ctrl+C`) while Chrome is running, the profile lock is cleaned up automatically on the *next* run, not instantly

---

## 🔮 Future Improvements

* Deployment scripts / Dockerfile for one-command VPS setup
* A lightweight way to complete the initial `--login` step remotely on a headless VPS (e.g. via VNC or by syncing an authenticated `chrome_profile/`)
* Configurable skill/keyword filters and scrape interval via `.env` instead of hardcoded values
* Retry/backoff logic for transient network failures instead of failing the whole cycle
* Optional daily digest mode (one summary message) as an alternative to per-project notifications
* Basic test coverage for the data-cleaning and RTL-formatting utility functions
* Reduce field extraction repetition in `scraper.py` with shared helper functions

---

## 👨‍💻 Author

Mojtaba Shafidokht

---

## ⭐️ Show Your Support

If you found this project useful, consider giving it a star ⭐ on GitHub!