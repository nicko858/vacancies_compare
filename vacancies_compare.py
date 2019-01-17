import requests
from dotenv import load_dotenv
from os import getenv
import math
from requests import ConnectionError
from urllib3.exceptions import ResponseError
from handle_data import get_time_period
from handle_data import fill_vacancies_dict
from handle_data import average_salary
from handle_data import make_terminal_table


class APIUnavailable(Exception):
    pass


def get_pages_and_vacancies_count(url, params, headers=None, site=None):
    try:
        response = requests.get(url, params=params, headers=headers)
    except (ConnectionError, ResponseError):
        raise APIUnavailable("{} is unavailable!".format(url))
    if not response.ok:
        raise APIUnavailable(("{} is unavailable!".format(url)))
    resp_json = response.json()
    if site == "SuperJob":
        vacancies_count = resp_json["total"]
        pages_count = math.ceil(vacancies_count / params["count"])
    else:
        vacancies_count = resp_json["found"]
        pages_count = resp_json["pages"]
    return pages_count, vacancies_count


def fetch_from_superjob(
        programming_languages,
        headers,
        town=4,
        job_catalog=48,
        per_page=100
):
    vacancies_stat = {}
    error_data = []
    for prog_lang in programming_languages:
        url = "https://api.superjob.ru/2.0/vacancies/"
        params = {
            "town": town,
            "keyword": "Программист {}".format(prog_lang),
            "catalogues": job_catalog,
            "count": per_page,
        }
        pages_count, vacancies_found = get_pages_and_vacancies_count(
            url,
            params,
            headers=headers,
            site="SuperJob"
        )
        vacancies = []
        for page in range(0, pages_count):
            params["page"] = page
            try:
                response = requests.get(
                    url,
                    params=params,
                    headers=headers
                )
                if not response.ok:
                    raise ResponseError
            except (ConnectionError, ResponseError):
                error_data.append(url)
                continue
            response = requests.get(url, params=params, headers=headers)
            resp_json = response.json()
            vacancies.extend(resp_json['objects'])
        vacancies_processed, avg_salary = average_salary(
            vacancies,
            "SuperJob"
        )
        fill_vacancies_dict(
            vacancies_stat,
            prog_lang,
            vacancies_found,
            vacancies_processed,
            avg_salary)
    return vacancies_stat, error_data


def fetch_from_headhunter(programming_languages, period=31, area=1):
    vacancies_stat = {}
    error_data = []
    for prog_lang in programming_languages:
        url = "https://api.hh.ru/vacancies"
        date_to, date_from = get_time_period(period)
        params = {
            "area": area,
            "vacancy_search_fields": "name",
            "text": "Программист {}".format(prog_lang),
            "date_from": date_from,
            "date_to": date_to
        }
        pages_count, vacancies_found = get_pages_and_vacancies_count(
            url,
            params,
            site="Headhunter"
        )
        vacancies = []
        for page in range(0, pages_count):
            params["page"] = page
            try:
                response = requests.get(url, params=params)
                if not response.ok:
                    raise ResponseError
            except (ConnectionError, ResponseError):
                error_data.append(url)
                continue
            resp_json = response.json()
            vacancies.extend(resp_json["items"])
        vacancies_processed, avg_salary = average_salary(
            vacancies,
            "Headhunter"
        )
        fill_vacancies_dict(
            vacancies_stat,
            prog_lang,
            vacancies_found,
            vacancies_processed,
            avg_salary)
    return vacancies_stat, error_data


if __name__ == '__main__':
    load_dotenv()
    secret_key = getenv("secret_key")
    headers = {"X-Api-App-Id": secret_key}
    programming_languages = [
        "Swift",
        "TypeScript",
        "Scala",
        "Objective-C",
        "Go",
        "C/C++",
        "C#",
        "PHP",
        "Ruby",
        "Python",
        "Java",
        "JavaScript"
    ]
    try:
        superjob_stat, superjob_error_data = fetch_from_superjob(
            programming_languages,
            headers,
            town=4,
            job_catalog=48,
            per_page=100
        )
        headhunter_stat, headhunter_error_data = fetch_from_headhunter(
            programming_languages,
            period=31,
            area=1
        )
        error_data = superjob_error_data + headhunter_error_data
        if error_data:
            print("Some sources is unavailable! "
                  "Statistics excluded this sources:")
            [print(url) for url in error_data]
    except APIUnavailable as error:
        exit(error)
    superjob_table = make_terminal_table(
        superjob_stat,
        site="SuperJob",
        area="Moscow"
    )
    headhunter_table = make_terminal_table(
        headhunter_stat,
        site="Headhunter",
        area="Moscow"
    )
    print()
    print(superjob_table.table, headhunter_table.table, sep="\n\n")





