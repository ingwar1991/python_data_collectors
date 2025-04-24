import traceback

from ..db.celery import get_app
from .utils import create_collector

celery_app = get_app()


@celery_app.task
def run_job(collector_type: str, params: dict):
    # including with lazy to avoid dependency chain
    from .register_jobs import register_job

    print(f"Found job: {collector_type} with {params}")
    try:
        collector_instance = create_collector(collector_type)
        print("\trunning collector")

        next_page_params = collector_instance.fetch_data(params)

        if next_page_params is not None:
            register_job(collector_type, next_page_params)

    except Exception as e:
        print(f"\tfailed to build collector: {e}")
        traceback.print_exc()
