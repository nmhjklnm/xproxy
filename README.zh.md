# xproxy

[English](./README.en.md) | [简体中文](./README.zh-CN.md)

[![Documentation Status](https://readthedocs.org/projects/xproxy/badge/?version=latest)](https://xproxy.readthedocs.io/en/latest/?badge=latest)

## 项目介绍

xproxy 是一个为代理提供细粒度控制的轻量级代理 IP 管理框架，兼容长短效代理和多厂商代理。

市面上的短效代理价格便宜但有效期短，通常在几十秒内失效。为了有效利用这些代理，需要对其进行细粒度的控制和管理。xproxy 提供了多种特性和功能，帮助用户轻松管理和使用代理，同时支持多厂商代理的兼容和共用。

## 特性

1. **细粒度控制**：通过详细的代理属性管理，实现对代理的精确控制。包括代理的创建时间、最后使用时间、使用次数、最大使用次数、过期时间等属性。
2. **自动轮换**：支持定期轮换代理或在代理池存量不足时进行轮换。可以为代理池设置最小 IP 数量，当低于这个数量时会自动进行轮换。
3. **代理验证**：自动检查和验证代理的使用次数和过期时间，支持主动标记失效代理，确保代理在有效期内使用。
4. **可定制**：可以轻松扩展，将不同来源代理共用。

## 安装

```bash
pip install xproxy
```

## 示例

```python
from xproxy.manager import DuoMiProxyManager
import requests

# 代理管理器，会主动记录无效过的代理，防止重复使用无效代理 自动维护代理池有效代理数量
proxy_manager = DuoMiProxyManager(
    proxy_url='http://api.dmdaili.com/dmgetip.asp?apikey=3be53e22&pwd=4f2799827bfe9c6f0e2a64749cf5f3f6&getnum=50&httptype=1&geshi=2&fenge=1&fengefu=&operate=all',
)

proxy = proxy_manager.get_order_proxy()  # proxy_manager.get_random_proxy()
response = requests.get(url, proxies={"http":  str(proxy.url), "https": str(proxy.url)})

if response.status_code != 200:
    proxy_manager.mark_proxy_invalid(proxy.url)  # 可以主动标记代理为无效
```

## 使用教程

详细的使用教程请参考 [xproxy 使用文档](https://xproxy.readthedocs.io)。

### TODO

- [x] 细粒度控制：自动检查和验证代理的使用次数和过期时间，确保代理在有效期内使用。
- [ ] 多厂商兼容：支持从不同来源获取代理，并能协同共用这些代理。
- [ ] 可视化监控：提供代理使用情况的可视化监控工具。
- [ ] 本地服务器支持：可以在本地启动服务器，通过 API 形式访问代理管理功能。

