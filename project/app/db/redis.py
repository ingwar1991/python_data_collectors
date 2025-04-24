from redis import Redis


def get_db() -> Redis:
    return Redis(host="data_collectors_redis", port=6379, db=0)
