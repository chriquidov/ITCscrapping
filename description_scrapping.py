"""
Web Scraping for Indeed.com; Returns  jobs and their meta-data
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
from urllib.parse import urljoin


TARGET_PATH = 'jobs3.csv'
JOB_TITLE = 'data scientist'
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
    link_list=get_link_to_full_description(soup)
    divs1 = soup.find_all('div', class_='job_seen_beacon')
    for i,item in enumerate(divs1):
        title = get_job_title(item)
        company = get_company_name(item)
        location = get_job_location(item)
        summary = get_job_summary(item)
        rating = get_company_rating(item)
        salary = get_job_salary(item)
        job_type = get_job_type(item)
        link= link_list[i]
        job = {
            'title': title,
            'company': company,
            'rating': rating,
            'location': location,
            'salary': salary,
            'job_type': job_type,
            'summary': summary,
            'link':link
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


def get_link_to_full_description(soup):
    """Param: receives the soup of the page, returns a list of the links to the job offers full description """
    job_column = soup.find('div', class_='mosaic-provider-jobcards') #gets the column of the job offers
    url = f'https://www.indeed.com/' #TODO: Find a way to make one url and put in as magic number!
    link_list=[]
    for i in job_column.find_all('a'): # loop over all the a's in the column
        try:
            if i.attrs['id']: # If id is provided it means the a contains info about a job offer and a relative link to the job offer
                abs_path=urljoin(url, i.get('href')) # Gets the link from the a and creates an absolute path to the job offer detailed description
                link_list.append(abs_path)
        except:
            pass
    return link_list

def main():
    # Convert Input to URL type
    job_title_url_format = urllib.parse.quote(JOB_TITLE, safe='')
    location_url_format = urllib.parse.quote(LOCATION, safe='')
    number_of_scrap_conv = (NUMBER_OF_SCRAPS // 15 +1 ) * 10

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
