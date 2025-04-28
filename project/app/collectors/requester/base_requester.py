from abc import ABC, abstractmethod
import asyncio
import aiohttp
from requests.models import Response
from typing import Union, Dict, List, Any, Optional
import xml.etree.ElementTree as ET

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

        self._session: Optional[aiohttp.ClientSession] = None
        self._authenticated = False

        self._rate_limiter = RateLimiter(**rate_limit_config)

    async def _create_session(self):
        timeout = aiohttp.ClientTimeout(total=self._timeout)
        self._session = aiohttp.ClientSession(timeout=timeout)

    async def _get_session(self):
        if self._session is None:
            await self._create_session()

        return self._session

    async def close_session(self):
        if self._session is not None:
            await self._session.close()

    @abstractmethod
    async def authenticate(self):
        pass

    def get_rate_limiter_data(self):
        return self._rate_limiter.to_dict()

    async def request(self, endpoint, method='GET', data=None):
        if not self._authenticated:
            await self.authenticate()

        try:
            self._rate_limiter.check()
        except RateLimitLimitReachedException as e:
            # rate limit achieved, sleeping till the next timeframe starts
            print(f"Rate limit reached: {e}")
            await asyncio.sleep(e.seconds_until_next_timeframe())
            print("Waked up from waiting for the next rate limit timeframe")

        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        method = method.upper()

        try:
            current_session = await self._get_session()

            if method == 'GET':
                async with current_session.get(url, params=data) as response:
                    response.raise_for_status()

                    return await self.parse_response(response)

            elif method == 'POST':
                async with current_session.post(url, params=data) as response:
                    response.raise_for_status()

                    return await self.parse_response(response)

            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

        except aiohttp.ClientResponseError as e:
            print(f"Request error: status_code={e.status}, message={e.message}")

        except aiohttp.ClientError as e:
            print(f"Request failed: {e}")

        return None

    async def parse_response(self, response: Response) -> Union[Dict, List, str, ET.Element, ET.ElementTree]:
        match self._response_type:
            case 'json':
                return await response.json()
            case 'xml':
                return await response.xml()
            case _:
                return await response.text()
