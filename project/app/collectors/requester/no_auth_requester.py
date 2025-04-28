from typing import Dict, Any

from .base_requester import BaseRequester


class NoAuthRequester(BaseRequester):
    def __init__(
        self,
        base_url: str, response_type: str, timeout_in_seconds: int,
        rate_limit_config: Dict[str, Any],
    ):
        super().__init__(base_url, response_type, timeout_in_seconds, rate_limit_config)

    async def authenticate(self):
        return
