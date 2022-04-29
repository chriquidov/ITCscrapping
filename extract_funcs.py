import requests
from bs4 import BeautifulSoup
from scraper_api import ScraperAPIClient


"""Functions extracting soups"""


def extract(number_of_scraps_conv, job_title_url_format='', location_url_format=''):
    """
    Extract html contents from all the pages
    :param location_url_format: string
    :param job_title_url_format: string
    :param number_of_scraps_conv: integer (multiple of 10)
    :return: lists of soup
    """
    client = ScraperAPIClient('960e44a893382d6a37505c837a092346')
    url_list = [f'https://www.indeed.com/jobs?q={job_title_url_format}&l={location_url_format}&start={page}' for page in
                range(0, number_of_scraps_conv, 10)]
    rs = [client.get(url) for url in url_list]

    soups = [BeautifulSoup(response.content, 'html.parser') for response in rs]
    return soups


def extract_companies_soup(comp_link_list):
    """
    Takes the list of url of the companies previously scrapped returns list of the soups
    :param comp_link_list: list of the url of the indeed page of the companies
    :return: list of soups of these pages
    """
    client = ScraperAPIClient('960e44a893382d6a37505c837a092346')
    rs = [client.get(i['indeed_company_link']) for i in comp_link_list]
    soups = {}
    for i, response in enumerate(rs):
        try:
            soups[comp_link_list[i]['name']] = BeautifulSoup(response.content, 'html.parser')
        except AttributeError:
            soups[comp_link_list[i]['name']] = None
    return soups
