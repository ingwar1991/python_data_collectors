from .base_requester import BaseRequester


class TokenAuthRequester(BaseRequester):
    def __init__(self, base_url, response_type, timeoutInSeconds, token):
        super().__init__(base_url, response_type, timeoutInSeconds)

        self.token = token

    def authenticate(self):
        self.session.headers.update({
            'token': self.token
        })

        self.authenticated = True
