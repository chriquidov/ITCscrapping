import pandas as pd
import urllib.parse
from tqdm import tqdm
import time
import conf
import os
import argparse
from extract_funcs import extract, extract_companies_soup
from transform_funcs import transform_comp_soups, transform_job_offers
from update_mysql_db import update_mysql_db

"""
Web Scraping for Indeed.com; Returns  jobs and their meta-data
"""


def commandline_func():
    """The function allows programm to run from command line, where user should input one job name and the min number of jobs to scrape,
    there is also two optionnal features such as a welcome message and a help message displayed when -w and -h
    are inputted"""

    parser = argparse.ArgumentParser(description='Scrapes the data of indeed website, scrapping data on job offers '
                                                 'according to reaserched job title and on companies offering the job '
                                                 'all over the USA')

    parser.add_argument('-w', '--welcome', help='prints welcome message', action='store_true')
    parser.add_argument('job_name', type=str, help='Job title to research')
    parser.add_argument('nb', type=int, help='Min number of jobs to scrape')
    parser.add_argument('-l', '--location', type=float, help='Place to specify in the job search')

    args = parser.parse_args()
    if args.welcome:
        print("Good morning")
    if args.location:
        location = args.location
    else:
        location = conf.LOCATION

    return args.job_name, args.nb, location


def main():
    job_title, nb_scraps, location = commandline_func()
    # Convert Input to URL type
    job_title_url_format = urllib.parse.quote(job_title, safe='')
    location_url_format = urllib.parse.quote(location, safe='')
    number_of_scrap_conv = (nb_scraps // 15 + 1) * 10

    print("Scrapping in progress...\n Number of pages being scrapped")
    comp_list, joblist = [], []
    soup_list_jobs = extract(number_of_scrap_conv, job_title_url_format, location_url_format)
    for soup in tqdm(soup_list_jobs):
        transform_job_offers(soup, joblist, comp_list,job_title)

    soup_companies = extract_companies_soup(comp_list)
    transform_comp_soups(soup_companies, comp_list)

    timestr = time.strftime("%y%m%d_%H%M")
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # jobs_df = pd.DataFrame(joblist)
    # print('Here are a few exemple of the scrapped data\n', jobs_df.head())
    # jobs_df.to_csv(dir_path+'\\'+conf.JOBS_FILENAME + ".csv", encoding='utf-8')
    print(f"Scrapping completed successfully: {len(joblist)} jobs imported ")

    # comp_df = pd.DataFrame(comp_list)
    # comp_df.to_csv(f'{dir_path}\\companies.csv')
    # print('Here are a few exemple of the scrapped data\n', comp_df.head())
    print(f"Scrapping completed successfully: {len(comp_list)} companies imported ")
    update_mysql_db(job_list=joblist,company_list=comp_list)

if __name__ == '__main__':
    main()
