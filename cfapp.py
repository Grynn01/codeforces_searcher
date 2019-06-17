import requests
import json
import operator


class ApiError(Exception):
    def __init__(self):
        self.message = 'Codeforces API Error'


class ZeroProblemError(Exception):
    def __init__(self):
        self.message = 'All problems with this configuration have been made'


def test_api():
    url = 'https://codeforces.com/api/problemset.problems?tags=implementation'
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError()


def generate_template(method: str, params: list) -> str:
    string = method + '?'
    for param in params:
        tmp = param + '={}'
        string += tmp
    return string


def make_query(method: str, params_name: list, params_values: list) -> dict:
    '''
    Build ans make the query to Codeforces Api,
    returning the problemset filtered by tag
    '''
    url = 'http://codeforces.com/api/' +\
          generate_template(method, params_name).format(params_values)
    response = requests.get(url)
    if response.status_code != 200:
        raise ApiError()
    problems = json.loads(response.text)
    return problems['result']


def level_filter(set: dict, min_level, max_level) -> list:
    '''
    From the problems filtered by tag, this function
    filters by difficult and return the problems in a list
    '''

    filtered_problems = []
    for i in range(len(set['problems'])):
        try:
            if min_level <= int(set['problems'][i]['rating']) <= max_level:
                filtered_problems.append(set['problemStatistics'][i])
        except Exception:
            continue
    sorted_problems = sorted(filtered_problems,
                             key=operator.itemgetter('solvedCount'),
                             reverse=True)
    return sorted_problems


def get_submits(handle: str):
    submits = make_query('user.status', ['handle'], handle)
    return submits


def check_problem(handle: str, problem: object) -> bool:
    submits = get_submits(handle)
    for submit in submits:
        if problem['contestId'] == submit['problem']['contestId'] and\
           problem['index'] == submit['problem']['index']\
           and submit['verdict'] == 'OK':
            return False
    return True


def get_problem(handle: str, problems: list) -> tuple:
    for problem in problems:
        if check_problem(handle, problem):
            return (problem['contestId'], problem['index'])
    raise ZeroProblemError()


def generate_url(ids: tuple) -> str:
    url = 'https://codeforces.com/problemset/problem/{}/{}'.format(ids[0],
                                                                   ids[1])
    return url
