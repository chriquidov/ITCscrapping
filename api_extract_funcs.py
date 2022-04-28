from careerjet_api import CareerjetAPIClient
import conf


def getjobs_from_careerjet_api(job_list, comp_list, job_title, location):
    """
    Function gets data from careerjet_api and adds to the list of jobs and companies the data on the jobs in the lists
    :param job_list: list of jobs form indeed scrapping
    :param comp_list: list of companies form indeed scrapping
    :param job_title: searched job by user
    :param location: location of job
    :return:
    """
    nb_jobs = askuser_if_get_from_api()
    if nb_jobs <= 0:
        return
    else:
        nb_req = (99 + nb_jobs - 1) // 99
        for i in range(nb_req):
            cj = CareerjetAPIClient("en_US")

            result_json = cj.search({
                'location': location,
                'keywords': job_title,
                'affid': '213e213hd12344552',
                'user_ip': '11.22.33.44',
                'url': 'http://www.example.com/jobsearch',
                'user_agent': conf.HEADERS,
                'pagesize': 99})
            add_job_data_to_lists(job_list, comp_list, result_json, job_title)
    return


def askuser_if_get_from_api():
    """
    Ask the user to give a number of jobs to get from the careerjet api
    :return: nb jobs to get
    """
    int_check = False
    nb_jobs_careerjet = 'a'
    while not int_check:
        nb_jobs_careerjet = input(
            'If you want to get jobs from the careerjet_api enter the minimum number \
of jobs you want to get else enter 0: ')
        int_check = isint(nb_jobs_careerjet)
    return int(nb_jobs_careerjet)


def add_job_data_to_lists(job_list, comp_list, result_json, job_title):
    """
    Adds jobs to the list of jobs and companies from the request
    :param job_list:
    :param comp_list:
    :param result_json: result of the request from api
    :param job_title: searched job title
    :return:
    """
    for j in result_json['jobs']:
        job = {
            'title': j['title'],
            'searched_title': job_title,
            'company': j['company'],
            'location': j['locations'],
            'salary': transform_salary(j['salary']),
            'job_type': None,
            'summary': j['description'].replace('<b>', '').replace('</b>', '').replace('/', ''),
            'link_job': j['url'],
            'indeed_company_link': None
        }

        job_list.append(job)
        comp_dict = {'name': j['company'], 'indeed_company_link': None}
        comp_list.append(comp_dict)
    return


def isint(s):
    """
    Checks if string is an int
    :param s: inputted string
    :return: boolean
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def transform_salary(str_sal):
    sal = ''
    print("-" * 200, str_sal)
    for i in str_sal:
        if i in [' ', '-', '']:
            break
        elif i in ['$']:
            continue
        elif i.isdigit():
            sal += i
    if sal.isdigit():
        return int(sal)
    else:
        return None
