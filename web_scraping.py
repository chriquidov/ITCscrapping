"""
Web Scraping for Indeed.com; Returns  jobs and their meta-data
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse

TARGET_PATH = 'jobs3.csv'
JOB_TITLE = 'Anything'
LOCATION = 'United States'
NUMBER_OF_SCRAPS = 10


def extract(page=0, job_title_url_format='', location_url_format=''):
    """
    Extract html content from page number "page"
    :param location_url_format: string
    :param job_title_url_format: string
    :param page: integer (multiple of 10)
    :return: soup object
    """
    headers = {
        'User-Agent': 'Windows 10/ Edge browser: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
    }
    url = f'https://www.indeed.com/jobs?q={job_title_url_format}&l={location_url_format}&start={page}'
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def transform(soup, joblist):
    """
    Extract html content from page number "page"
    :param joblist: list
    :param soup: soup object
    :return: soup object
    """
    divs = soup.find_all('div', class_='job_seen_beacon')
    for item in divs:
        title = get_job_title(item)
        company = get_company_name(item)
        location = get_job_location(item)
        summary = get_job_summary(item)
        rating = get_company_rating(item)
        salary = get_job_salary(item)
        job_type = get_job_type(item)

        job = {
            'title': title,
            'company': company,
            'rating': rating,
            'location': location,
            'salary': salary,
            'job_type': job_type,
            'summary': summary,
        }
        joblist.append(job)
    return


def get_job_title(item):
    """Param: item in page's soup
        returns the job title of the specific job offer if exists"""
    try:
        return item.find('h2', class_='jobTitle').text
    except:
        return 'Nan'


def get_company_name(item):
    """Param: item in page's soup
        returns the name of the comapny of the specific job offer if exists"""
    try:
        return item.find('span', class_='companyName').text.strip()
    except:
        return 'Nan'


def get_job_location(item):
    """Param: item in page's soup
            returns the location of the comapny of the specific job offer if exists"""
    try:
        return item.find('div', class_='companyLocation').text.strip()
    except:
        return 'Nan'


def get_job_summary(item):
    """Param: item in page's soup
        returns the summary of the specific job offer if exists"""
    try:
        return item.find('div', {'class': 'job-snippet'}).text.strip()
    except:
        return 'Nan'


def get_company_rating(item):
    """Param: item in page's soup
            returns the summary of the specific job offer if exists"""
    try:
        return item.find('span', class_='ratingNumber').text.strip()
    except:
        return 'Nan'


def get_job_salary(item):
    """Param: item in page's soup
                returns the salary of the specific job offer if exists"""
    try:
        return item.find('div', class_='metadata salary-snippet-container').text.strip()
    except:
        return 'Nan'


def get_job_type(item):
    """Param: item in page's soup
                    returns the job type of the specific job offer if exists"""
    try:
        return item.find('div', class_='metadata').text.strip()
    except:
        return 'Nan'


def get_link_to_full_description(item):
    """Param: item in page's soup
                        returns the job type of the specific job offer if exists"""
    try:
        return item.find('div', class_='metadata').text.strip()
    except:
        return 'Nan'

def main():
    # Convert Input to URL type
    job_title_url_format = urllib.parse.quote(JOB_TITLE, safe='')
    location_url_format = urllib.parse.quote(LOCATION, safe='')
    number_of_scrap_conv = (NUMBER_OF_SCRAPS // 15 + 1) * 10

    joblist = []
    for i in range(0, number_of_scrap_conv, 10):
        c = extract(i, job_title_url_format, location_url_format)
        transform(c, joblist)

    df = pd.DataFrame(joblist)
    print(df.head())
    df.to_csv(TARGET_PATH)
    print(f"Scrapping completed successfully: {df.shape[0]} imported")



if __name__ == '__main__':
    main()
