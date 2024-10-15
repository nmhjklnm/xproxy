"""Test config"""
import pytest
from typing import List, Dict
from xproxy.manager import ProxyManager  # 替换为你的模块名
from typing import Optional


class TestProxyManager(ProxyManager):
    def get_proxies(self) -> List[Dict[str, Optional[str]]]:
        return [
            {"url": "http://127.0.0.1:8000"},
            {"url": "http://127.0.0.1:8001"},
            {"url": "http://127.0.0.1:8002"}
        ]


@pytest.fixture
def proxy_manager():
    return TestProxyManager(min_valid_proxies=4, max_use_count=5, proxy_expiry_seconds=10)
