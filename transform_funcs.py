import re
from urllib.parse import urljoin
import conf
from tqdm import tqdm
import json

"""Functions that turns the soups in the data we require"""


def isfloat(num):
    """
    Checks if number is floatable
    :param num: string
    :return: Boolean
    """
    try:
        float(num)
        return True
    except (TypeError, ValueError):
        return False


def transform_job_offers(soup, joblist, comp_link_list):
    """
    Extract html content from page number "page"
    :param comp_link_list: list of the dictionnaries of the companies info
    :param joblist: list
    :param soup: soup object
    :appends to the job list and comp_link_dict
    """
    link_list = get_link_to_full_description(soup)
    divs1 = soup.find_all('div', class_='job_seen_beacon')
    for i, item in enumerate(divs1):
        title = get_job_title(item)
        company = get_company_name(item)
        location = get_job_location(item)
        summary = get_job_summary(item)
        if isfloat(get_company_rating(item)):
            rating = float(get_company_rating(item))
        else:
            rating = None

        salary = get_job_salary(item)
        job_type = get_job_type(item)
        link = link_list[i]
        company_link = get_company_link(item)
        job = {
            'title': title,
            'company': company,
            'location': location,
            'salary': salary,
            'job_type': job_type,
            'summary': summary,
            'link_job': link,
            'indeed_company_link': company_link
        }
        joblist.append(job)

        if not any(d['indeed_company_link'] == company_link for d in comp_link_list):
            comp_dict = {
                'name': company,
                'indeed_company_link': company_link,
                'rating': rating
            }
            comp_link_list.append(comp_dict)
    return


def require_number_of_scraps():
    """Request from the user a valid number of job offer to scrap"""
    number_of_scraps = -1
    while (type(number_of_scraps) != int) or number_of_scraps < 1:
        number_of_scraps = int(input('Please enter the minimum number of job offer you want to scrap: \n'))
    return number_of_scraps


def get_job_title(item):
    """Param: item in page's soup
        returns the job title of the specific job offer if exists"""
    try:
        return item.find('h2', class_='jobTitle').text
    except (AttributeError):
        return None


def get_company_name(item):
    """Param: item in page's soup
        returns the name of the comapny of the specific job offer if exists"""
    try:
        return item.find('span', class_='companyName').text.strip()
    except AttributeError:
        return None


def get_job_location(item):
    """Param: item in page's soup
            returns the location of the comapny of the specific job offer if exists"""
    try:
        return item.find('div', class_='companyLocation').text.strip()
    except AttributeError:
        return None


def get_job_summary(item):
    """Param: item in page's soup
        returns the summary of the specific job offer if exists"""
    try:
        return item.find('div', {'class': 'job-snippet'}).text.strip()
    except AttributeError:
        return None


def get_company_rating(item):
    """Param: item in page's soup
            returns the summary of the specific job offer if exists"""
    try:
        return item.find('span', class_='ratingNumber').text.strip()
    except AttributeError:
        return None


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
    except AttributeError:
        return None


def get_job_type(item):
    """Param: item in page's soup
         returns the job type of the specific job offer if exists"""
    try:
        return item.find(lambda tag: tag.name == 'div' and tag.get('class') == ["metadata"]).text.strip()
    except AttributeError:
        return None


def get_link_to_full_description(soup):
    """Param: receives the soup of the page, returns a list of the links to the job offers full description """
    job_column = soup.find('div', class_='mosaic-provider-jobcards')  # gets the column of the job offers
    link_list = []
    for i in job_column.find_all('a'):
        try:
            if i.attrs['id']:
                abs_path = urljoin(conf.SAMPLE_URL, i.get('href'))
                link_list.append(abs_path)
        except (KeyError, AttributeError):
            pass
    return link_list


def get_company_link(item):
    """Given the :item: in the job offer, returns the link of the company offering if exists"""
    try:
        comp_link = item.find('a', class_="turnstileLink companyOverviewLink", href=True).get('href')
        return urljoin(conf.SAMPLE_URL, comp_link)
    except AttributeError:
        return None


def get_comp_stat(soup):
    """
    Takes soup returns the stats
    :param soup: soup of a company's indeed page
    :return: Dict of Found numbers of reviews, salaries etc. on the comapny
    """
    comp = {}

    li_conts = soup.find_all('li', class_="css-tz4lm4 eu4oa1w0")
    for i in li_conts:
        try:
            if isfloat(i.find('div', class_="css-r228jg eu4oa1w0").text):
                comp[i['data-tn-element']] = float(i.find('div', class_="css-r228jg eu4oa1w0").text)
            else:
                comp[i['data-tn-element']] = float(
                    i.find('div', class_="css-r228jg eu4oa1w0").text.replace('K', '').replace('M', '')) * 1000

        except AttributeError:
            pass
    return comp


