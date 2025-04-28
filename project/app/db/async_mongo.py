from datetime import datetime, timezone
from dateutil import parser
from typing import Optional
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


def get_db_client() -> AsyncIOMotorClient:
    db_name = os.environ.get("MONGO_DB_NAME")
    db_port = os.environ.get("MONGO_PORT")
    db_user = os.environ.get("MONGO_USER")
    db_pass = os.environ.get("MONGO_USER_PASS")

    mongo_uri = f"mongodb://{db_user}:{db_pass}@data_collectors_mongo:{db_port}/{db_name}?authSource={db_name}"

    return AsyncIOMotorClient(mongo_uri)


def get_db_conn() -> AsyncIOMotorDatabase:
    db_name = os.environ.get("MONGO_DB_NAME")

    return get_db_client()[db_name]


# Full copy of app.db.mongo.fix_dt_for_db
# didn't want to raise any confusion by importing
# from both sync & async packages
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
