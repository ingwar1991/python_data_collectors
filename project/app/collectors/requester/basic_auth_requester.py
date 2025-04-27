from requests.auth import HTTPBasicAuth
from typing import Dict, Any

from .base_requester import BaseRequester


class BasicAuthRequester(BaseRequester):
    def __init__(
        self,
        base_url: str, response_type: str, timeout_in_seconds: int,
        rate_limit_config: Dict[str, Any],
        username: str, password: str
    ):
        super().__init__(base_url, response_type, timeout_in_seconds)

        self.__username = username
        self.__password = password

    def authenticate(self):
        self._session.auth = HTTPBasicAuth(self.__username, self.__password)
        self.authenticated = True
