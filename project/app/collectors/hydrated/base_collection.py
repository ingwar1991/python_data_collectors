from abc import ABC, abstractmethod
from typing import List

from .base_entity import BaseHydratedEntity


class BaseHydratedCollection(ABC):
    def __init__(self, entities: list[BaseHydratedEntity], dedup_before_insert: bool = False):
        self._entities = entities

        self._dedup_before_insert = dedup_before_insert
        self._is_deduped = False
        self._dup_entities: list[BaseHydratedEntity] = []

        self._db_conn = None

    def _get_db_conn(self):
        if self._db_conn is None:
            self._db_conn = self._create_db_conn()

        return self._db_conn

    @abstractmethod
    def _create_db_conn(self):
        pass

    @abstractmethod
    async def _set_into_db(self):
        pass

    # the next 3 methods will be required
    # only if dedup_before_insert will be in place
    # thus instead of making them abstract they are just empty
    # in order not to force to create unused methods

    async def _get_existing_unique_ids_from_db(self) -> List[str]:
        return []

    async def _insert_new_in_db(self):
        return

    async def _update_existing_in_db(self):
        return

    def len(self) -> int:
        return len(self._entities)

    def dup_len(self) -> int:
        return len(self._dup_entities)

    async def save_to_db(self):
        if not self._dedup_before_insert:
            await self._set_into_db()

            return

        await self._dedup()

        await self._insert_new_in_db()
        await self._update_existing_in_db()

    async def _dedup(self):
        if self._is_deduped:
            return

        new_entities = []
        dup_entities = []

        existing_unique_ids = await self._get_existing_unique_ids_from_db()
        for entity in self._entities:
            if entity.unique_id in existing_unique_ids:
                dup_entities.append(entity)
            else:
                new_entities.append(entity)

        self._is_deduped = True
        self._entities = new_entities
        self._dup_entities = dup_entities
