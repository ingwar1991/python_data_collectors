from requests.auth import HTTPBasicAuth
from .base_requester import BaseRequester


class BasicAuthRequester(BaseRequester):
    def __init__(self, base_url, response_type, timeoutInSeconds, username, password):
        super().__init__(base_url, response_type, timeoutInSeconds)

        self.username = username
        self.password = password

    def authenticate(self):
        self.session.auth = HTTPBasicAuth(self.username, self.password)
        self.authenticated = True
