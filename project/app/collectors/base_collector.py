from abc import ABC, abstractmethod
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from .requester import BaseRequester, NoAuthRequester, BasicAuthRequester, TokenAuthRequester, TokenBearerAuthRequester, OAuthRequester
from ..db.async_mongo import fix_dt_for_db
from .hydrated.base_collection import BaseHydratedCollection


class BaseCollector(ABC):
    def __init__(self, config, rate_limit_data: Dict[str, Any] = None):
        self.config = config

        self.__rate_limit_data = rate_limit_data if rate_limit_data is not None else {}
        self.__requester = None

        base_config_path = Path(__file__).parent / 'config.yaml'
        with open(base_config_path, 'r') as f:
            self._base_config = yaml.safe_load(f)

    def _get_limit(self) -> int:
        limit = self.config.get('limit') or self._base_config.get('limit')
        if limit is None:
            raise KeyError("Missing 'limit' in both config and base_config")

        return limit

    def _get_timeout(self) -> int:
        timeout = self.config.get(
            'timeout') or self._base_config.get('timeout')
        if timeout is None:
            raise KeyError("Missing 'timeout' in both config and base_config")

        return timeout

    def _get_http_method(self) -> str:
        return self.config.get('http_method', 'GET')

    def _get_vendor_name(self) -> str:
        vendor_name = self.config.get('vendor_name')
        if vendor_name is None:
            raise KeyError(self._get_class_name() +
                           ": missing 'vendor_name' in config")

        return vendor_name

    def _get_auth_type(self) -> str:
        auth_type = self.config.get('auth_type')
        if auth_type is None:
            raise KeyError(self._get_class_name() +
                           ": missing 'auth_type' in config")

        return auth_type

    def _get_base_url(self) -> str:
        base_url = self.config.get('base_url')
        if base_url is None:
            raise KeyError(self._get_class_name() +
                           ": missing 'base_url' in config")

        return base_url

    def _get_endpoint(self) -> str:
        endpoint = self.config.get('endpoint')
        if endpoint is None:
            raise KeyError(self._get_class_name() +
                           ": missing 'endpoint' in config")

        return endpoint

    def _get_response_type(self) -> str:
        response_type = self.config.get('response_type')
        if response_type is None:
            raise KeyError(self._get_class_name() +
                           ": missing 'response_type' in config")

        return response_type

    def _get_dedup_before_insert(self) -> bool:
        return self.config.get('dedup_before_insert', 0) > 0

    @abstractmethod
    def _hydrate_request_params(self, data: Dict) -> Dict:
        """
        Returns hydrated dict of params for request
        """
        pass

    @abstractmethod
    def _hydrate(self, raw_data: Dict) -> BaseHydratedCollection:
        """
        Returns collection of hydrated entities
        """
        pass

    @abstractmethod
    def _paginate(self, request_params: Dict, raw_data: Dict) -> Dict:
        """
        Returns Dictionary containing next_page_request_params.
        """
        pass

    def _get_class_name(self) -> str:
        return self.__class__.__name__

    async def fetch_data(self, hydrated_request_params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Fetch data and return next_page_request_params.

        Returns:
            Dictionary containing next_page_request_params.
        """
        if hydrated_request_params is None:
            hydrated_request_params = self._hydrate_request_params({
                'limit': self._get_limit(),
                'offset': 0,
            })

        return await self._request_data(hydrated_request_params)

    async def _request_data(self, request_params: Dict) -> Dict:
        """
        Makes a request to vendor api and saves the result

        Returns Dictionary containing next_page_request_params.
        """
        raw_data = await self._get_requester().request(
            self.config['endpoint'],
            self.config.get('http_method', 'GET'),
            request_params,
        )
        if not raw_data:
            return None

        hydratedCollection = self._hydrate(raw_data)
        await hydratedCollection.save_to_db()

        return self._paginate(request_params, raw_data)

    def _normalize_dt(self, dt_str: str) -> Optional[datetime]:
        return fix_dt_for_db(dt_str)

    def _get_custom_requester(self) -> BaseRequester:
        raise NotImplementedError(
            self._get_class_name() + ' has no get_custom_requester() implemented'
        )

    def _create_rate_limiter_config(self) -> Dict[str, Any]:
        """
        Returns dict hydrated as RateLimiter config
        """
        config = {
            "vendor_name": self._get_vendor_name(),
            **self.config.get("rate_limit", {
                "requests_allowed": -1,
                "timeframe": 0
            }),
            **self.__rate_limit_data
        }

        return config

    def get_rate_limiter_data(self) -> Dict[str, Any]:
        """
        Returns RateLimiter data (config + requests_done, started_at)
        """
        return self._get_requester().get_rate_limiter_data()

    def _get_requester(self) -> BaseRequester:
        if not self.__requester:
            match self.config['auth_type']:
                case 'no_auth':
                    self.__requester = NoAuthRequester(
                        self._get_base_url(),
                        self._get_response_type(),
                        self._get_timeout(),
                        self._create_rate_limiter_config()
                    )

                case 'basic':
                    username = self.config.get('username')
                    password = self.config.get('password')
                    if username is None or password is None:
                        raise KeyError(
                            self._get_class_name() + ": missing username|password for basic auth_type"
                        )

                    self.__requester = BasicAuthRequester(
                        self._get_base_url(),
                        self._get_response_type(),
                        self._get_timeout(),
                        self._create_rate_limiter_config(),
                        username, password
                    )

                case 'token':
                    token = self.config.get('token')
                    if token is None:
                        raise KeyError(
                            self._get_class_name() + ": missing token for token|token_bearer auth_type"
                        )

                    self.__requester = TokenAuthRequester(
                        self._get_base_url(),
                        self._get_response_type(),
                        self._get_timeout(),
                        self._create_rate_limiter_config(),
                        token
                    )

                case 'token_bearer':
                    token = self.config.get('token')
                    if token is None:
                        raise KeyError(
                            self._get_class_name() + ": missing token for token|token_bearer auth_type"
                        )

                    self.__requester = TokenBearerAuthRequester(
                        self._get_base_url(),
                        self._get_response_type(),
                        self._get_timeout(),
                        self._create_rate_limiter_config(),
                        token
                    )

                case 'oauth':
                    token_url = self.config.get('token_url')
                    client_id = self.config.get('client_id')
                    client_secret = self.config.get('client_secret')
                    if token_url is None or client_id is None or client_secret is None:
                        raise KeyError(
                            self._get_class_name() + ": missing token_url|client_id|client_secret for oauth auth_type"
                        )

                    self.__requester = OAuthRequester(
                        self._get_base_url(),
                        self._get_response_type(),
                        self._get_timeout(),
                        self._create_rate_limiter_config(),
                        token_url,
                        client_id, client_secret,
                        self.config.get('scope')
                    )

                case _:
                    self.__requester = self._get_custom_requester()

        return self.__requester

    async def close_requester_session(self):
        return await self._get_requester().close_session()
