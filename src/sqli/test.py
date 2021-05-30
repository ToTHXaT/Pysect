from sqlite3 import connect

from typing import *

import requests
from termcolor import colored

con = connect('test.db')
cur = con.cursor()
#con.execute('CREATE TABLE User (username varchar(80), password varchar(80))')
#con.execute('INSERT INTO User values ("Ainur", "1234")')
#con.commit()
"""query = 'select username, password from User where username = "{}" and password = "{}"'\
    .format('Ainur" and sleep(1000) --', '1234')

res = cur.execute(query)
print(query)
print(cur.fetchall())

con.close()"""


class SQLInjectionTest:
    headers = {}
    query_params = {}
    body = ""
    method = "GET"
    url = ""
    json_body = {}

    sqli = ['"; abcd --', "'; abcd --", '"; abcd /*', "'; abcd /*", '; abcd ']


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
            return requests.get(url, params=query_params, headers=headers)
        if method.upper() == 'POST':
            return requests.post(url, params=query_params, headers=headers, data=json_body)
