import hashlib
from datetime import datetime
from ..base_entity import BaseHydratedEntity


class HydratedHost(BaseHydratedEntity):
    def __init__(
            self, source: str,
            ip: str, mac: str,
            os: str, os_version:
            str, name: str,
            first_seen: datetime, last_seen: datetime,
            raw_data
    ):
        self.source = source

        self.ip = ip
        self.mac = mac
        self.os = os
        self.os_version = os_version
        self.name = name
        self.first_seen = first_seen
        self.last_seen = last_seen

        super().__init__(raw_data)

    def _generate_unique_id(self) -> str:
        # keeping the same hosts, but from different vendors
        raw = (self.source + self.ip + self.mac).encode('utf-8')

        return hashlib.sha256(raw).hexdigest()
