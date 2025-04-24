from pymongo import ASCENDING, DESCENDING
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Any

from ..db.mongo import get_db_conn

db_collection = get_db_conn().hostsDiscovered


def _get_raw_data(request_params: Optional[Dict] = None) -> List[Dict[str, Any]]:
    query, sort = _build_query_and_sort(request_params)

    stmt = db_collection.find(query, {"_id": 0})
    if sort:
        stmt.sort(sort)

    return list(stmt)


def _get_grouped_data(request_params: Optional[Dict] = None) -> List[Dict[str, Any]]:
    pipeline = [
        {
            "$group": {
                "_id": {"ip": "$ip", "mac": "$mac"},
                "ip": {"$first": "$ip"},
                "mac": {"$first": "$mac"},
                "source_list": {"$addToSet": "$source"},
                "os_list": {"$addToSet": "$os"},
                "os_version_list": {"$addToSet": "$os_version"},
                "name_list": {"$addToSet": "$name"},
                "first_seen": {"$min": "$first_seen"},
                "last_seen": {"$max": "$last_seen"},
                "raw_data": {"$push": "$raw_data"}
            }
        }
    ]

    query, sort = _build_query_and_sort(request_params)

    if query:
        pipeline.append({"$match": query})

    if sort is not None:
        field, direction = sort[0]
        pipeline.append({"$sort": {field: direction}})

    return list(db_collection.aggregate(pipeline))


def _build_query_and_sort(request_params: Optional[Dict] = None) -> Tuple[Dict, Optional[list]]:
    query = {}
    sort = None
    if not request_params:
        return query, sort

    # Exact match
    if request_params.get("source"):
        query["source"] = request_params["source"]

    # Partial match for string fields
    for field in ["ip", "mac", "os", "os_version", "name"]:
        value = request_params.get(field)
        if value:
            query[field] = {"$regex": value, "$options": "i"}  # case-insensitive partial match

    # Date range filtering
    if request_params.get("first_seen"):
        try:
            query["first_seen"] = {
                "$gte": datetime.fromisoformat(request_params["first_seen"])
            }
        except ValueError:
            print(f"Wrong date format at first_seen: {request_params['first_seen']}")

    if request_params.get("last_seen"):
        try:
            query["last_seen"] = {
                "$lte": datetime.fromisoformat(request_params["last_seen"])
            }
        except ValueError:
            print(f"Wrong date format at last_seen: {request_params['last_seen']}")

    # Sorting
    order_by = request_params.get("order_by")
    if order_by:
        direction = ASCENDING if request_params.get("order_dir", "asc") == "asc" else DESCENDING
        sort = [(order_by, direction)]

    return query, sort
