import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_URL = f"{BASE_URL}/c/courses/tds-kb/34"

def get_topic_urls():
    topic_urls = []
    for page in range(0, 10):  # adjust the range to get more pages
        url = f"{CATEGORY_URL}.json?page={page}"
        print(f"Fetching: {url}")
        res = requests.get(url)
        if res.status_code != 200:
            break
        data = res.json()
        topics = data.get("topic_list", {}).get("topics", [])
        for topic in topics:
            topic_urls.append(f"{BASE_URL}/t/{topic['slug']}/{topic['id']}")
        time.sleep(1)
    return topic_urls

def get_topic_content(url):
    print(f"Scraping topic: {url}")
    res = requests.get(f"{url}.json")
    if res.status_code != 200:
        return None
    data = res.json()
    posts = data.get("post_stream", {}).get("posts", [])
    return {
        "title": data.get("title", ""),
        "url": url,
        "posts": [post.get("cooked", "") for post in posts]
    }

def scrape_discourse():
    topic_urls = get_topic_urls()
    all_posts = []
    for url in topic_urls:
        content = get_topic_content(url)
        if content:
            all_posts.append(content)
        time.sleep(1)

    with open("discourse.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)
    print("✅ Saved Discourse posts to discourse.json")

if __name__ == "__main__":
    scrape_discourse()
