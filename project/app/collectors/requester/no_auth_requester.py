from .base_requester import BaseRequester


class NoAuthRequester(BaseRequester):
    def __init__(self, base_url, response_type, timeoutInSeconds):
        super().__init__(base_url, response_type, timeoutInSeconds)

    def authenticate(self):
        return
