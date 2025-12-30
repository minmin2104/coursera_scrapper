import requests
from bs4 import BeautifulSoup
import json

COURSE_SITEMAP_URL = "https://www.coursera.org/sitemap~www~courses.xml"


if __name__ == "__main__":
    res = requests.get(COURSE_SITEMAP_URL)
    content = res.content.decode("utf-8")
    soup = BeautifulSoup(content, "xml")
    locs = soup.find_all("loc")
    urls = []
    for loc in locs:
        urls.append(loc.get_text())
    with open("courses_link.json", "w") as f:
        json.dump(list(set(urls)), f, indent=4)
