import datetime
import requests
from typing import List, Optional, Dict
from xproxy.manager import ProxyManager
import datetime


class DuoMiProxyManager(ProxyManager):
    def __init__(self, proxy_url: str, max_use_count: Optional[int] = 10, min_valid_proxies: int = 3, proxy_expiry_seconds: Optional[int] = None, rotate_seconds: Optional[int] = 60):
        self.proxy_url = proxy_url
        super().__init__(max_use_count, min_valid_proxies,
                    proxy_expiry_seconds, rotate_seconds)

    def get_proxies(self) -> List[Dict[str, Optional[str]]]:
        response = requests.get(self.proxy_url)
        proxy_list = response.json()['data']
        proxies = []
        for proxy in proxy_list:
            expiry_time = datetime.datetime.strptime(
                proxy['endtime'], '%Y/%m/%d %H:%M:%S')
            proxies.append({
                'url': f"http://{proxy['ip']}:{proxy['port']}",
                'provider': 'DuoMi',
                'expiry_time': expiry_time
            })
        return proxies
