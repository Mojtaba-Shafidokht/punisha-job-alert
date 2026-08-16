import json

FILE_NAME = "projects.json"


def load_data():
    try:
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return json.load(f)

    except Exception as e:
        print(f"Error occurred: {e}")
        return False


def save_data(data):
    try:
        with open(FILE_NAME, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True

    except Exception as e:
        print(f"Error occurred: {e}")
        return False


def find_new_projects(scraped_projects, existing_projects):
    new_ids = set(scraped_projects) - set(existing_projects)
    return {pid: scraped_projects[pid] for pid in new_ids}
