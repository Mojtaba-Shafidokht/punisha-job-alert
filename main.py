import argparse
from notifier import send_notification
from scraper import scrape, login_only
from database import load_data, save_data, find_new_projects


def run_scrape_cycle():
    print("Running cycle...")
    existing = load_data()
    scraped = scrape(headless=True)
    if scraped == "LoginRequiredError":
        print("Session expired - run with --login to sign in again.")
        return None

    if not scraped:
        print("Scraping failed - check logs above.")
        return None

    new_projects = find_new_projects(scraped, existing)

    if new_projects:
        send_notification(new_projects)

    merged = {**existing, **scraped}
    save_data(merged)
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
        run_scrape_cycle()

    return True


if __name__ == "__main__":
    main()
