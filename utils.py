import re


def clean_count(text):
    cleaned_count = int(text.split(" ")[0])

    return cleaned_count


def extract_id(url):
    match = re.search(r'/project/(\d+)', url)
    return match.group(1) if match else None
