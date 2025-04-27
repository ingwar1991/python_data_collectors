import time

from .worker import run_job, JobData
from .utils import get_vendor_names, read_yaml


def register_job(collector_type: str, job_data: JobData = None):
    job_data_dict = job_data.to_dict() if job_data is not None else None
    job = run_job.delay(collector_type, job_data_dict)

    print(f"Job queued: {job.id}, {collector_type}, {job_data_dict}")


def register_all_jobs():
    for vendor_name in get_vendor_names():
        register_job(vendor_name)


if __name__ == "__main__":
    print("Scheduling jobs...")

    base_config = read_yaml()
    # tf in minutes in which jobs will be scheduled, default 5
    interval_min = base_config.get("scheduler_tf", "5")

    while True:
        register_all_jobs()

        time.sleep(interval_min * 60)
