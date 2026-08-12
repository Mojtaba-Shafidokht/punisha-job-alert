from scraper import scrape
from database import load_data, save_data, find_new_projects


def main():
    existing = load_data()
    scraped = scrape()

    new_projects = find_new_projects(scraped, existing)

    if new_projects:
        pass

    merged = {**existing, **scraped}
    save_data(merged)

    print("-" * 50)
    for project in merged:
        for k, v in merged[project].items():
            print(f"{k.capitalize()}: {v}")
        print("-" * 50)


if __name__ == "__main__":
    main()
