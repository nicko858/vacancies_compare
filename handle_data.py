from terminaltables import AsciiTable
from collections import OrderedDict
import datetime


def get_time_period(day_ago):
    today = datetime.date.today()
    last_month = today - datetime.timedelta(days=day_ago)
    return today, last_month


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


def make_terminal_table(vacancies_stat, site, area):
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
    table.title = "{} {}".format(site, area)
    return table


def predict_rub_salary_for_headhunter(vacancy):
    try:
        salary = vacancy["salary"]
        currency = salary["currency"]
    except (TypeError, KeyError):
        return
    if not salary or currency != "RUR":
        return
    salary_avg = calculate_salary(salary["from"], salary["to"])
    return salary_avg


def predict_rub_salary_for_superjob(vacancy):
    try:
        currency = vacancy["currency"]
        salary_from = vacancy["payment_from"]
        salary_to = vacancy["payment_to"]
    except (TypeError, KeyError):
        return
    if not (salary_from and salary_to) or currency != "rub":
        return
    salary_avg = calculate_salary(salary_from, salary_to)
    return salary_avg