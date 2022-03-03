import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
from urllib.parse import urljoin
import re
from tqdm import tqdm
import time
import conf

"""
Web Scraping for Indeed.com; Returns  jobs and their meta-data
"""

# SAMPLE_URL = f'https://www.indeed.com/'
# FILENAME = 'jobs-'
# JOB_TITLE = 'data scientist'
# LOCATION = 'United States'
# HEADERS = {
#     'User-Agent': 'Windows 10/ Edge browser: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
# }


def require_number_of_scraps():
    """Request from the user a valid number of job offer to scrap"""
    number_of_scraps = -1
    while (type(number_of_scraps) != int) or number_of_scraps < 1:
        number_of_scraps = int(input('Please enter the minimum number of job offer you want to scrap: \n'))
    return number_of_scraps


def extract(page=0, job_title_url_format='', location_url_format=''):
    """
    Extract html content from page number "page"
    :param location_url_format: string
    :param job_title_url_format: string
    :param page: integer (multiple of 10)
    :return: soup object
    """
    url = f'https://www.indeed.com/jobs?q={job_title_url_format}&l={location_url_format}&start={page}'
    r = requests.get(url, conf.HEADERS)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup


def transform(soup, joblist):
    """
    Extract html content from page number "page"
    :param joblist: list
    :param soup: soup object
    :return: soup object
    """
    link_list = get_link_to_full_description(soup)
    divs1 = soup.find_all('div', class_='job_seen_beacon')
    for i, item in enumerate(divs1):
        title = get_job_title(item)
        company = get_company_name(item)
        location = get_job_location(item)
        summary = get_job_summary(item)
        rating = get_company_rating(item)
        salary = get_job_salary(item)
        job_type = get_job_type(item)
        link = link_list[i]
        job = {
            'title': title,
            'company': company,
            'rating': rating,
            'location': location,
            'salary': salary,
            'job_type': job_type,
            'summary': summary,
            'link': link
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
        coeff = 1
        salary = item.find('div', class_='metadata salary-snippet-container').text.strip()
        res = int(re.search(r'(\d+,?\d*)', salary).group(0).replace(",", ""))
        if "year" in salary: coeff = 1
        if "month" in salary: coeff = 12
        if "hour" in salary: coeff = 12 * 176
        salary = coeff * res
        return salary
    except:
        return 'Nan'


def get_job_type(item):
    """Param: item in page's soup
         returns the job type of the specific job offer if exists"""
    try:
        return item.find(lambda tag: tag.name == 'div' and tag.get('class') == ["metadata"]).text.strip()
    except:
        return 'Nan'


def get_link_to_full_description(soup):
    """Param: receives the soup of the page, returns a list of the links to the job offers full description """
    job_column = soup.find('div', class_='mosaic-provider-jobcards')  # gets the column of the job offers
    link_list = []
    for i in job_column.find_all('a'):
        try:
            if i.attrs['id']:
                abs_path = urljoin(conf.SAMPLE_URL, i.get('href'))
                link_list.append(abs_path)
        except:
            pass
    return link_list


def main():
    # Convert Input to URL type
    job_title_url_format = urllib.parse.quote(conf.JOB_TITLE, safe='')
    location_url_format = urllib.parse.quote(conf.LOCATION, safe='')
    number_of_scrap_conv = (require_number_of_scraps() // 15 + 1) * 10

    print("Scrapping in progress...\n Number of pages being scrapped")
    joblist = []
    for i in tqdm(range(0, number_of_scrap_conv, 10)):
        c = extract(i, job_title_url_format, location_url_format)
        transform(c, joblist)

    timestr = time.strftime("%y%m%d_%H%M")
    target_path = conf.FILENAME + timestr + ".csv"

    df = pd.DataFrame(joblist)
    print('Here are a few exemple of the scrapped data\n', df.head())
    df.to_csv(target_path, encoding='utf-8')
    print(f"Scrapping completed successfully: {df.shape[0]} jobs imported to {target_path}")


if __name__ == '__main__':
    main()
