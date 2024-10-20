import random
import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, HttpUrl
from abc import ABC, abstractmethod
import logging
from enum import Enum
import time
import threading


class InvalidReason(str, Enum):
    MAX_USE_COUNT = "max_use_count"
    EXPIRED = "expired"
    MANUAL = "manual"


class Proxy(BaseModel):
    url: HttpUrl
    created_at: datetime.datetime = None
    last_used: datetime.datetime = datetime.datetime.min
    use_count: int = 0
    _is_valid: bool = True
    invalid_reason: Optional[InvalidReason] = None
    max_use_count: Optional[int] = 10  # Default value, can be overridden
    expiry_seconds: Optional[int] = None  # Optional expiry time in seconds
    expiry_time: Optional[datetime.datetime] = None  # Optional expiry datetime
    metadata: Dict[str, Optional[str]] = {}  # Metadata dictionary

    def __init__(self, **data):
        super().__init__(**data)
        # Set created_at to current time if not provided
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        # Ensure expiry_time is set correctly if expiry_seconds is provided
        if self.expiry_seconds is not None:
            self.expiry_time = self.created_at + \
                datetime.timedelta(seconds=self.expiry_seconds)
        # Ensure expiry_time is not in the past
        if self.expiry_time is not None and self.expiry_time < datetime.datetime.now():
            self._is_valid = False
            self.invalid_reason = InvalidReason.EXPIRED

    @property
    def formatted(self) -> str:
        username = self.metadata.get('username')
        password = self.metadata.get('password')
        if username and password:
            return f"http://{username}:{password}@{self.url.host}:{self.url.port}"
        return f"http://{self.url.host}:{self.url.port}"

    @property
    def is_valid(self) -> bool:
        now = datetime.datetime.now()
        if self.max_use_count is not None and self.use_count >= self.max_use_count:
            self._is_valid = False
            self.invalid_reason = InvalidReason.MAX_USE_COUNT
        if self.expiry_seconds is not None and (now - self.created_at).total_seconds() >= self.expiry_seconds:
            self._is_valid = False
            self.invalid_reason = InvalidReason.EXPIRED
        if self.expiry_time is not None and now >= self.expiry_time:
            self._is_valid = False
            self.invalid_reason = InvalidReason.EXPIRED
        return self._is_valid

    @is_valid.setter
    def is_valid(self, value: bool):
        self._is_valid = value
        if not value and self.invalid_reason is None:
            self.invalid_reason = InvalidReason.MANUAL

    def increment_usage(self):
        self.use_count += 1
        if self.max_use_count is not None and self.use_count >= self.max_use_count:
            self._is_valid = False
            self.invalid_reason = InvalidReason.MAX_USE_COUNT