def get_comp_hapiness(soup):
    """
    Takes available information about the company's Hapiness degrees
    :param soup: soup of the company's webpage
    :return: dictionnary of the found elements
    """
    comp_hapiness = {}

    scripts = soup.find_all('script')
    for i in scripts:
        if 'window._initialData' in i.text:
            data = i.text
    data=data[data.find('{'):-data[::-1].find('}')]
    data=data.replace('\\','')
    print(data)
    data = json.loads(data)
    for el in data['happinessModule']['individualRatings']:
        comp_hapiness[el['category']] = el['score']
    return comp_hapiness

def get_about_comp(soup):
    """
    Takes soup of comapny's page returns available information on overview section of webpagw
    :param soup:
    :return: dictionnary of found parameters
    """
    about_comp = {}
    comp_size = {'5,001 to 10,000': 5001, 'more than 10,000': 10001, '1001 to 5,000': 1001, '501 to 1,000': 501}
    comp_revenues = {'more than $10B (USD)': 10000000000,
                     '$100M to $500M (USD)': 100000000,
                     '$5B to $10B (USD)': 5000000000,
                     'less than $1M (USD)': 900000,
                     '$1B to $5B (USD)': 1000000000,
                     '$1M to $5M (USD)': 1000000,
                     '$500M to $1B (USD)': 500000000,
                     '$5M to $25M (USD)': 5000000
                     }
    # Find about table
    try:
        about = soup.find('ul', class_="css-1vd66n9 e37uo190")
        # add CEO name and approval rate
        about_comp[about.find('span', class_="css-3j50sk e1wnkr790").text] = about.find('span',
                                                                                        class_="css-1w0iwyp e1wnkr790").text
        about_comp['Approved'] = int(about.find('span', class_="css-4oitjw e1wnkr790").text.replace('%', ''))
        # add other elements
        for i in about.find_all('li', class_="css-ion97 e37uo190"):
            if i.find('div', class_="css-18pwhsj e1wnkr790").text == 'Founded':
                about_comp[i.find('div', class_="css-18pwhsj e1wnkr790").text] = int(i.find('div',
                                                                                            class_="css-1w0iwyp e1wnkr790").text)
            elif i.find('div', class_="css-18pwhsj e1wnkr790").text == 'Company size':
                if i.find('div', class_="css-1w0iwyp e1wnkr790").text in comp_size:
                    about_comp[i.find('div', class_="css-18pwhsj e1wnkr790").text] = comp_size[i.find('div',
                                                                                                      class_="css-1w0iwyp e1wnkr790").text]
                else:
                    about_comp[i.find('div', class_="css-18pwhsj e1wnkr790").text] = -999999

            elif i.find('div', class_="css-18pwhsj e1wnkr790").text == 'Revenue':
                if i.find('div', class_="css-1w0iwyp e1wnkr790").text in comp_revenues.keys():
                    about_comp[i.find('div', class_="css-18pwhsj e1wnkr790").text] = comp_revenues[i.find('div',
                                                                                                          class_="css-1w0iwyp e1wnkr790").text]
                else:
                    about_comp[i.find('div', class_="css-18pwhsj e1wnkr790").text] = -999999

            elif i.find('div', class_="css-18pwhsj e1wnkr790").text == 'Link':
                link = i.find('div', class_="css-1w0iwyp e1wnkr790")
                about_comp[i.find('div', class_="css-18pwhsj e1wnkr790").text] = link.find(href=True).get('href')

            else:
                about_comp[i.find('div', class_="css-18pwhsj e1wnkr790").text] = i.find('div',
                                                                                        class_="css-1w0iwyp e1wnkr790").text
    except AttributeError:
        pass
    return about_comp


def transform_comp_soups(soup_companies, comp_link_list):
    """
    Takes the soup of all companies pages on indeed and scrapps info
    :param soup_companies: dict of soup of companies
    :param comp_link_list: dict name:soup_companies:
    :return: appends data to the companies dicts
    """
    print('Extracting data from companies soups')

    for i, soup in enumerate(tqdm(soup_companies.values())):
        try:
            comp_link_list[i].update(get_comp_stat(soup))
            comp_link_list[i].update(get_comp_hapiness(soup))
            comp_link_list[i].update(get_about_comp(soup))
        except AttributeError:
            pass
    return
