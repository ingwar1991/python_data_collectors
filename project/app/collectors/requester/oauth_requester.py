import requests
from .base_requester import BaseRequester


class OAuthRequester(BaseRequester):
    def __init__(self, base_url, response_type, timeoutInSeconds, token_url, client_id, client_secret, scope=None):
        super().__init__(base_url, response_type, timeoutInSeconds)

        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.access_token = None

    def authenticate(self):
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        if self.scope:
            data['scope'] = self.scope

        try:
            response = self.session.post(self.token_url, data=data)
            response.raise_for_status()
            token_info = response.json()
            self.access_token = token_info['access_token']
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}'
            })
            self.authenticated = True

        except requests.RequestException as e:
            raise RuntimeError(f"OAuth authentication failed: {e}")
