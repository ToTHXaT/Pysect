from typing import Dict, List

import requests
from termcolor import colored

from src.expectations.base import *


def expect(response: Response, expectations) -> List[Explanation]:
    return [exp for exp in [i.is_meeting(response) for i in expectations] if isinstance(exp, Explanation)]


class BaseTest:
    headers = {}
    query_params = {}
    body = ""
    method = "GET"
    url = ""
    json_body = {}

    def set_headers(self, headers: Dict[str, str]):
        self.headers.update(**headers)

    def set_query_params(self, query: Dict[str, str]):
        self.query_params.update(**query)

    def set_json(self, json_body: dict):
        self.json_body = json_body

    def set_url(self, url: str):
        self.url = url

    def set_method(self, method: str):
        self.method = method

    def run_tests(self):
        test_funcs = [func for func in dir(self) if func.startswith('test_') and callable(getattr(self, func))]

        if len(test_funcs) < 1:
            raise Exception("No test functions to run tests")

        for func in test_funcs:
            explanations = getattr(self, func)()
            if explanations.__len__() < 1:
                print(colored('Passed at ' + __name__ + '.' + self.__class__.__name__ + '.' + func,
                              'green', attrs=['bold']))
            else:
                print(colored('Failed at ' + __name__ + '.' + self.__class__.__name__ + '.' + func,
                              'red', attrs=['bold', 'underline']))

                for i in explanations:
                    print('    ', colored(i, 'red'))

    def _send_request(self, **kwargs):
        method = kwargs.get('method') or self.method
        url = kwargs.get('url') or self.url
        url += kwargs.get('path', '')
        headers = {**self.headers, **kwargs.get('headers', {})}
        json_body = kwargs.get('json_body') or self.json_body
        query_params = {**self.query_params, **kwargs.get('query_params', {})}

        if method.upper() == 'GET':
            return requests.get(url, params=query_params, headers=headers)#, hooks={'response': print_req_res})
        if method.upper() == 'POST':
            return requests.post(url, params=query_params, headers=headers, data=json_body)