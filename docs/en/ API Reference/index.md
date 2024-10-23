# API Reference

本节提供了 xproxy 库的 API 参考。这里您可以找到关于核心类和方法的详细信息。

## 核心类

xproxy 的核心功能主要由两个类提供：`ProxyManager` 和 `Proxy`。

### ProxyManager

`ProxyManager` 是一个抽象基类，用于管理代理池。它提供了获取、刷新和轮换代理的基本功能。



### Proxy

`Proxy` 类表示单个代理，包含代理的 URL、使用次数、有效性等信息。


各个类的具体使用参见其他部分。