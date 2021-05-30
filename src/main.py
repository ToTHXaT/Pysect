from typing import Dict, List

import requests
from requests import Response
from termcolor import colored
from pydantic import BaseModel

from src.expectations.base import *
from src.base.BaseTest import *

BASE_URL = "https://5f8ad2fb8453150016706248.mockapi.io/api/"


class UserSchema(BaseModel):
    id: int
    name: str
    money: str


class UserListSchema(BaseModel):
    __root__: List[UserSchema]


class TestSmth(BaseTest):
    url = 'https://www.google.com/'

    def test_smth(self) -> List[Explanation]:
        response = self._send_request()

        return expect(response, [
            HeaderToBePresent('Content-Type'),
            StatusCodeToBeSuccessful()
        ])

    def test_error(self) -> List[Explanation]:
        response = self._send_request(path='some')

        return expect(response, [
            HeaderToBePresent('Content-Type'),
            StatusCodeToBeClientError()
        ])

    def test_mock(self) -> List[Explanation]:
        response = self._send_request(url=BASE_URL, path='user')

        return expect(response, [
            StatusCodeToBeSuccessful(),
            HeaderToBeEqual('Content-Type', 'application/json'),
            JSONToBeMatchingSchema(UserListSchema)
        ])

    def test_post(self) -> List[Explanation]:
        response = self._send_request(url=BASE_URL, path='user', method='POST',
                                      json_body={'name': 'Gans', 'money': '0.00'})

        return expect(response, [
            StatusCodeToBeSuccessful(),
            JSONToBeMatchingSchema(UserSchema)
        ])


if __name__ == '__main__':
    bt = TestSmth()

    bt.run_tests()
