import pytest
from pymongo import UpdateOne
from pymongo.errors import PyMongoError
from datetime import datetime, timedelta

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


def test_read_one_document_after_single_insert(db):
    fetched_document = db.find_one({"unique_id": "tst_uniqid_1"})

    assert fetched_document is not None
    assert fetched_document["ip"] == "127.0.0.1"
    assert fetched_document["mac"] == "12-5e-2e-db-58-aa"
    assert fetched_document["name"] == "tst1"


bulk_entities_to_insert = [
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


def test_bulk_insert_with_duplicates(db):
    operations = [
        UpdateOne(
            {"unique_id": item["unique_id"]},
            {"$set": item},
            upsert=True
        ) for item in bulk_entities_to_insert
    ]

    # ordered=false continues processing even after some of the operations fail
    result = db.bulk_write(operations, ordered=False)

    assert result.upserted_count == 2
    assert result.matched_count == 1
    assert result.modified_count == 1


def test_read_multiple_documents_after_bulk_insert(db):
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


def test_bulk_insert_with_duplicates_update_by_date(db):
    bulk_entities_to_insert_upd = bulk_entities_to_insert
    for key, ent in enumerate(bulk_entities_to_insert_upd):
        ent["name"] += " updated"
        ent["first_seen"] = ent["first_seen"] - timedelta(days=1)
        ent["last_seen"] = ent["last_seen"] + timedelta(days=1)

        bulk_entities_to_insert_upd[key] = ent

    operations = [
        UpdateOne(
            {"unique_id": ent["unique_id"]},
            [{
                "$set": {
                    "last_seen": {
                        "$cond": [
                            {"$gt": [ent["last_seen"], "$last_seen"]},
                            ent["last_seen"],
                            "$last_seen"
                        ]
                    },
                    "name": {
                        "$cond": [
                            {"$gt": [ent["last_seen"], "$last_seen"]},
                            ent["name"],
                            "$name"
                        ]
                    },
                    "first_seen": {
                        "$cond": [
                            {"$lt": [ent["first_seen"], "$first_seen"]},
                            ent["first_seen"],
                            "$first_seen"
                        ]
                    }
                }
            }],
            upsert=True
        ) for ent in bulk_entities_to_insert_upd
    ]

    result = db.bulk_write(operations, ordered=False)

    assert result.upserted_count == 0
    assert result.matched_count == 3
    assert result.modified_count == 3


def test_read_multiple_documents_after_bulk_insert_update_by_date(db):
    fetched_docs = list(db.find({"unique_id": {"$in": [
        "tst_uniqid_1",
        "tst_uniqid_2",
        "tst_uniqid_3"
    ]}}))
    assert len(fetched_docs) == 3

    fetched_by_id = {doc["unique_id"]: doc for doc in fetched_docs}

    assert fetched_by_id["tst_uniqid_1"]["name"] == "tst4 updated"
    assert fetched_by_id["tst_uniqid_1"]["first_seen"].strftime("%Y-%m-%dT%H:%M:%SZ") == "2023-07-24T19:10:00Z"
    assert fetched_by_id["tst_uniqid_1"]["last_seen"].strftime("%Y-%m-%dT%H:%M:%SZ") == "2023-07-26T20:15:00Z"

    assert fetched_by_id["tst_uniqid_2"]["name"] == "tst2 updated"
    assert fetched_by_id["tst_uniqid_2"]["first_seen"].strftime("%Y-%m-%dT%H:%M:%SZ") == "2023-07-24T19:10:10Z"
    assert fetched_by_id["tst_uniqid_2"]["last_seen"].strftime("%Y-%m-%dT%H:%M:%SZ") == "2023-07-26T20:15:10Z"

    assert fetched_by_id["tst_uniqid_3"]["name"] == "tst3 updated"
    assert fetched_by_id["tst_uniqid_3"]["first_seen"].strftime("%Y-%m-%dT%H:%M:%SZ") == "2023-07-24T19:10:20Z"
    assert fetched_by_id["tst_uniqid_3"]["last_seen"].strftime("%Y-%m-%dT%H:%M:%SZ") == "2023-07-26T20:15:20Z"
