from app.db.celery import get_app

celery_app = get_app('test_tasks')


@celery_app.task
def add(x, y):
    return x + y


def test_enqueue():
    result = add.delay(1, 1)
    assert result.id is not None
