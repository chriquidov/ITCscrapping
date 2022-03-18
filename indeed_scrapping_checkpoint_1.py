import grequests
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



def require_number_of_scraps():
    """Request from the user a valid number of job offer to scrap"""
    number_of_scraps = -1
    while (type(number_of_scraps) != int) or number_of_scraps < 1:
        number_of_scraps = int(input('Please enter the minimum number of job offer you want to scrap: \n'))
    return number_of_scraps


def extract(number_of_scraps_conv, job_title_url_format='', location_url_format=''):
    """
    Extract html contents from all the pages
    :param location_url_format: string
    :param job_title_url_format: string
    :param number_of_scraps_conv: integer (multiple of 10)
    :return: lists of soup
    """
    url_list = [f'https://www.indeed.com/jobs?q={job_title_url_format}&l={location_url_format}&start={page}' for page in range(0,number_of_scraps_conv,10)]
    rs = (grequests.get(url) for url in url_list)
    requests=grequests.map(rs)
    soups=[BeautifulSoup(response.content, 'html.parser') for response in requests]
    return soups


def transform_job_offers(soup, joblist, comp_link_list):
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
        company_link = get_company_link(item)
        job = {
            'title': title,
            'company': company,
            'rating': rating,
            'location': location,
            'salary': salary,
            'job_type': job_type,
            'summary': summary,
            'link_job': link,
            'company_link': company_link
        }
        joblist.append(job)
        if not company_link in comp_link_list:
            comp_link_list.append(company_link)
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


def get_company_link(item):
    """Given the :item: in the job offer, returns the link of the company offering if exists"""
    try:
        comp_link=item.find('a',class_="turnstileLink companyOverviewLink",href=True).get('href')
        return urljoin(conf.SAMPLE_URL,comp_link)
    except (AttributeError) as e:
        return None


def extract_companies_soup(comp_urls):
    """
    Takes the list of url of the companies previously scrapped returns list of the soups
    :param comp_urls: list of the url of the indeed page of the companies
    :return: list of soups of these pages
    """
    rs = (grequests.get(url) for url in comp_urls)
    requests = grequests.map(rs)
    soups = []
    for response in requests:
        try:
            soups.append(BeautifulSoup(response.content, 'html.parser'))
        except AttributeError as e:
            pass
    return soups


def get_comp_stat(soup):
    """
    Takes soup returns the stats
    :param soup: soup of a company's indeed page
    :return: Dict of Found numbers of reviews, salaries etc. on the comapny
    """
    comp={}
    comp['name']=soup.title.text
    li_conts=soup.find_all('li', class_="css-tz4lm4 eu4oa1w0")
    for i in li_conts:
        try:
            comp[i['data-tn-element']]=i.find('div',class_="css-r228jg eu4oa1w0").text
        except Exception as e:
            pass
    return comp


def get_comp_hapiness(soup):
    """
    Takes available information about the company's Hapiness degrees
    :param soup:
    :return: dictionnary of the found elements
    """
    comp_hapiness = {}
    comp_hapiness['name']=soup.title.text
    hp_case=soup.find_all('div', class_="css-pnxt15 eu4oa1w0")
    for i in hp_case:
        comp_hapiness[i.find('div', class_="css-19akx1r e1wnkr790").text]=i.find('div', class_="css-zlzlxd eu4oa1w0").text
    return comp_hapiness


def get_about_comp(soup):
    """
    Takes soup of comapny's page returns available information on overview section of webpagw
    :param soup:
    :return: dictionnary of found parameters
    """
    about_comp = {}
    # Company name
    about_comp['name'] = soup.title.text
    # Find about table
    try:
        about = soup.find('ul', class_="css-1vd66n9 e37uo190")
        # add CEO name and approval rate
        about_comp[about.find('span', class_="css-3j50sk e1wnkr790").text] = about.find('span',
                                                                                        class_="css-1w0iwyp e1wnkr790").text
        about_comp['Approved'] = about.find('span', class_="css-4oitjw e1wnkr790").text
        # add other elements
        for i in about.find_all('li', class_="css-ion97 e37uo190"):
            if i.find('div', class_="css-18pwhsj e1wnkr790").text != 'Link':
                about_comp[i.find('div', class_="css-18pwhsj e1wnkr790").text] = i.find('div',
                                                                                        class_="css-1w0iwyp e1wnkr790").text
            else:
                link = i.find('div', class_="css-1w0iwyp e1wnkr790")
                about_comp[i.find('div', class_="css-18pwhsj e1wnkr790").text] = link.find(href=True).get('href')
    except (AttributeError) as e:
        pass
    return about_comp


def transform_comp_soups(soup_companies):
    """
    Takes the soup of all companies pages on indeed and scrapps info
    :param soup_companies:
    :return: 3 dictionnaries: Stats on company reviews..., Hapiness stats, Overview of comapny
    """
    print('Extracting data from comapanies soups')
    all_companies_stats= []
    companies_hapiness=[]
    about_companies=[]
    for soup in tqdm(soup_companies):
        all_companies_stats.append(get_comp_stat(soup))
        companies_hapiness.append(get_comp_hapiness(soup))
        about_companies.append(get_about_comp(soup))
    return all_companies_stats,companies_hapiness,about_companies

def main():
    # Convert Input to URL type
    job_title_url_format = urllib.parse.quote(conf.JOB_TITLE, safe='')
    location_url_format = urllib.parse.quote(conf.LOCATION, safe='')
    number_of_scrap_conv = (require_number_of_scraps() // 15 + 1) * 10

    print("Scrapping in progress...\n Number of pages being scrapped")
    comp_link_list, joblist = [], []
    soup_list_jobs = extract(number_of_scrap_conv, job_title_url_format, location_url_format)
    for soup in tqdm(soup_list_jobs):
        transform_job_offers(soup, joblist, comp_link_list)

    soup_companies = extract_companies_soup(comp_link_list)
    comp_stats, comp_hapiness, comp_overview=transform_comp_soups(soup_companies)

    timestr = time.strftime("%y%m%d_%H%M")

    jobs_df = pd.DataFrame(joblist)
    print('Here are a few exemple of the scrapped data\n', jobs_df.head())
    jobs_df.to_csv(conf.JOBS_FILENAME + timestr + ".csv", encoding='utf-8')
    print(f"Scrapping completed successfully: {jobs_df.shape[0]} jobs imported ")

    comp_df = pd.DataFrame(joblist)
    print('Here are a few exemple of the scrapped data\n', jobs_df.head())
    jobs_df.to_csv(conf.JOBS_FILENAME + timestr + ".csv", encoding='utf-8')
    print(f"Scrapping completed successfully: {jobs_df.shape[0]} jobs imported ")

if __name__ == '__main__':
    main()
