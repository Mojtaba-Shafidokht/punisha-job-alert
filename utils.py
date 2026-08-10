import re
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


def clean_count(text):
    cleaned_count = int(text.split(" ")[0])

    return cleaned_count


def extract_id(url):
    match = re.search(r'/project/(\d+)', url)
    return match.group(1) if match else None


def build_page_url(base_url, page_num):
    parsed = urlparse(base_url)
    query = parse_qs(parsed.query)
    query["page"] = [str(page_num)]
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))
