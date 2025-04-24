from datetime import datetime, timezone
from dateutil import parser
from pymongo import MongoClient, database
from typing import Optional
import os


def get_db_client() -> MongoClient:
    dbName = os.environ.get("MONGO_DB_NAME")
    dbPort = os.environ.get("MONGO_PORT")
    dbUser = os.environ.get("MONGO_USER")
    dbUserPass = os.environ.get("MONGO_USER_PASS")

    mongo_uri = f"mongodb://{dbUser}:{dbUserPass}@data_collectors_mongo:{dbPort}/{dbName}?authSource={dbName}"

    return MongoClient(mongo_uri)


def get_db_conn() -> database.Database:
    return get_db_client().get_database()


def fix_dt_for_db(dt_str: str) -> Optional[datetime]:
    try:
        dt = parser.parse(dt_str)

        if dt.tzinfo:
            dt = dt.astimezone(timezone.utc)
        else:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt

    except (ValueError, TypeError) as e:
        print(f"Failed to parse datetime string: {dt_str} — {e}")
        return None
