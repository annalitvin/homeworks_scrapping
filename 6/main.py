import hashlib
import os.path

import requests
import json

from urllib.parse import urljoin

from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/126.0.0.0 Safari/537.36"
]
BBC_NEWS_URL = "https://www.bbc.com/sport"
BBC_NEWS_DOMEN = "https://www.bbc.com"


def save_to_json(data, file_name: str):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)


def get_content(url: str, from_site: bool = False):

    content_filename = hashlib.md5(url.encode("utf-8")).hexdigest()

    if os.path.exists(content_filename) and not from_site:
        with open(content_filename, "r", encoding="utf-8") as file:
            content = file.read()
        return content

    headers = {"User-Agent": USER_AGENTS[0]}
    response = requests.get(url, headers=headers)

    with open(content_filename, "w", encoding="utf-8") as file:
        file.write(response.text)
    return response.text


def get_news(num_article: int = 5):
    content = get_content(BBC_NEWS_URL)

    soup = BeautifulSoup(content, "lxml")

    article_data = []

    articles = soup.find_all("div", {"data-testid": "promo", "type": "article"})
    article_count = 0
    for article in articles:
        article_count += 1
        url_element = article.find("a")
        if url_element.parent.has_attr("spacing"):
            url = urljoin(BBC_NEWS_DOMEN, article.find("a").get("href"))
            related_topics = get_related_topics(url)
            article_data.append(dict(Link=url, Topics=related_topics))
        if article_count == num_article:
            break
    return article_data


def get_related_topics(article_url):
    content = get_content(article_url)

    soup = BeautifulSoup(content, "lxml")
    topic_list_block = soup.find("div", {"data-component": "topic-list"})
    if topic_list_block:
        topic_lists = (
            topic_list_block.find("div", string="Related Topics")
            .find_next_sibling("div")
            .find("ul")
            .find_all("li")
        )
        topic_lists = [item.text for item in topic_lists]
        return topic_lists


if __name__ == "__main__":
    news = get_news()
    save_to_json(news, "news.json")
