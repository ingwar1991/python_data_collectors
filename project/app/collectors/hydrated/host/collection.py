from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from typing import List, Dict, Any

from ..base_collection import BaseHydratedCollection
# from ....db.mongo import get_db_conn
from ....db.async_mongo import get_db_conn


class HydratedHostsCollection(BaseHydratedCollection):
    def _create_db_conn(self):
        return get_db_conn().hostsDiscovered

    async def _set_into_db(self):
        await self.__update_or_upsert_into_db(self._entities, True)

        return

    async def _update_existing_in_db(self):
        if not self.dup_len():
            return

        result = await self.__update_or_upsert_into_db(self._dup_entities, False)
        if result is None:
            raise RuntimeError(f"Failed to run update_existing query: {result} for {self._dup_entities}")
        if result.matched_count == 0:
            raise RuntimeError("No matching documents found for update.")

        return

    async def _get_existing_unique_ids_from_db(self) -> List[str]:
        unique_ids = [entity.unique_id for entity in self._entities]
        cursor = self._get_db_conn().find(
            {"unique_id": {"$in": unique_ids}},
            {"unique_id": 1, "_id": 0}
        )

        existing_ids = []
        async for doc in cursor:
            existing_ids.append(doc["unique_id"])

        return existing_ids

    async def _insert_new_in_db(self):
        if not self.len():
            return

        docs = [entity.to_dict() for entity in self._entities]
        try:
            result = await self._get_db_conn().insert_many(docs, ordered=False)
            if not result.acknowledged:
                raise RuntimeError("Insert not acknowledged by MongoDB")
        except BulkWriteError as err:
            raise RuntimeError(f"Bulk insert error: {err.details}")

    async def __update_or_upsert_into_db(self, entities: List[Dict[str, Any]], upsert: bool):
        if not len(entities):
            return

        update_operations = []
        for entity in entities:
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

        if update_operations:
            try:
                return await self._get_db_conn().bulk_write(update_operations, ordered=False)
            except BulkWriteError as err:
                raise RuntimeError(f"Bulk update operation failed: {err.details}")
