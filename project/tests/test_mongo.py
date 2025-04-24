import pytest
from pymongo import UpdateOne
from pymongo.errors import PyMongoError

from app.db.mongo import get_db_client, get_db_conn, fix_dt_for_db


@pytest.fixture(scope="module")
def db():
    collection = get_db_conn().hostsDiscovered
    yield collection


@pytest.fixture(scope="module", autouse=True)
def global_test_cleanup(request, db):
    def cleanup():
        unique_ids = [
            "tst_uniqid_1",
            "tst_uniqid_2",
            "tst_uniqid_3",
        ]

        db.delete_many({"unique_id": {"$in": unique_ids}})
        print("[Test Cleanup] Deleted test entries by unique_id")

    request.addfinalizer(cleanup)


def test_db_connection():
    client = get_db_client()

    try:
        client.admin.command('ping')
        print("MongoDB connection successful!")
    except PyMongoError:
        pytest.fail("MongoDB connection failed!")
    finally:
        client.close()


def test_insert_single_document(db):
    doc = {
        "unique_id": "tst_uniqid_1",
        "source": "test",
        "ip": "127.0.0.1", "mac": "12-5e-2e-db-58-aa",
        "os": "linux", "os_version": "ubuntu",
        "name": "tst1",
        "first_seen": fix_dt_for_db("2023-07-25T19:10:00Z"), "last_seen": fix_dt_for_db("2023-07-25T20:15:00Z")
    }

    try:
        result = db.insert_one(doc)
        assert result.inserted_id is not None
    except Exception as e:
        print(f"Failed to insert doc: {e}")
        pytest.fail(f"Failed to insert doc: {e}")


def test_read_one_document(db):
    fetched_document = db.find_one({"unique_id": "tst_uniqid_1"})

    assert fetched_document is not None
    assert fetched_document["ip"] == "127.0.0.1"
    assert fetched_document["mac"] == "12-5e-2e-db-58-aa"
    assert fetched_document["name"] == "tst1"


def test_bulk_insert_with_duplicates(db):
    data_to_insert = [
        {
            "unique_id": "tst_uniqid_1",
            "source": "test",
            "ip": "127.0.0.1", "mac": "12-5e-2e-db-58-aa", 
            "os": "linux", "os_version": "ubuntu",
            "name": "tst4",
            "first_seen": fix_dt_for_db("2023-07-25T19:10:00Z"), "last_seen": fix_dt_for_db("2023-07-25T20:15:00Z")
        },
        {
            "unique_id": "tst_uniqid_2",
            "source": "test",
            "ip": "127.0.0.2", "mac": "12-5e-2e-db-58-bb", 
            "os": "linux", "os_version": "ubuntu",
            "name": "tst2",
            "first_seen": fix_dt_for_db("2023-07-25T19:10:10Z"), "last_seen": fix_dt_for_db("2023-07-25T20:15:10Z")
        },
        {
            "unique_id": "tst_uniqid_3",
            "source": "test",
            "ip": "127.0.0.3", "mac": "12-5e-2e-db-58-cc", 
            "os": "linux", "os_version": "ubuntu",
            "name": "tst3",
            "first_seen": fix_dt_for_db("2023-07-25T19:10:20Z"), "last_seen": fix_dt_for_db("2023-07-25T20:15:20Z")
        },
    ]

    operations = [
        UpdateOne(
            {"unique_id": item["unique_id"]},
            {"$set": item},
            upsert=True
        ) for item in data_to_insert
    ]

    # ordered=false continues processing even after some of the operations fail
    result = db.bulk_write(operations, ordered=False)

    assert result.upserted_count == 2
    assert result.matched_count == 1
    assert result.modified_count == 1


def test_read_multiple_documents(db):
    fetched_docs = list(db.find({"unique_id": {"$in": [
        "tst_uniqid_1",
        "tst_uniqid_2",
        "tst_uniqid_3"
    ]}}))
    assert len(fetched_docs) == 3

    fetched_by_id = {doc["unique_id"]: doc for doc in fetched_docs}

    assert fetched_by_id["tst_uniqid_1"]["ip"] == "127.0.0.1"
    assert fetched_by_id["tst_uniqid_1"]["name"] == "tst4"

    assert fetched_by_id["tst_uniqid_2"]["ip"] == "127.0.0.2"

    assert fetched_by_id["tst_uniqid_3"]["ip"] == "127.0.0.3"
