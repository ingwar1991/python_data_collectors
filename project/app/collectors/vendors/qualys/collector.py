from typing import Dict, Optional

from ...base_collector import BaseCollector
from ...hydrated import BaseHydratedCollection, HydratedHostsCollection, HydratedHost


class Collector(BaseCollector):
    def _hydrate_request_params(self, data: Dict) -> Dict:
        return {
            'limit': data['limit'],
            'skip': data['offset'],
        }

    def _paginate(self, request_params: Dict, raw_data: Dict) -> Optional[Dict]:
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
                raw_host.get('agentInfo', {}).get('connectedFrom'),
                self.__get_mac_addr(raw_host),
                raw_host.get('agentInfo', {}).get('platform'),
                raw_host.get('os'),
                raw_host.get('name'),
                self._normalize_dt(self.__get_first_seen(raw_host)),
                self._normalize_dt(self.__get_last_seen(raw_host)),

                raw_host
            ))

        return HydratedHostsCollection(
            hostsList,
            self._get_dedup_before_insert()
        )

    def __get_mac_addr(self, raw_data: Dict) -> str:
        mac_addr = next(
            (ent['HostAssetInterface']['macAddress']
             for ent in raw_data.get('networkInterface', {}).get('list', [])
             if ent.get('HostAssetInterface', {}).get('macAddress')),
            None
        )

        if not mac_addr:
            return None

        return mac_addr.lower()

    def __get_first_seen(self, raw_data: Dict) -> str:
        return next(
            (ent['Ec2AssetSourceSimple']['firstDiscovered']
             for ent in raw_data.get('sourceInfo', {}).get('list', [])
             if ent.get('Ec2AssetSourceSimple', {}).get('firstDiscovered')
             ),
            None
        )

    def __get_last_seen(self, raw_data: Dict) -> str:
        return next(
            (ent['Ec2AssetSourceSimple']['lastUpdated']
             for ent in raw_data.get('sourceInfo', {}).get('list', [])
             if ent.get('Ec2AssetSourceSimple', {}).get('lastUpdated')
             ),
            None
        )
