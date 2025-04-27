from typing import Dict, Any

from .base_requester import BaseRequester


class TokenAuthRequester(BaseRequester):
    def __init__(
        self,
        base_url: str, response_type: str, timeout_in_seconds: int,
        rate_limit_config: Dict[str, Any],
        token: str
    ):
        super().__init__(base_url, response_type, timeout_in_seconds, rate_limit_config)

        self.__token = token

    def authenticate(self):
        self._session.headers.update({
            'token': self.__token
        })

        self.authenticated = True
