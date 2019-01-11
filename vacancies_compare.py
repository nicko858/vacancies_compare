import requests
from dotenv import load_dotenv
from os import getenv
import math
from terminaltables import AsciiTable
from collections import OrderedDict
import datetime
from requests import ConnectionError
from urllib3.exceptions import ResponseError


class APIUnavailable(Exception):
    pass


def get_time_period(day_ago):
    today = datetime.date.today()
    last_month = today - datetime.timedelta(days=day_ago)
    return today, last_month


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


def calculate_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from and not salary_to:
        return salary_from * 1.2
    elif salary_to and not salary_from:
        return salary_to * 0.8


def fill_vacancies_dict(
        vacancies_stat,
        prog_lang,
        vacancies_found,
        vacancies_processed,
        avg_salary):
    vacancies_stat[prog_lang] = OrderedDict()
    vacancies_stat[prog_lang]["vacancies_found"] = vacancies_found
    vacancies_stat[prog_lang]["vacancies_processed"] = vacancies_processed
    vacancies_stat[prog_lang]["average_salary"] = avg_salary


def predict_rub_salary_for_headhunter(vacancy):
    try:
        salary = vacancy["salary"]
        currency = salary["currency"]
    except TypeError:
        return
    if not salary or currency != "RUR":
        return None
    salary_from = salary["from"]
    salary_to = salary["to"]
    salary_avg = calculate_salary(salary_from, salary_to)
    return salary_avg


def predict_rub_salary_for_superjob(vacancy):
    try:
        currency = vacancy["currency"]
        salary_from = vacancy["payment_from"]
        salary_to = vacancy["payment_to"]
    except TypeError:
        return
    if not (salary_from and salary_to) or currency != "rub":
        return
    salary_avg = calculate_salary(salary_from, salary_to)
    return salary_avg


def average_salary(vacancies, site):
    predict_methods = {
        "SuperJob": predict_rub_salary_for_superjob,
        "Headhunter": predict_rub_salary_for_headhunter
    }
    salary_list = [predict_methods[site](vacancy)
                   for vacancy in vacancies
                   if predict_methods[site](vacancy)]
    if salary_list:
        avg_salary = int(sum(salary_list) / len(salary_list))
        return len(salary_list), avg_salary
    return len(salary_list), None


def make_terminal_table(vacancies_stat, site):
    table = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата']
    ]
    for prog_lang, stat in vacancies_stat.items():
        table_body = []
        table_body.append(prog_lang)
        for metric, metric_value in stat.items():
            table_body.append(metric_value)
        table.append(table_body)
    table = AsciiTable(table)
    table.title = "{} Moscow".format(site)
    return table


def fetch_from_superjob(programming_languages, headers):
    vacancies_stat = {}
    for prog_lang in programming_languages:
        url = "https://api.superjob.ru/2.0/vacancies/"
        params = {
            "town": 4,
            "keyword": "Программист {}".format(prog_lang),
            "catalogues": 48,
            "count": 100,
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
                response = requests.get(url, params=params, headers=headers)
            except (ConnectionError, ResponseError):
                print("{} is unavailable {}")
                print("Statistics may be corrupt!")
                continue
            resp_json = response.json()
            vacancies.extend(resp_json['objects'])
        vacancies_processed, avg_salary = average_salary(vacancies, "SuperJob")
        fill_vacancies_dict(
            vacancies_stat,
            prog_lang,
            vacancies_found,
            vacancies_processed,
            avg_salary)
    return vacancies_stat


def fetch_from_headhunter(programming_languages):
    vacancies_stat = {}
    for prog_lang in programming_languages:
        url = "https://api.hh.ru/vacancies"
        date_to, date_from = get_time_period(31)
        params = {
            "area": 1,
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
            except (ConnectionError, ResponseError):
                print("{} is unavailable {}")
                print("Statistics may be corrupt!")
                continue
            resp_json = response.json()
            vacancies.extend(resp_json["items"])
        vacancies_processed, avg_salary = average_salary(vacancies, "Headhunter")
        fill_vacancies_dict(
            vacancies_stat,
            prog_lang,
            vacancies_found,
            vacancies_processed,
            avg_salary)
    return vacancies_stat


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
    days_in_month = 31
    date_to, date_from = get_time_period(days_in_month)
    try:
        superjob_stat = fetch_from_superjob(programming_languages, headers)
        headhunter_stat = fetch_from_headhunter(programming_languages)
    except APIUnavailable as error:
        exit(error)
    superjob_table = make_terminal_table(superjob_stat, site="SuperJob")
    headhunter_table = make_terminal_table(headhunter_stat, site="Headhunter")
    print()
    print(superjob_table.table, headhunter_table.table, sep="\n\n")





