import requests
from termcolor import colored

from src.base import BaseTest

sqli_raw = """'
"
#
-
--
'%20--
--';
'%20;
=%20'
=%20;
=%20--
\x23
\x27
\x3D%20\x3B'
\x3D%20\x27
\x27\x4F\x52 SELECT *
\x27\x6F\x72 SELECT *
'or%20select *
admin'--
<>"'%;)(&+
'%20or%20''='
'%20or%20'x'='x
"%20or%20"x"="x
')%20or%20('x'='x
0 or 1=1
' or 0=0 --
" or 0=0 --
or 0=0 --
' or 0=0 #
" or 0=0 #
or 0=0 #
' or 1=1--
" or 1=1--
' or '1'='1'--
"' or 1 --'"
or 1=1--
or%201=1
or%201=1 --
' or 1=1 or ''='
" or 1=1 or ""="
' or a=a--
" or "a"="a
') or ('a'='a
") or ("a"="a
hi" or "a"="a
hi" or 1=1 --
hi' or 1=1 --
hi' or 'a'='a
hi') or ('a'='a
hi") or ("a"="a
'hi' or 'x'='x';
@variable
,@variable
PRINT
PRINT @@variable
select
insert
as
or
procedure
limit
order by
asc
desc
delete
update
distinct
having
truncate
replace
like
handler
bfilename
' or username like '%
' or uname like '%
' or userid like '%
' or uid like '%
' or user like '%
exec xp
exec sp
'; exec master..xp_cmdshell
'; exec xp_regread
t'exec master..xp_cmdshell 'nslookup www.google.com'--
--sp_password
\x27UNION SELECT
' UNION SELECT
' UNION ALL SELECT
' or (EXISTS)
' (select top 1
'||UTL_HTTP.REQUEST
1;SELECT%20*
to_timestamp_tz
tz_offset
&lt;&gt;&quot;'%;)(&amp;+
'%20or%201=1
%27%20or%201=1
%20$(sleep%2050)
%20'sleep%2050'
char%4039%41%2b%40SELECT
&apos;%20OR
'sqlattempt1
(sqlattempt2)
|
%7C
*|
%2A%7C
*(|(mail=*))
%2A%28%7C%28mail%3D%2A%29%29
*(|(objectclass=*))
%2A%28%7C%28objectclass%3D%2A%29%29
(
%28
)
%29
&
%26
!
%21
' or 1=1 or ''='
' or ''='
x' or 1=1 or 'x'='y
/
//
//*
*/*
"""


class SQLInjectionTest(BaseTest):
    sqli_n = 0
    sqli = sqli_raw.split('\n')

    def inject(self, s: str):
        return s + self.sqli[self.sqli_n]

    def _inject_forward(self):
        self.sqli_n += 1

    def run_tests(self):
        test_funcs = [func for func in dir(self) if func.startswith('test_') and callable(getattr(self, func))]

        if len(test_funcs) < 1:
            raise Exception("No test functions to run tests")

        for func in test_funcs:
            for _ in self.sqli:
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


