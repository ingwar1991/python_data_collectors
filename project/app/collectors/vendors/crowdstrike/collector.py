from typing import Dict, Optional

from ...base_collector import BaseCollector
from ...hydrated import BaseHydratedCollection, HydratedHostsCollection, HydratedHost


class Collector(BaseCollector):
    def _hydrate_request_params(self, data: Dict) -> Dict:
        return {
            'limit': data['limit'],
            'skip': data['offset'],
        }

    def _paginate(self, request_params, raw_data: Optional[Dict] = None) -> Dict:
        hosts_collection = self._hydrate(raw_data)
        if hosts_collection.len() < request_params['limit']:
            return None

        request_params['skip'] += request_params['limit']
        return request_params

    def _hydrate(self, raw_data: Dict) -> BaseHydratedCollection:
        hostsList = []
        for raw_host in raw_data:
            hostsList.append(HydratedHost(
                self._get_vendor_name(),
                raw_host.get('external_ip'),
                self.__get_mac_addr(raw_host),
                raw_host.get('platform_name'),
                raw_host.get('os_version'),
                raw_host.get('hostname'),
                self._normalize_dt(raw_host.get('first_seen')),
                self._normalize_dt(raw_host.get('last_seen')),

                raw_host
            ))

        return HydratedHostsCollection(hostsList)

    def __get_mac_addr(self, raw_data: Dict) -> str:
        mac_addr = raw_data.get('mac_address')
        if not mac_addr:
            return None

        return mac_addr.lower().replace("-", ":")
