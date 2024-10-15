# xproxy

## 特性

- **可定制**：可以轻松扩展，将不同来源代理共用。
- **代理验证**：自动检查和验证代理的使用次数和过期时间。
- **自动轮换**：定期刷新和轮换代理，以确保持续供应有效代理。
- **线程安全**：使用多线程处理代理轮换，无阻塞主应用程序。
- **轮询选择**：支持轮询代理选择，均匀分配负载。

## 安装

```
pip install xproxy
```

## 示例

```python
from xproxy.manager import DuoMiProxyManager
import requests
proxy_manager = DuoMiProxyManager(  # 代理管理器，会主动记录无效过的代理，防止重复使用无效代理 自动维护代理池有效代理数量，
    proxy_url='http://api.dmdaili.com/dmgetip.asp?apikey=3be53e22&pwd=4f2799827bfe9c6f0e2a64749cf5f3f6&getnum=50&httptype=1&geshi=2&fenge=1&fengefu=&operate=all',
    max_use_count=5,        # 设定单个代理最大使用次数
    min_valid_proxies=20,   # 设定代理池至少维持20个有效代理
    proxy_expiry_seconds=60,  # 设定单个代理60秒内 或者达到 endtime的时间记录为超时
    rotate_seconds=30       # 定时服务，每隔30秒，检查一遍代理池，如果代理池代理少了，就获取代理
)
proxy = proxy_manager.get_order_proxy()  # proxy_manager.get_random_proxy()
response = requests.get(url, headers=headers, proxies={
                        "http":  str(proxy.url), "https": str(proxy.url)}, timeout=60)
if response.status_code != 200:
    proxy_manager.mark_proxy_invalid(proxy.url)  # 可以主动标记代理为无效
  
```

### 2.1 init project

```bash
poetry install -v
```

### 2.2 usage

TODO

## 3. Develop

You may need to read the [develop document](./docs/development.md) to use SRC Layout in your IDE.
