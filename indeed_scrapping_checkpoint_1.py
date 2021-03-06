import argparse
import urllib.parse
from tqdm import tqdm
import conf
from extract_funcs import extract, extract_companies_soup, apply_proxy
from transform_funcs import transform_comp_soups, transform_job_offers
from update_mysql_db import update_mysql_db
from api_extract_funcs import getjobs_from_careerjet_api

"""
Web Scraping for Indeed.com; Returns  jobs and their meta-data
"""


def commandline_func():
    """The function allows the program to run from command line, where user should input one job name and the min number
    of jobs to scrape, there is also two optional features such as a welcome message and a help message displayed
    when -w and -h are inputted """

    parser = argparse.ArgumentParser(description='Scrapes the data of indeed website, scrapping data on job offers '
                                                 'according to researched job title and on companies offering the job '
                                                 'all over the USA')

    parser.add_argument('-w', '--welcome', help='prints welcome message', action='store_true')
    parser.add_argument('job_name', type=str, help='Job title to research')
    parser.add_argument('nb', type=int, help='Min number of jobs to scrape')
    parser.add_argument('-l', '--location', type=str, help='Place to specify in the job search')
    parser.add_argument('-a', '--api', type=int, help='Please specify if you get from Api ')
    parser.add_argument('-p', '--proxy', type=float, help='Please specify if you want to use a proxy ')

    args = parser.parse_args()
    if args.welcome:
        print("Good morning")
    if args.location:
        location = args.location
    else:
        location = conf.LOCATION

    return args.job_name, args.nb, location, args.api, args.proxy


def main():
    job_title, nb_scraps, location, api_nb, prox = commandline_func()
    # Convert Input to URL type
    job_title_url_format = urllib.parse.quote(job_title, safe='')
    location_url_format = urllib.parse.quote(location, safe='')
    number_of_scrap_conv = (nb_scraps // 15 + 1) * 10

    print("Scrapping in progress...\n Number of pages being scrapped")
    comp_list, joblist = [], []
    soup_list_jobs = extract(number_of_scrap_conv, job_title_url_format, location_url_format, prox)
    for soup in tqdm(soup_list_jobs):
        transform_job_offers(soup, joblist, comp_list, job_title)
    print(f'{len(joblist)} jobs imported from indeed')
    getjobs_from_careerjet_api(joblist, comp_list, job_title, location, api_nb)
    print(f'{len(joblist)} jobs imported in total')

    soup_companies = extract_companies_soup(comp_list, prox)
    transform_comp_soups(soup_companies, comp_list)

    print(f"Scrapping completed successfully: {len(joblist)} jobs imported ")
    print(f"Scrapping completed successfully: {len(comp_list)} companies imported ")

    update_mysql_db(job_list=joblist, company_list=comp_list)


if __name__ == '__main__':
    main()