class ProxyManager(ABC):
    def __init__(self, max_use_count: Optional[int] = 10, min_valid_proxies: int = 3, proxy_expiry_seconds: Optional[int] = None, rotate_seconds: Optional[int] = 60):
        self.min_valid_proxies = min_valid_proxies
        self.max_use_count = max_use_count
        self.proxy_expiry_seconds = proxy_expiry_seconds
        self.rotate_seconds = rotate_seconds
        self.proxies: Dict[str, Proxy] = self._get_proxies()
        self._start_rotation_thread()

    @abstractmethod
    def get_proxies(self) -> List[Dict[str, Optional[str]]]:
        """
        This method should be implemented to return a list of dictionaries containing proxy information.
        """
        pass

    def _get_proxies(self) -> Dict[str, Proxy]:
        proxy_dicts = self.get_proxies()
        proxies = {}
        for proxy_dict in proxy_dicts:
            # 获取 Proxy 类的属性
            proxy_attributes = Proxy.__annotations__.keys()

            # 分离属性
            proxy_kwargs = {key: proxy_dict.pop(key) for key in list(
                proxy_dict.keys()) if key in proxy_attributes}
            metadata = proxy_dict  # 剩余的项作为元数据

            # 创建 Proxy 对象
            proxy = Proxy(**proxy_kwargs, metadata=metadata)
            if self.max_use_count is not None:
                proxy.max_use_count = self.max_use_count
            if self.proxy_expiry_seconds is not None:
                proxy.expiry_seconds = self.proxy_expiry_seconds

            assert proxy.is_valid, (
                f"Invalid proxy detected: {proxy.formatted}, "
                f"created_at: {proxy.created_at}, "
                f"expiry_seconds: {proxy.expiry_seconds}, "
                f"expiry_time: {proxy.expiry_time}, "
                f"now: {datetime.datetime.now()}, "
                f"proxy_kwargs: {proxy_kwargs}, "
                f"metadata: {metadata}"
            )
            proxies[proxy.url] = proxy
        return proxies

    def refresh_proxies(self, replace_invalid: bool = False):
        """
        Refresh the proxy list to ensure the minimum number of valid proxies is met.

        This method fetches new proxies and adds them to the proxy list until the number
        of valid proxies meets the `min_valid_proxies` threshold. If no new proxies are
        added in an iteration, the method logs a warning and stops to avoid an infinite loop.
        """
        logging.info(f"Starting proxy refresh. Total proxies: {len(self.proxies)}, Valid proxies: {
            len(self.valid_proxies)}, Invalid proxies: {len(self.invalid_proxies)}")

        initial_valid_count = len(self.valid_proxies)

        while len(self.valid_proxies) < self.min_valid_proxies:
            logging.info(f"Current valid proxies: {
                len(self.valid_proxies)}, Minimum valid proxies: {self.min_valid_proxies}")
            new_proxies = self._get_proxies()
            existing_urls = set(self.proxies.keys())
            added_proxies = 0
            for proxy in new_proxies.values():
                if proxy.url not in existing_urls or replace_invalid:
                    self.proxies[proxy.url] = proxy
                    added_proxies += 1
            logging.info(f"Refreshed proxies, added {
                added_proxies} new proxies, total count: {len(self.proxies)}")
            if added_proxies == 0:
                logging.warning(
                    "No new proxies were added. Stopping refresh to avoid infinite loop.")
                break
            time.sleep(1)  # Wait for 1 second before the next refresh attempt

        final_valid_count = len(self.valid_proxies)
        added_valid_proxies = final_valid_count - initial_valid_count

        logging.info(f"Finished proxy refresh. Total proxies: {len(self.proxies)}, Valid proxies: {
            len(self.valid_proxies)}, Invalid proxies: {len(self.invalid_proxies)}")
        logging.info(
            f"Added {added_valid_proxies} valid proxies during refresh.")

    def get_random_proxy(self) -> Proxy:
        available_proxies = list(self.valid_proxies.values())
        if len(available_proxies) < self.min_valid_proxies:
            print("Available proxies below threshold, refreshing proxies...")
            self.refresh_proxies()
            available_proxies = list(self.valid_proxies.values())

        if not available_proxies:
            raise Exception("No available proxies left after refresh")

        proxy = random.choice(available_proxies)
        proxy.last_used = datetime.datetime.now()
        proxy.increment_usage()
        return proxy

    def mark_proxy_invalid(self, proxy_url: str):
        proxy = self.proxies.get(proxy_url)
        if proxy:
            proxy.is_valid = False
            print(f"Marked proxy as invalid: {proxy.formatted}")
        else:
            print(f"Proxy not found: {proxy_url}")

    @property
    def valid_proxies(self) -> Dict[str, Proxy]:
        return {url: proxy for url, proxy in self.proxies.items() if proxy.is_valid}

    @property
    def invalid_proxies(self) -> Dict[str, Proxy]:
        return {url: proxy for url, proxy in self.proxies.items() if not proxy.is_valid}

    def _start_rotation_thread(self):
        def rotate_proxies():
            while True:
                time.sleep(self.rotate_seconds)
                logging.info("Rotating proxies...")
                self.refresh_proxies(replace_invalid=True)

        rotation_thread = threading.Thread(target=rotate_proxies, daemon=True)
        rotation_thread.start()

    def get_order_proxy(self) -> Proxy:
        """
        Get a proxy in a round-robin fashion.
        """
        available_proxies = list(self.valid_proxies.values())
        if len(available_proxies) < self.min_valid_proxies:
            logging.info(
                "Available proxies below threshold, refreshing proxies...")
            self.refresh_proxies()
            available_proxies = list(self.valid_proxies.values())

        if not available_proxies:
            raise Exception("No available proxies left after refresh")

        # Sort proxies by last used time to implement round-robin
        available_proxies.sort(key=lambda proxy: proxy.last_used)
        proxy = available_proxies[0]
        proxy.last_used = datetime.datetime.now()
        proxy.increment_usage()
        return proxy
