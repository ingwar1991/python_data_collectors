import pytest
from app.collectors.requester.rate_limiter import RateLimitMissingAttributeException, RateLimitLimitReachedException, RateLimiter


def test_rate_limiter_initialization_valid():
    rl = RateLimiter("test_vendor", 5, 10)
    assert rl.to_dict()["vendor_name"] == "test_vendor"


def test_rate_limiter_missing_vendor_name():
    with pytest.raises(RateLimitMissingAttributeException) as exc:
        RateLimiter("", 5, 10)
    assert "vendor_name" in str(exc.value)


def test_rate_limiter_missing_requests_allowed():
    with pytest.raises(RateLimitMissingAttributeException) as exc:
        RateLimiter("test_vendor", 0, 10)
    assert "requests_allowed" in str(exc.value)


def test_rate_limiter_missing_timeframe():
    with pytest.raises(RateLimitMissingAttributeException) as exc:
        RateLimiter("test_vendor", 5, 0)
    assert "timeframe" in str(exc.value)


def test_rate_limiter_no_limit():
    rl = RateLimiter("test_vendor", -1, 0)
    # Should not raise anything
    for _ in range(100):
        rl.check()


def test_rate_limiter_respects_limit():
    rl = RateLimiter("test_vendor", 2, 10)
    rl.check()
    rl.check()

    with pytest.raises(RateLimitLimitReachedException) as exc:
        rl.check()  # 3rd call, should raise

    assert isinstance(exc.value.seconds_until_next_timeframe(), int)
    assert exc.value.seconds_until_next_timeframe() > 0


def test_rate_limiter_resets_after_timeframe():
    rl = RateLimiter("test_vendor", 1, 1)
    rl.check()

    with pytest.raises(RateLimitLimitReachedException):
        rl.check()  # 2nd call, should raise

    rl.check()  # Should reset and pass
