import requests
from bs4 import BeautifulSoup
from scraper_api import ScraperAPIClient

"""Functions extracting soups"""


def apply_proxy():
    """
    Ask user if apply proxy or not
    :return: Boolean
    """
    res = input('Do you want to run from proxy:[y/n]:')
    if res == 'y':
        return True
    else:
        return False


def extract(number_of_scraps_conv, job_title_url_format='', location_url_format='', prox=0):
    """
    Extract html contents from all the pages
    :param prox: boolean proxy
    :param location_url_format: string
    :param job_title_url_format: string
    :param number_of_scraps_conv: integer (multiple of 10)
    :return: lists of soup
    """
    url_list = [f'https://www.indeed.com/jobs?q={job_title_url_format}&l={location_url_format}&start={page}' for page in
                range(0, number_of_scraps_conv, 10)]
    if prox == 1:
        client = ScraperAPIClient('960e44a893382d6a37505c837a092346')
        rs = [client.get(url) for url in url_list]
    else:
        print('No proxy used jobs')
        rs = [requests.get(url) for url in url_list if url]

    soups = [BeautifulSoup(response.content, 'html.parser') for response in rs]
    return soups


def extract_companies_soup(comp_link_list, prox=0):
    """
    Takes the list of url of the companies previously scrapped returns list of the soups
    :param prox: apply prox
    :param comp_link_list: list of the url of the indeed page of the companies
    :return: list of soups of these pages
    """
    client = ScraperAPIClient('960e44a893382d6a37505c837a092346')
    rs = [client.get(i['indeed_company_link']) for i in comp_link_list if i is not None]

    soups = {}
    for i, response in enumerate(rs):
        try:
            soups[comp_link_list[i]['name']] = BeautifulSoup(response.content, 'html.parser')
        except AttributeError:
            soups[comp_link_list[i]['name']] = None
    return soups
