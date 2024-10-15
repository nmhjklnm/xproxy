import datetime
import pytest
from xproxy.manager import Proxy  # 替换为你的模块名
from pydantic import BaseModel, AnyUrl


def test_proxy_creation(proxy_manager):
    assert len(proxy_manager.proxies) == 3
    for proxy in proxy_manager.proxies.values():
        assert isinstance(proxy.url, AnyUrl)
        assert proxy.max_use_count == 5
        assert proxy.expiry_seconds == 10


def test_proxy_validity(proxy_manager):
    proxy = list(proxy_manager.proxies.values())[0]
    assert proxy.is_valid

    # Simulate max use count reached
    proxy.use_count = 5
    assert not proxy.is_valid

    # Reset use count for further tests
    proxy.use_count = 0

    # Simulate expiry time reached
    proxy.created_at = datetime.datetime.now() - datetime.timedelta(seconds=11)
    assert not proxy.is_valid


def test_increment_usage(proxy_manager):
    proxy = list(proxy_manager.proxies.values())[0]
    initial_use_count = proxy.use_count
    proxy.increment_usage()
    assert proxy.use_count == initial_use_count + 1

    # Simulate max use count reached
    proxy.use_count = 4
    proxy.increment_usage()
    assert proxy.use_count == 5
    assert not proxy.is_valid


def test_get_random_proxy(proxy_manager):
    proxy = proxy_manager.get_random_proxy()
    assert proxy.is_valid
    assert proxy.last_used > datetime.datetime.min
    assert proxy.use_count == 1


def test_refresh_proxies(proxy_manager):
    initial_count = len(proxy_manager.proxies)
    proxy_manager.refresh_proxies()
    assert len(proxy_manager.proxies) == initial_count  # No new proxies added

    # Simulate adding new proxies with unique URLs
    proxy_manager.get_proxies = lambda: [{"url": "http://127.0.0.1:8003"}]
    proxy_manager.refresh_proxies()
    assert len(proxy_manager.proxies) == initial_count + 1


def test_mark_proxy_invalid(proxy_manager):
    proxy = list(proxy_manager.proxies.values())[0]
    proxy_manager.mark_proxy_invalid(proxy.url)
    assert not proxy.is_valid
