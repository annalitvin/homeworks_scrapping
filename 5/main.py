import hashlib
import json
import sqlite3

import requests
import re

from os import path
from collections import namedtuple

PARENT_DIR = path.dirname(path.abspath(__file__))

JOB_CARDS_PAYLOAD_FILENAME = path.join(PARENT_DIR, "job_cards_payload.json")
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
    "Chrome/126.0.0.0 Safari/537.36"
]
JOB_PATTERN = re.compile(
    r"<a href=\"(?P<url>(?:(?:https?|ftp|smtp|mailto):\/\/)?"
    r"(?:www.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}"
    r"\b(?:[-a-zA-Z0-9()@:%_\+~#?&\/=]*))\" title=\"Consulter l'offre d'emploi "
    r"(?P<title>[0-9A-Za-zàâçéèêëîïôûùüÿñæœ -�!#$%&'()*+°,.\/:;<=>?@_`{|}~]*)\" "
    r"class=\"jobCard_link\" style=\"text-align:left;\">"
)
JOB_SITE_URL = "https://www.lejobadequat.com/emplois"
POSITIONS_NUMBER_PER_PAGE = 12

Job = namedtuple("Job", ["title", "url"])


def save_to_json(data, file_name: str):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)


def save_to_sqlite(data, file_name: str):
    conn = sqlite3.connect(file_name)

    create_table_sql = """
        create table if not exists job (
            id integer primary key,
            title text,
            url text
        );
    """

    with conn:
        conn.execute(create_table_sql)
        conn.executemany("INSERT INTO job(title, url) VALUES(?, ?)", data)

    conn.close()


def get_jobs(page: int = 1):

    content = get_content(JOB_SITE_URL, page)
    jobs_records = re.findall(JOB_PATTERN, content)
    if len(jobs_records) != POSITIONS_NUMBER_PER_PAGE:
        raise Exception(
            f"Need 12 records per page. "
            f"Please check the pattern. Page number: {page}"
        )
    return [Job(job[1], job[0]) for job in jobs_records]


def get_content(url: str, page: int = 1, from_site: bool = False):

    content_filename = hashlib.md5(f"{url}-{page}".encode("utf-8")).hexdigest()
    try:
        if from_site:
            raise FileNotFoundError
        with open(content_filename, "r") as file:
            content = file.read()
            return content
    except FileNotFoundError:
        with open(JOB_CARDS_PAYLOAD_FILENAME, "r") as file:
            payload = json.load(file)
            payload["data"]["paged"] = page

        headers = {"User-Agent": USER_AGENTS[0]}
        response = requests.post(JOB_SITE_URL, headers=headers, json=payload)
        content = response.json()["template"]
        with open(content_filename, "w", encoding="utf-8") as file:
            file.write(content)
        return content


if __name__ == "__main__":

    job_items = get_jobs()

    filename_json = "jobs.json"
    jobs = [dict(title=item.title, url=item.url) for item in job_items]
    save_to_json(jobs, filename_json)

    filename_sqlite = "jobs.db"
    jobs = [(item.title, item.url) for item in job_items]
    save_to_sqlite(job_items, filename_sqlite)
