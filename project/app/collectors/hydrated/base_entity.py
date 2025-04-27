from abc import ABC, abstractmethod
import inspect
from typing import Dict, List, Any


class BaseHydratedEntity(ABC):
    def __init__(self, raw_data: Dict):
        self.raw_data = raw_data

        self.__validate()
        self.unique_id = self._generate_unique_id()

    @abstractmethod
    def _generate_unique_id(self) -> str:
        pass

    def _sanitize_raw_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        return raw_data

    def to_dict(self) -> Dict[str, Any]:
        entDict = self.__dict__
        entDict["raw_data"] = self._sanitize_raw_data(entDict)

        return entDict

    def _get_class_name(self) -> str:
        return self.__class__.__name__

    @classmethod
    def _get_required_fields(cls) -> List[str]:
        sig = inspect.signature(cls.__init__)

        return [
            param.name for param in sig.parameters.values()
            if param.name != 'self' and param.name != 'raw_data'
            and param.kind in (param.POSITIONAL_OR_KEYWORD,)
            and param.default is param.empty
        ]

    def __validate(self):
        """
        Check if any of the required fields are missing
        """
        missingField = [field for field in self._get_required_fields() if getattr(self, field) is None]
        if missingField:
            raise ValueError(f"{self._get_class_name()}: missing required fields: {', '.join(missingField)}")
