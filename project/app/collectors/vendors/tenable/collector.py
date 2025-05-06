from typing import Dict, Optional, Any

from ...base_collector import BaseCollector
from ...hydrated import BaseHydratedCollection, HydratedHostsCollection, HydratedHost


class Collector(BaseCollector):
    def _hydrate_request_params(self, data: Dict) -> Optional[Dict]:
        cursor_param = data.get('cursor', '')
        if not cursor_param:
            return None

        return {
            'cursor': cursor_param,
        }

    def _paginate(self, request_params, raw_data: Optional[Dict] = None) -> Optional[Dict]:
        if not len(raw_data.get('hosts')):
            return None

        cursor_param = raw_data.get('cursor')
        if not cursor_param:
            return None

        return {
            'cursor': cursor_param
        }

    def _hydrate(self, raw_data: Dict) -> BaseHydratedCollection:
        hostsList = []
        for raw_host in raw_data.get('hosts', []):
            hostsList.append(HydratedHost(
                self._get_vendor_name(),
                self.__get_ip(raw_host),
                raw_host.get('display_mac_address'),
                raw_host.get('display_operating_system'),
                '',
                raw_host.get('host_name'),
                self._normalize_dt(self.__get_first_seen(raw_host)),
                self._normalize_dt(self.__get_last_seen(raw_host)),

                raw_host
            ))

        return HydratedHostsCollection(
            hostsList,
            self._get_dedup_before_insert()
        )

    def __get_ip(self, raw_data: Dict[str, Any]) -> str:
        ipv6 = raw_data.get("display_ipv6_address")
        if ipv6:
            return ipv6

        ipv4 = raw_data.get("display_ipv4_address")
        if ipv4:
            return ipv4

        raise Exception("No ip data in Tenable collector")

    def __get_first_seen(self, raw_data: Dict[str, Any]) -> str:
        date_param = raw_data.get("first_observed", {}).get("$date")
        if not date_param:
            raise Exception("No first_seen data in Tenable collector")

        return date_param

    def __get_last_seen(self, raw_data: Dict[str, Any]) -> str:
        date_param = raw_data.get("last_observed", {}).get("$date")
        if not date_param:
            raise Exception("No last_seen data in Tenable collector")

        return date_param
