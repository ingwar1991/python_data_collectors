import requests
from typing import Dict, Any

from .base_requester import BaseRequester


class OAuthRequester(BaseRequester):
    def __init__(
        self,
        base_url: str, response_type: str, timeoutInSeconds: int,
        rate_limit_config: Dict[str, Any],
        token_url: str, client_id: str, client_secret: str, scope: str = None
    ):
        super().__init__(base_url, response_type, timeoutInSeconds, rate_limit_config)

        self.__token_url = token_url
        self.__client_id = client_id
        self.__client_secret = client_secret
        self.__scope = scope
        self.__access_token = None

    def authenticate(self):
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.__client_id,
            'client_secret': self.__client_secret,
        }

        if self.__scope:
            data['scope'] = self.__scope

        try:
            response = self._session.post(self.__token_url, data=data)
            response.raise_for_status()
            token_info = response.json()
            self.__access_token = token_info['access_token']
            self._session.headers.update({
                'Authorization': f'Bearer {self.__access_token}'
            })
            self.authenticated = True

        except requests.RequestException as e:
            raise RuntimeError(f"OAuth authentication failed: {e}")
