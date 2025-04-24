from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from typing import List

from ..base_collection import BaseHydratedCollection
from ....db.mongo import get_db_conn


class HydratedHostsCollection(BaseHydratedCollection):
    def _get_db_conn(self):
        return get_db_conn().hostsDiscovered

    def _get_existing_unique_ids_from_db(self) -> List[str]:
        unique_ids = [entity.unique_id for entity in self._entities]
        cursor = self._db_conn.find(
            {"unique_id": {"$in": unique_ids}},
            {"unique_id": 1, "_id": 0}
        )

        return [entity["unique_id"] for entity in cursor]

    def _insert_new_in_db(self):
        if not len(self._entities):
            return

        docs = [entity.to_dict() for entity in self._entities]
        try:
            result = self._db_conn.insert_many(docs, ordered=False)
            if not result.acknowledged:
                raise RuntimeError("Insert not acknowledged by MongoDB")
        except BulkWriteError as err:
            raise RuntimeError(f"Bulk insert error: {err.details}")

    def _update_existing_in_db(self):
        if not self._entities:
            return

        update_operations = []

        for entity in self._entities:
            update_operations.append(
                UpdateOne(
                    {"unique_id": entity.unique_id},
                    {"$set": entity.to_dict()}
                )
            )

        try:
            if update_operations:
                result = self._db_conn.bulk_write(update_operations, ordered=False)

                if result.matched_count == 0:
                    raise RuntimeError("No matching documents found for update.")
        except BulkWriteError as err:
            raise RuntimeError(f"Bulk update operation failed: {err.details}")
