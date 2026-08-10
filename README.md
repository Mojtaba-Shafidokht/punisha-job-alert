# 🔔 Ponisha Job Alert

A Python-based scraper that monitors [Ponisha](https://ponisha.ir) (an Iranian freelancing platform) for new projects matching your skills, using Selenium.

---

## 🚀 Features

* 🔍 Scrapes project listings filtered by your registered skills on Ponisha
* 📄 Automatic pagination — collects all matching projects, not just the first page
* 🧹 Extracts title, description, required skills, deadline, bid count, and budget for each project
* 🛡️ Handles Ponisha's mobile/desktop duplicate DOM rendering (MUI) correctly
* 🧱 Modular and scalable project structure

---

## 🛠️ Technologies Used

* Python 3
* Selenium (web scraping and browser automation)

---

## 📂 Project Structure

```
punisha-job-alert/
│
├── main.py # Entry point of the application
├── scraper.py # Selenium logic: login, filtering, pagination, project extraction
├── utils.py # Helper functions for data extraction
├── requirements.txt # Project dependencies
├── README.md # Project documentation
```

---

## ⚙️ Installation

1. Clone the repository:

```bash
git clone https://github.com/Mojtaba-Shafidokht/punisha-job-alert.git
cd punisha-job-alert
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
punisha-job-alert/
├── chromedriver.exe
```

---

## 🔐 Login

Since Ponisha requires an authenticated session to filter projects by your skills, the app uses a persistent Chrome profile (`chrome_profile/`) via Selenium's `user-data-dir`. On first run, a browser window opens for manual login; your session is then reused on future runs without logging in again.

---

## ▶️ Usage

Run the program:

```bash
python main.py
```

---

## 🧠 How It Works

1. The scraper launches Chrome with a persistent user profile for session reuse
2. It checks whether the user is already logged in, and waits for manual login if not
3. It filters projects by the user's registered skills
4. It reads the total number of matching projects and calculates the number of pages
5. It iterates through all pages, extracting title, description, skills, deadline, bid count, and budget for each project
6. Duplicate DOM entries (Ponisha's mobile/desktop MUI rendering) are filtered using `is_displayed()`

---

## ⚠️ Notes

* This project is for educational purposes
* Ponisha's page structure may change over time, which can break the scraper's selectors
* Requires a valid, logged-in Ponisha account

---

## 🔮 Future Improvements

* Store scraped projects locally (e.g. JSON) with a stable unique ID to avoid duplicate entries across runs
* Telegram notifications for new matching projects
* Scheduling — run periodically instead of manually
* Reduce field extraction repetition with shared helper functions

---

## 👨‍💻 Author

Mojtaba Shafidokht

---

## ⭐️ Show Your Support

If you found this project useful, consider giving it a star ⭐ on GitHub!