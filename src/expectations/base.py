import inspect
from pydantic.dataclasses import dataclass
from pydantic import BaseModel, ValidationError
from typing import Callable, Union, Type
from requests import Response
import re


class Explanation:
    __slots__ = ('expl',)
    expl: str

    def __init__(self, expl: str):
        self.expl = expl

    def __str__(self):
        return self.expl


class BaseExpectation:

    def is_meeting(self, response: Response):
        raise NotImplementedError()


@dataclass
class HeaderToBe(BaseExpectation):
    header: str


@dataclass
class StatusCodeToBe(BaseExpectation):
    status_code: int


@dataclass
class JSONToBe(BaseExpectation):
    shema: Type[BaseModel]


@dataclass
class HeaderToBePresent(HeaderToBe):

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if self.header in response.headers:
            return True
        else:
            return Explanation(f"Header '{self.header}' is not present in response")


@dataclass
class HeaderToBeEqual(HeaderToBe):
    value: str

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if self.header in response.headers:
            if response.headers.get(self.header, '') == self.value:
                return True
            else:
                return Explanation(f"Header '{self.header} is equal to '{response.headers.get(self.header)}'"
                                   f", expected to be '{self.value}'")
        else:
            return Explanation(f"Header '{self.header}' is not present in response")


@dataclass
class HeaderToBeMatchingRegexp(HeaderToBe):
    regexp: str

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if self.header in response.headers and re.match(self.regexp, self.header):
            return True
        else:
            return Explanation(f"Header '{self.header} doesn\'t match regexp '{self.regexp}'")


@dataclass
class HeaderToBeValidatableBy(HeaderToBe):
    validator: Callable[[str, Response], bool]

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if self.validator(self.header, response):
            return True
        else:
            return Explanation(f"Header {self.header} wasn\'t marked as valid by custom function "
                               f"\n{inspect.getsource(self.validator)}")


@dataclass
class StatusCodeToBeEqual(StatusCodeToBe):

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if self.status_code == response.status_code:
            return True
        else:
            return Explanation(f"Status code is {response.status_code}, expected to be {self.status_code}")


@dataclass
class StatusCodeToBeInformational:

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if 100 <= response.status_code < 200:
            return True
        else:
            return Explanation(f"Status code is {response.status_code}, expected to be informational")


@dataclass
class StatusCodeToBeSuccessful:

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if 200 <= response.status_code < 300:
            return True
        else:
            return Explanation(f"Status code is {response.status_code}, expected to be successful")


@dataclass
class StatusCodeToBeRedirected:

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if 300 <= response.status_code < 400:
            return True
        else:
            return Explanation(f"Status code is {response.status_code}, expected to be redirected")


@dataclass
class StatusCodeToBeClientError:

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if 400 <= response.status_code < 500:
            return True
        else:
            return Explanation(f"Status code is {response.status_code}, expected to be client error")


@dataclass
class StatusCodeToBeServerError:

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if 500 <= response.status_code < 600:
            return True
        else:
            return Explanation(f"Status code is {response.status_code}, expected to be server error")


@dataclass
class JSONToBeMatchingSchema(JSONToBe):

    def is_meeting(self, response: Response) -> Union[bool, Explanation]:
        if response.headers.get('Content-Type') == 'application/json':
            try:
                json = response.json()
            except Exception:
                return Explanation(f"JSON is invalid")
        else:
            return Explanation(f"Response body is not json")

        try:
            obj = self.shema.parse_obj(json)
            return True
        except ValidationError as e:
            return Explanation(f"Json data is not matching schema"
                               f"\n{e}")