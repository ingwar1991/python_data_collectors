from typing import Optional
from celery import Celery


def get_app(db_name: Optional[str] = None) -> Celery:
    """
    Returns a Celery app instance connected to Redis as the broker.
    The optional `db_name` defaul value is `collector_tasks`
    """
    return Celery('collector_tasks', broker='redis://data_collectors_redis:6379/0')
