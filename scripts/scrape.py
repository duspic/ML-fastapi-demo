import math
import itertools
import requests
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/125.0.0.0 Safari/537.36"
}

LISTINGS_BASE_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={}&location={}&start={}'
JOB_POSTING_BASE_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'

KEYWORD_LIST = ["Backend", "Python", "Software%20Developer", "AI%20Developer", "ML%20Developer"]
LOCATION_LIST = ["Croatia", "Remote", "Zagreb"]
KEYWORD_LOCATION_COMBINATIONS = itertools.product(KEYWORD_LIST, LOCATION_LIST)

NO_OF_PAGES = 10
ENTRIES_PER_PAGE = 10

RESULT_CSV_FILE_PATH = "./data/scraped_linkedin_jobs.csv"

def extract_job_id_from_listing(job):
    div = job.find("div", {"class":"base-card"})
    if not div:
        return 0
    return div.get('data-entity-urn').split(":")[3]

def extract_info_from_posting(job):
    title = job.find("h2", {"class":"top-card-layout__title"})
    location = job.find("span", {"class":"topcard__flavor--bullet"})
    org_name = job.find("a", {"class":"topcard__org-name-link"})
    description = job.find("div",{"class":"description__text"})

    ret_dict = {
        "title": "",
        "location": "",
        "org_name": "",
        "org_link": "",
        "description": ""
    }

    if title:
        ret_dict["title"] = title.text
    if location:
        ret_dict["location"] = location.text.replace('\n','').strip()
    if org_name:
        ret_dict["org_name"] = org_name.text.replace('\n','').strip()
        ret_dict["org_link"] = org_name.get('href')
    if description:
        ret_dict["description"] = description.text.replace('\n','').strip()

    return ret_dict

def main():
    result_csv = []
    unique_job_ids = set()

    for (keyword, location) in KEYWORD_LOCATION_COMBINATIONS:
        print(f"Scraping job listings for {keyword, location}")
        for page_no in range(0, NO_OF_PAGES * ENTRIES_PER_PAGE, ENTRIES_PER_PAGE):
            url = LISTINGS_BASE_URL.format(keyword, location, page_no)
            res = requests.get(url, headers=HEADERS, timeout=200)
            soup = BeautifulSoup(res.text,'html.parser')

            job_ids_on_page = [extract_job_id_from_listing(job) for job in soup.find_all("li")]
            unique_job_ids.update(job_ids_on_page)
            print(f"{url} - Found postings: {len(job_ids_on_page)}. Expected {ENTRIES_PER_PAGE}")

    unique_job_ids.discard(0)

    print("Scraping individual job postings")
    for job_id in unique_job_ids:
        url = JOB_POSTING_BASE_URL.format(job_id)

        res = requests.get(url, headers=HEADERS, timeout=500)
        soup = BeautifulSoup(res.text, 'html.parser')

        job_info = extract_info_from_posting(soup)
        if job_info["title"] != "":
            job_info["job_posting_link"] = url
            result_csv.append(job_info)
            print(f"{url} - Succesfully scraped posting")
        else:
            print(f"{url} - Something didn't work when scraping this page.")

    dataframe = pd.DataFrame(result_csv).replace(pd.NA, "")
    dataframe.to_csv(RESULT_CSV_FILE_PATH)
    print(f"Succesfully saved CSV file to {RESULT_CSV_FILE_PATH}")
    

if __name__ == '__main__':
    main()