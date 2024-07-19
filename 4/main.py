import json
import time
import random
import requests
import re

from os import path

PARENT_DIR = path.dirname(path.abspath(__file__))

JOB_CARDS_PAYLOAD_FILENAME = path.join(PARENT_DIR, "job_cards_payload.json")
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/126.0.0.0 Safari/537.36"
]
JOB_SITE_URL = "https://www.lejobadequat.com/emplois"
JOB_TITLE_PATTERN = re.compile(
    (
        '<h3 class="jobCard_title">'
        "([0-9A-Za-zàâçéèêëîïôûùüÿñæœ -�!#$%&'()*+°,./:;<=>?@_`{|}~]*)"
        "</h3>"
    )
)
POSITIONS_NUMBER_PER_PAGE = 12


def get_job_titles(page: int = 1):
    with open(JOB_CARDS_PAYLOAD_FILENAME, "r") as file:
        payload = json.load(file)
        payload["data"]["paged"] = page

    headers = {"User-Agent": USER_AGENTS[0]}
    response = requests.post(JOB_SITE_URL, headers=headers, json=payload)
    content = response.json()["template"]
    job_title_items = re.findall(JOB_TITLE_PATTERN, content)

    if len(job_title_items) != POSITIONS_NUMBER_PER_PAGE:
        raise Exception(
            f"Need 12 records per page. "
            f"Please check the pattern. Page number: {page}"
        )

    return job_title_items


if __name__ == "__main__":
    JOB_TITLES_FILENAME = path.join(PARENT_DIR, "job_titles.json")
    pages = range(1, 3)
    job_titles = []
    for page in pages:
        time.sleep(random.randint(3, 9))
        job_titles.append(dict(page=page, job_titles=get_job_titles(page)))

    with open(JOB_TITLES_FILENAME, "w") as f:
        json.dump(job_titles, f)
