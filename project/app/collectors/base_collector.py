from abc import ABC, abstractmethod
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from .requester import NoAuthRequester, BasicAuthRequester, TokenAuthRequester, TokenBearerAuthRequester, OAuthRequester
from ..db.mongo import fix_dt_for_db
from .hydrated.base_collection import BaseHydratedCollection


class BaseCollector(ABC):
    def __init__(self, config):
        self.config = config

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

    def fetch_data(self, hydrated_request_params: Optional[Dict] = None) -> Dict:
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

        return self._request_data(hydrated_request_params)

    def _request_data(self, request_params: Dict) -> Dict:
        """
        Returns Dictionary containing next_page_request_params.
        """
        raw_data = self._get_requester().request(
            self.config['endpoint'],
            self.config.get('http_method', 'GET'),
            request_params,
        )
        if not raw_data:
            return None

        self._hydrate(raw_data).save_to_db()

        return self._paginate(request_params, raw_data)

    def _normalize_dt(self, dt_str: str) -> Optional[datetime]:
        return fix_dt_for_db(dt_str)

    def _get_custom_requester(self) -> BasicAuthRequester:
        raise NotImplementedError(
            self._get_class_name() + ' has no get_custom_requester() implemented'
        )

    def _get_requester(self) -> BasicAuthRequester:
        match self.config['auth_type']:
            case 'no_oauth':
                return NoAuthRequester(
                    self._get_base_url(),
                    self._get_response_type(),
                    self._get_timeout(),
                )

            case 'basic':
                username = self.config.get('username')
                password = self.config.get('password')
                if username is None or password is None:
                    raise KeyError(
                        self._get_class_name() + ": missing username|password for basic auth_type"
                    )

                return BasicAuthRequester(
                    self._get_base_url(),
                    self._get_response_type(),
                    self._get_timeout(),
                    username, password
                )

            case 'token_bearer' | 'token':
                token = self.config.get('token')
                if token is None:
                    raise KeyError(
                        self._get_class_name() + ": missing token for token|token_bearer auth_type"
                    )

                return TokenAuthRequester(
                    self._get_base_url(),
                    self._get_response_type(),
                    self._get_timeout(),
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

                return OAuthRequester(
                    self._get_base_url(),
                    self._get_response_type(),
                    self._get_timeout(),
                    token_url,
                    client_id, client_secret,
                    self.config.get('scope')
                )

            case _:
                return self._get_custom_requester()
