import time


class RateLimitMissingAttributeException(AttributeError):
    def __init__(self, attr_name: str):
        super().__init__(f"RateLimiter is missing `{attr_name}` attribute")


class RateLimitLimitReachedException(Exception):
    def __init__(self, message, seconds_until_next_timeframe: int):
        super().__init__(message)

        self.__seconds_until_next_timeframe = seconds_until_next_timeframe

    def seconds_until_next_timeframe(self):
        return self.__seconds_until_next_timeframe


class RateLimiter():
    def __init__(
        self,
        vendor_name: str,
        requests_allowed: int, timeframe: int = 0,
        requests_done: int = 0, started_at: int = 0
    ):
        self.__vendor_name = vendor_name

        self.__requests_allowed = requests_allowed
        self.__timeframe = timeframe

        self.__requests_done = requests_done
        self.__started_at = started_at

        self.__validate()

    def __validate(self):
        if not self.__vendor_name:
            raise RateLimitMissingAttributeException("vendor_name")

        if not self.__requests_allowed:
            raise RateLimitMissingAttributeException("requests_allowed")

        # requests_allowed == -1 means there's no rate limit
        if self.__requests_allowed != -1 and not self.__timeframe:
            raise RateLimitMissingAttributeException("timeframe")

    def to_dict(self):
        return {
            "vendor_name": self.__vendor_name,

            "requests_allowed": self.__requests_allowed,
            "timeframe": self.__timeframe,

            "requests_done": self.__requests_done,
            "started_at": self.__started_at,
        }

    def __unix_now_in_seconds(self):
        return int(time.time())

    def __reset(self):
        self.__requests_done = 0
        self.__started_at = self.__unix_now_in_seconds()

    def __timeframe_passed(self):
        return self.__started_at + self.__timeframe < self.__unix_now_in_seconds()

    def __check__timeframe(self):
        if self.__started_at == 0 or self.__timeframe_passed():
            self.__reset()

    def get_seconds_until_next_tf(self):
        seconds_until_next_tf = int(self.__timeframe - (time.time() - self.__started_at))

        return seconds_until_next_tf if seconds_until_next_tf > 0 else 1

    def check(self):
        # if request_allowed == -1, then there's no rate limit
        if self.__requests_allowed == -1:
            return

        self.__check__timeframe()

        self.__requests_done += 1
        if self.__requests_done > self.__requests_allowed:
            seconds_until_next_tf = self.get_seconds_until_next_tf()
            self.__reset()
            raise RateLimitLimitReachedException(
                f"Rate limit reached: {self.to_dict()}\n\tCurrent timeframe ends in {seconds_until_next_tf} seconds",
                seconds_until_next_tf
            )
