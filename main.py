import argparse
from notifier import send_notification, send_login_alert
from scraper import scrape, login_only
from database import load_data, save_data, find_new_projects
from state import should_notify_login_alert, mark_login_alert_sent, reset_login_alert


def run_scrape_cycle(headless=True):
    existing = load_data()
    scraped = scrape(headless)
    if scraped == "LoginRequiredError":
        if should_notify_login_alert():
            send_login_alert()
            print("Session expire notification was sent.")
            mark_login_alert_sent()

        else:
            print("Session expired — notification skipped (cooldown active).")

        return None

    if not scraped:
        print("Scraping failed - check logs above.")
        return None

    new_projects = find_new_projects(scraped, existing)

    if new_projects:
        send_notification(new_projects)

    merged = {**existing, **scraped}
    save_data(merged)
    reset_login_alert()
    return True


def main():
    parser = argparse.ArgumentParser(description="Ponisha Job Alert Scraper")
    parser.add_argument("--login", action="store_true", help="login manually")
    parser.add_argument("--show-browser", action="store_true", help="show browser")

    args = parser.parse_args()
    headless = not args.show_browser

    if args.login:
        headless = False
        login_only(headless)
        return None

    else:
        run_scrape_cycle(headless)

    return True


if __name__ == "__main__":
    main()
