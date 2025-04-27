from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from typing import List, Dict, Any

from ..base_collection import BaseHydratedCollection
from ....db.mongo import get_db_conn


class HydratedHostsCollection(BaseHydratedCollection):
    def _get_db_conn(self):
        return get_db_conn().hostsDiscovered

    def _set_into_db(self):
        self.__update_or_upsert_into_db(self._entities, True)

        return

    def _update_existing_in_db(self):
        if not self.dup_len():
            return

        result = self.__update_or_upsert_into_db(self._dup_entities, False)
        if result.matched_count == 0:
            raise RuntimeError("No matching documents found for update.")

        return

    def _get_existing_unique_ids_from_db(self) -> List[str]:
        unique_ids = [entity.unique_id for entity in self._entities]
        cursor = self._db_conn.find(
            {"unique_id": {"$in": unique_ids}},
            {"unique_id": 1, "_id": 0}
        )

        return [entity["unique_id"] for entity in cursor]

    def _insert_new_in_db(self):
        if not self.len():
            return

        docs = [entity.to_dict() for entity in self._entities]
        try:
            result = self._db_conn.insert_many(docs, ordered=False)
            if not result.acknowledged:
                raise RuntimeError("Insert not acknowledged by MongoDB")
        except BulkWriteError as err:
            raise RuntimeError(f"Bulk insert error: {err.details}")

    def __update_or_upsert_into_db(self, entities: List[Dict[str, Any]], upsert: bool):
        if not len(entities):
            return

        update_operations = []
        for entity in self._entities:
            entityDict = entity.to_dict()

            update_operations.append(
                UpdateOne(
                    {"unique_id": entityDict["unique_id"]},
                    [{
                        "$set": {
                            # update last_seen if in new doc it is later, than the saved one
                            "last_seen": {
                                "$cond": [
                                    {"$gt": [entityDict["last_seen"], "$last_seen"]},
                                    entityDict["last_seen"],
                                    "$last_seen"
                                ]
                            },

                            # update raw_data if in new doc last_seen is later, than the saved one
                            "raw_data": {
                                "$cond": [
                                    {"$gt": [entityDict["last_seen"], "$last_seen"]},
                                    entityDict["raw_data"],
                                    "$raw_data"
                                ]
                            },

                            # because we might have upsert=True here we need to specify all required fields
                            "source": {"$ifNull": ["$source", entityDict["source"]]},
                            "ip": {"$ifNull": ["$ip", entityDict["ip"]]},
                            "mac": {"$ifNull": ["$mac", entityDict["mac"]]},
                            "os": {"$ifNull": ["$os", entityDict["os"]]},
                            "os_version": {"$ifNull": ["$os_version", entityDict["os_version"]]},
                            "name": {"$ifNull": ["$name", entityDict["name"]]},
                            "first_seen": {"$ifNull": ["$first_seen", entityDict["first_seen"]]}
                        }
                    }],
                    upsert=upsert
                )
            )

        try:
            if update_operations:
                return self._db_conn.bulk_write(update_operations, ordered=False)
        except BulkWriteError as err:
            raise RuntimeError(f"Bulk update operation failed: {err.details}")
