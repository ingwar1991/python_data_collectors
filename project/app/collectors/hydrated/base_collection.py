from abc import ABC, abstractmethod
from typing import List

from .base_entity import BaseHydratedEntity


class BaseHydratedCollection(ABC):
    def __init__(self, entities: list[BaseHydratedEntity]):
        self._entities = entities

        self._is_deduped = False
        self._dup_entities: list[BaseHydratedEntity] = []

        self._db_conn = self._get_db_conn()

    @abstractmethod
    def _get_db_conn(self):
        pass

    @abstractmethod
    def _get_existing_unique_ids_from_db(self) -> List[str]:
        pass

    @abstractmethod
    def _insert_new_in_db(self):
        pass

    def len(self) -> int:
        return len(self._entities)

    def dup_len(self) -> int:
        return len(self._dup_entities)

    # some cases won't need that at all
    # thus the method is empty instead of abstract
    def _update_existing_in_db(self):
        return

    def save_to_db(self):
        self._dedup()

        self._insert_new_in_db()
        self._update_existing_in_db()

    def _dedup(self):
        if self._is_deduped:
            return

        new_entities = []
        dup_entities = []

        existing_unique_ids = self._get_existing_unique_ids_from_db()
        for entity in self._entities:
            if entity.unique_id in existing_unique_ids:
                dup_entities.append(entity)
            else:
                new_entities.append(entity)

        self._is_deduped = True
        self._entities = new_entities
        self._dup_entities = dup_entities
