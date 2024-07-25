import json

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

JOB_SEARCH_URL = "https://br.indeed.com/?from=jobsearch-empty-whatwhere"

OPTIONS = Options()
OPTIONS.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/58.0.3029.110 Safari/537.3"
)


def save_to_json(data, file_name: str):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)


def get_jobs():
    driver = webdriver.Chrome(options=OPTIONS)

    max_page = 3

    job_results = []

    driver.get(JOB_SEARCH_URL)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "jobsearch")))
    input_what = driver.find_element(By.ID, "text-input-what")
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: input_what.send_keys("home office") or True)
    input_where = driver.find_element(By.ID, "text-input-where")
    wait = WebDriverWait(driver, 10)
    wait.until(lambda d: input_where.send_keys("Campinas, SP") or True)
    submit_button = driver.find_element(
        By.CLASS_NAME, "yosegi-InlineWhatWhere-primaryButton"
    )
    submit_button.click()
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, "//nav[@aria-label='pagination']")))

    for page in range(1, max_page):
        page_url_xpath = f"//a[@data-testid='pagination-page-{page}']"
        if page == 1:
            page_url_xpath = "//a[@data-testid='pagination-page-current']"

        page_url = driver.find_element(By.XPATH, page_url_xpath).get_attribute("href")
        driver.get(page_url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "jcs-JobTitle")))
        job_elements = driver.find_elements(By.CLASS_NAME, "jcs-JobTitle")
        for job in job_elements:
            title = job.find_element(By.TAG_NAME, "span").text
            url = job.get_attribute("href")
            job_results.append(dict(title=title, url=url))

    driver.quit()

    return job_results


if __name__ == "__main__":
    jobs = get_jobs()
    save_to_json(jobs, "job_results.json")
