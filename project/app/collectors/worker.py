import traceback
from typing import Dict, Any

from ..db.celery import get_app
from .utils import create_collector

celery_app = get_app()


class JobData():
    def __init__(self, rate_limit_data: Dict[str, Any] = None, request_params: Dict[str, Any] = None):
        self.rate_limit_data = rate_limit_data
        self.request_params = request_params

    def to_dict(self):
        return self.__dict__


@celery_app.task
def run_job(collector_type: str, job_data_dict: Dict[str, Any] = None):
    # including with lazy to avoid dependency chain
    from .register_jobs import register_job

    job_data_dict = job_data_dict if job_data_dict is not None else {}
    job_data = JobData(**job_data_dict)
    print(f"Found job: {collector_type} with {job_data.to_dict()}")

    try:
        collector_instance = create_collector(collector_type, job_data.rate_limit_data)
        print("\tRunning collector")

        next_page_params = collector_instance.fetch_data(job_data.request_params)

        if next_page_params is not None:
            job_data.request_params = next_page_params
            job_data.rate_limit_data = collector_instance.get_rate_limiter_data()

            register_job(collector_type, job_data)

    except Exception as e:
        print(f"\t\tFailed to run collector's fetch_data(): {e}")
        traceback.print_exc()
