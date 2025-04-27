from abc import ABC, abstractmethod
import requests
from requests.models import Response
from typing import Union, Dict, List, Any
import xml.etree.ElementTree as ET
import time

from .rate_limiter import RateLimitLimitReachedException, RateLimiter


class BaseRequester(ABC):
    def __init__(
        self,
        base_url: str, response_type: str, timeout_in_seconds: int,
        rate_limit_config: Dict[str, Any]
    ):
        self._base_url = base_url
        self._response_type = response_type
        self._timeout = timeout_in_seconds

        self._session = requests.Session()
        self._authenticated = False

        self._rate_limiter = RateLimiter(**rate_limit_config)

    @abstractmethod
    def authenticate(self):
        pass

    def get_rate_limiter_data(self):
        return self._rate_limiter.to_dict()

    def request(self, endpoint, method='GET', data=None):
        if not self._authenticated:
            self.authenticate()

        try:
            self._rate_limiter.check()
        except RateLimitLimitReachedException as e:
            # rate limit achieved, sleeping till the next timeframe starts
            print(f"Rate limit reached: {e}")
            time.sleep(e.seconds_until_next_timeframe())
            print("Waked up from waiting for the next rate limit timeframe")

        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        method = method.upper()

        try:
            if method == 'GET':
                response = self._session.get(url, params=data, timeout=self._timeout)
            elif method == 'POST':
                response = self._session.post(url, params=data, timeout=self._timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()

            return self.parse_response(response)

        except requests.RequestException as e:
            print(f"Request error: status_code={response.status_code}, response_text={response.text}, error={e}")
            return None

    def parse_response(self, response: Response) -> Union[Dict, List, str, ET.Element, ET.ElementTree]:
        match self._response_type:
            case 'json':
                return response.json()
            case 'xml':
                return response.xml()
            case _:
                return response.text()
