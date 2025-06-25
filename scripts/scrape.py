import math
import itertools
import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import aiohttp
import asyncio
import async_timeout
import random


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/125.0.0.0 Safari/537.36"
}

LISTINGS_BASE_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={}&location={}&start={}'
JOB_POSTING_BASE_URL = 'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}'

ENTRIES_PER_PAGE = 10
RESULT_CSV_FILE_PATH = "./data/scraped_linkedin_jobs.csv"

# REQUEST CONSTANTS
MAX_CONCURRENT_REQUESTS = 3
REQUEST_TIMEOUT = 200
MAX_RETRIES = 5
BASE_DELAY = 3  # seconds

sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

def extract_job_id_from_listing(job):
    div = job.find("div", {"class": "base-card"})
    if not div:
        return 0
    return div.get('data-entity-urn').split(":")[3]

def extract_info_from_posting(job):
    title = job.find("h2", {"class": "top-card-layout__title"})
    location = job.find("span", {"class": "topcard__flavor--bullet"})
    org_name = job.find("a", {"class": "topcard__org-name-link"})
    description = job.find("div", {"class": "description__text"})

    ret_dict = {
        "title": "",
        "location": "",
        "org_name": "",
        "org_link": "",
        "description": ""
    }

    if title:
        ret_dict["title"] = title.text.strip()
    if location:
        ret_dict["location"] = location.text.replace('\n', '').strip()
    if org_name:
        ret_dict["org_name"] = org_name.text.replace('\n', '').strip()
        ret_dict["org_link"] = org_name.get('href')
    if description:
        ret_dict["description"] = description.text.replace('\n', '').strip()

    return ret_dict

async def fetch_job_posting(session, job_id):
    url = JOB_POSTING_BASE_URL.format(job_id)

    for attempt in range(MAX_RETRIES):
        try:
            async with sem:
                async with async_timeout.timeout(REQUEST_TIMEOUT):
                    async with session.get(url, headers=HEADERS) as res:
                        if res.status == 200:
                            text = await res.text()
                            soup = BeautifulSoup(text, 'html.parser')
                            job_info = extract_info_from_posting(soup)

                            if job_info["title"] != "":
                                job_info["job_posting_link"] = url
                                print(f"{url} - Successfully scraped")
                                return job_info
                            else:
                                print(f"{url} - No content found")
                                return None

                        elif res.status == 429:
                            delay = BASE_DELAY * (2 ** attempt) + random.uniform(0, 1)
                            print(f"{url} - 429 Too Many Requests. Retrying in {delay:.1f}s...")
                            await asyncio.sleep(delay)

                        else:
                            print(f"{url} - Failed with status {res.status}")
                            return None

        except asyncio.TimeoutError:
            print(f"{url} - Timed out (attempt {attempt + 1})")
        except Exception as e:
            print(f"{url} - Exception: {e}")

    print(f"{url} - Failed after {MAX_RETRIES} attempts.")
    return None


async def scrape_all_jobs(job_ids):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_job_posting(session, job_id) for job_id in job_ids]
        results = await asyncio.gather(*tasks)
        return [job for job in results if job]

def main(keywords, locations, no_of_pages):
    result_csv = []
    unique_job_ids = set()
    keyword_location_combinations = itertools.product(keywords, locations)

    for (keyword, location) in keyword_location_combinations:
        print(f"Scraping job listings for {keyword}, {location}")
        for page_no in range(0, no_of_pages * ENTRIES_PER_PAGE, ENTRIES_PER_PAGE):
            url = LISTINGS_BASE_URL.format(keyword, location, page_no)
            try:
                res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
                soup = BeautifulSoup(res.text, 'html.parser')
                job_ids_on_page = [extract_job_id_from_listing(job) for job in soup.find_all("li")]
                unique_job_ids.update(job_ids_on_page)
                print(f"{url} - Found postings: {len(job_ids_on_page)}. Expected {ENTRIES_PER_PAGE}")
            except Exception as e:
                print(f"Failed to fetch listing page: {url} - Exception: {e}")

    unique_job_ids.discard(0)

    print("Scraping individual job postings asynchronously")
    loop = asyncio.get_event_loop()
    result_csv = loop.run_until_complete(scrape_all_jobs(unique_job_ids))

    dataframe = pd.DataFrame(result_csv).replace(pd.NA, "")
    dataframe.to_csv(RESULT_CSV_FILE_PATH, index=False)
    print(f"Successfully saved CSV file to {RESULT_CSV_FILE_PATH}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape LinkedIn job postings.')

    parser.add_argument('--keywords', nargs='+', required=True,
                        help='List of keywords to search for (e.g., --keywords Backend Python)')
    parser.add_argument('--locations', nargs='+', required=True,
                        help='List of locations to search in (e.g., --locations Remote Zagreb)')
    parser.add_argument('--pages', type=int, default=5,
                        help='Number of pages to scrape per keyword-location combination')

    args = parser.parse_args()
    main(args.keywords, args.locations, args.pages)
