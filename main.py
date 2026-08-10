from scraper import scrape


def main():
    scraped_data = scrape()
    print("-" * 20)
    for dic in scraped_data:
        for k, v in dic.items():
            print(f"{k.capitalize()}: {v}")
        print("-" * 20)


if __name__ == "__main__":
    main()
