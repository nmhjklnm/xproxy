# XProxy


[![Documentation Status](https://readthedocs.org/projects/xproxy/badge/?version=latest)](https://xproxy.readthedocs.io/en/latest/?badge=latest)

## Project Introduction

xproxy is a lightweight proxy IP management framework that provides fine-grained control for proxies, compatible with both short-lived and long-lived proxies, and supports multiple vendors.

Short-lived proxies are cheap but have a very short lifespan, often expiring within seconds. To effectively utilize these proxies, fine-grained control and management are required. xproxy provides various features and functionalities to help users manage and use proxies easily, while also supporting compatibility and sharing of proxies from multiple vendors.

## Features

1. **Fine-grained control**: Manage proxies with detailed attributes for precise control, including creation time, last used time, usage count, maximum usage count, expiry time, etc.
2. **Automatic rotation**: Support periodic rotation of proxies or rotation when the proxy pool is below a minimum threshold. You can set a minimum number of IPs for the proxy pool, and it will rotate proxies when the count falls below this number.
3. **Proxy validation**: Automatically check and validate the usage count and expiration time of proxies, and support actively marking proxies as invalid to ensure they are used within their valid period.
4. **Customizable**: Easily extendable to share proxies from different sources.

## Installation

```bash
pip install xproxy
```

## Example

```python
from xproxy.manager import DuoMiProxyManager
import requests

# Proxy manager that actively records invalid proxies to prevent reuse and maintains the number of valid proxies in the pool
proxy_manager = DuoMiProxyManager(
    proxy_url='http://api.dmdaili.com/dmgetip.asp?apikey=3be53e22&pwd=4f2799827bfe9c6f0e2a64749cf5f3f6&getnum=50&httptype=1&geshi=2&fenge=1&fengefu=&operate=all',
)

proxy = proxy_manager.get_order_proxy()  # proxy_manager.get_random_proxy()
response = requests.get(url, proxies={"http":  str(proxy.url), "https": str(proxy.url)})

if response.status_code != 200:
    proxy_manager.mark_proxy_invalid(proxy.url)  # Actively mark the proxy as invalid
```

## Usage Guide

For detailed usage instructions, please refer to the [xproxy Documentation](https://xproxy.readthedocs.io).

### TODO

- [x] Fine-grained control: Automatically check and verify the usage count and expiration time of proxies to ensure they are used within their valid period.
- [ ] Multi-vendor compatibility: Support obtaining proxies from different sources and allow sharing of these proxies.
- [ ] Visualization monitoring: Provide visualization tools for monitoring proxy usage.
- [ ] Local server support: Enable starting a local server to access proxy management functionalities via API.
