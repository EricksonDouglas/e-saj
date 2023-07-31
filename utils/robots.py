from abc import abstractmethod, ABC
from datetime import datetime
from json import dump as json_dump
from re import sub as re_sub
from typing import Optional, Dict

from lxml.html import HtmlElement, fromstring
from requests import Session

from utils.definers import ModelResult, ModelParamsTypedDict

__import__("urllib3").disable_warnings(__import__("urllib3").exceptions.InsecureRequestWarning)
__import__("urllib3").disable_warnings()


class Robot(ABC):
    def __init__(self, params: ModelParamsTypedDict, logger):
        self._params = params
        self._logger = logger
        self._session = Session()
        self._session.verify = False

    @property
    def session(self) -> Session:
        return self._session

    @property
    def logger(self):
        return self._logger

    @property
    def params(self) -> ModelParamsTypedDict:
        return self._params

    @staticmethod
    def to_xpath(text: str) -> HtmlElement:
        return fromstring(text)

    @staticmethod
    def get_value_xpath(page: HtmlElement, fmt: str, enable_upper: bool = False) -> Optional[str]:
        text = page.xpath(f"string({fmt})").strip()
        text = text.upper() if enable_upper else text
        return text or None

    @staticmethod
    def only_digits(value: str) -> str:
        return re_sub(r"\D+", "", value)

    @staticmethod
    def str_to_iso_format(value: str, fmt: str) -> str:
        return datetime.strptime(value, fmt).isoformat()

    @staticmethod
    def save_to_json(result: Dict, filename: str) -> None:
        json_dump(result, open(f"{filename}.json", "w"), indent=4, ensure_ascii=False)

    @abstractmethod
    def run(self) -> ModelResult:
        raise NotImplemented
