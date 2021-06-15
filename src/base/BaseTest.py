from typing import Dict, List

from termcolor import colored
import requests

from src.expectations.base import *


class BaseTest:
    headers = {}
    query_params = {}
    body = ""
    method = "GET"
    url = ""
    json_body = {}
    response: Response
    explanations: List[Explanation]

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

    def expect(self, expectations):
        self.explanations = [exp for exp in [i.is_meeting(self.response) for i in expectations] if isinstance(exp, Explanation)]

    def run_tests(self):
        test_funcs = [func for func in dir(self) if func.startswith('test_') and callable(getattr(self, func))]

        if len(test_funcs) < 1:
            raise Exception("No test functions to run tests")

        for func in test_funcs:
            getattr(self, func)()
            if self.explanations.__len__() < 1:
                print(colored('Passed at ' + __name__ + '.' + self.__class__.__name__ + '.' + func,
                              'green', attrs=['bold']))
            else:
                print(colored('Failed at ' + __name__ + '.' + self.__class__.__name__ + '.' + func,
                              'red', attrs=['bold', 'underline']))

                for i in self.explanations:
                    print('    ', colored(i, 'red'))
                self.explanations.clear()

    def send_request(self, **kwargs):
        method = kwargs.get('method') or self.method
        url = kwargs.get('url') or self.url
        url += kwargs.get('path', '')
        headers = {**self.headers, **kwargs.get('headers', {})}
        json_body = kwargs.get('json_body') or self.json_body
        query_params = {**self.query_params, **kwargs.get('query_params', {})}

        if method.upper() == 'GET':
            self.response = requests.get(url, params=query_params, headers=headers)
        if method.upper() == 'POST':
            self.response = requests.post(url, params=query_params, headers=headers, data=json_body)
        if method.upper() == 'PUT':
            self.response = requests.put(url, params=query_params, headers=headers, data=json_body)
        if method.upper() == 'DELETE':
            self.response = requests.delete(url, params=query_params, headers=headers, data=json_body)
        if method.upper() == 'OPTIONS':
            self.response = requests.options(url, params=query_params, headers=headers, data=json_body)

