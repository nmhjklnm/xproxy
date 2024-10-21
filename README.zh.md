<div align="center">

<a href="https://nmhjklnm.github.io/xproxy/" target="_blank" title="前往 XProxy 网站"><img width="196px" alt="XProxy logo" src=".asset/logo.png"></a>

<a name="readme-top"></a>

# XProxy

一个轻量级的代理 IP 管理框架
<div align="center">
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python 版本"></a>
    <a href="https://nmhjklnm.github.io/xproxy/"><img src="https://img.shields.io/badge/docs-latest-brightgreen" alt="文档"></a>
    <a href="./LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-blue" alt="许可证"></a>
</div>


## 简介

XProxy 是一个轻量级的代理 IP 管理框架，提供对代理的细粒度控制，兼容短期和长期代理，并支持多个供应商。

**↘  XProxy 文档  ↙**

[English](https://nmhjklnm.github.io/xproxy/) · [简体中文](https://nmhjklnm.github.io/xproxy/zh-CN/)

</div>

## 动机
短期代理价格便宜，但寿命非常短，通常在几秒钟内就会失效。为了有效利用这些代理，需要进行细粒度的控制和管理。XProxy 提

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

详细的使用教程请参考 [xproxy 使用文档](https://nmhjklnm.github.io/xproxy/zh/)。

### TODO

- [x] 细粒度控制：自动检查和验证代理的使用次数和过期时间，确保代理在有效期内使用。
- [ ] 多厂商兼容：支持从不同来源获取代理，并能协同共用这些代理。
- [ ] 可视化监控：提供代理使用情况的可视化监控工具。
- [ ] 本地服务器支持：可以在本地启动服务器，通过 API 形式访问代理管理功能。

