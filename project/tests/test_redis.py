from app.db.redis import get_db

db = get_db()


def test_write_and_read():
    # Write
    db.set("pytest_key", "hello")

    # Read
    value = db.get("pytest_key")

    assert value == b"hello"
