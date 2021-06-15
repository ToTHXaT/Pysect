from typing import Dict, List

from termcolor import colored
import requests

from src.expectations.base import *
from src.base import BaseTest


class AuthTest(BaseTest):

    def run_tests(self):
        for role in self.roles:
            for resource in self.resourses:
                self.send_request(**role.get('auth'))

                if 200 <= self.response.status_code < 300:
                    if resource in self.expectations.get(role):
                        print(colored('Passed at ' + __name__ + '.' + self.__class__.__name__,
                                      'green', attrs=['bold']))
                else:
                    if not resource in self.expectations.get(role):
                        print(colored('Passed at ' + __name__ + '.' + self.__class__.__name__,
                                      'green', attrs=['bold']))

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

        kwargs.get('post_action', lambda *args: None)()





