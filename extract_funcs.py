import grequests
from bs4 import BeautifulSoup

"""Functions extracting soups"""


def extract(number_of_scraps_conv, job_title_url_format='', location_url_format=''):
    """
    Extract html contents from all the pages
    :param location_url_format: string
    :param job_title_url_format: string
    :param number_of_scraps_conv: integer (multiple of 10)
    :return: lists of soup
    """
    url_list = [f'https://www.indeed.com/jobs?q={job_title_url_format}&l={location_url_format}&start={page}' for page in
                range(0, number_of_scraps_conv, 10)]
    rs = (grequests.get(url) for url in url_list)
    requests = grequests.map(rs)
    soups = [BeautifulSoup(response.content, 'html.parser') for response in requests]
    return soups


def extract_companies_soup(comp_link_list):
    """
    Takes the list of url of the companies previously scrapped returns list of the soups
    :param comp_link_list: list of the url of the indeed page of the companies
    :return: list of soups of these pages
    """
    rs = (grequests.get(i['indeed_company_link']) for i in comp_link_list)
    requests = grequests.map(rs)
    soups = {}
    for i, response in enumerate(requests):
        try:
            soups[comp_link_list[i]['name']] = BeautifulSoup(response.content, 'html.parser')
        except AttributeError:
            soups[comp_link_list[i]['name']] = None
    return soups
