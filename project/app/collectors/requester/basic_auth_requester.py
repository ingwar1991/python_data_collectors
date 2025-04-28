import aiohttp
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

    async def authenticate(self):
        current_session = await self._get_session()
        current_session.auth = aiohttp.BasicAuth(self.__username, self.__password)

        self.authenticated = True
