# 架构设计决策：企业级代理 (Proxy) 配置模式

在开发涉及 LLM (大语言模型) 的应用时，如何处理企业内网环境下的代理配置是一个常见的架构决策点。本文档详细对比了两种实现方式：**全局环境变量法** 与 **程序化精细控制法**，并解释了为什么我们选择了后者。

## 1. 方案对比

### 方案 A：全局环境变量 (os.environ['http_proxy'])

这种方式通过修改进程的环境变量来影响底层的网络库。

```python
import os
os.environ['http_proxy'] = 'http://proxy.corporate.com:8080'
os.environ['https_proxy'] = 'http://proxy.corporate.com:8080'
```

*   **优点**：实现简单，几乎不需要修改代码。
*   **缺点**：
    *   **全局副作用**：进程内所有的 HTTP 请求（包括访问内网数据库、Redis、监控端点）都会被强制通过代理，这往往会导致内网连接失败。
    *   **隐式行为**：代码逻辑中看不出代理的存在，增加了排查网络问题的难度。
    *   **功能局限**：无法处理需要自定义证书 (SSL)、特定超时或身份验证的复杂代理场景。

### 方案 B：程序化精细控制 (Programmatic Injection) —— **本项目采用**

通过显式创建 `httpx.AsyncClient` 并将其注入到特定的 Provider 中。

```python
def _get_http_client():
    proxy_url = os.getenv('LLM_PROXY_URL')
    if proxy_url:
        return httpx.AsyncClient(proxy=proxy_url)
    return None

# 注入到特定 Provider
model = GoogleModel(..., provider=GoogleProvider(..., http_client=_get_http_client()))
```

*   **优点**：
    *   **环境隔离**：代理仅作用于 LLM 请求，不会干扰其他内网通信。
    *   **显式设计**：开发者可以清晰地在代码中追踪网络流量的去向。
    *   **高度可扩展**：可以轻松增加 SSL 证书配置、自定义超时设置或连接池优化。
*   **缺点**：代码量略多，需要理解各 SDK 的 Provider 注入机制。

---

## 2. 为什么在企业级架构中方案 B 更好？

### 2.1 零干扰原则 (Principle of Least Interference)
在复杂的微服务或企业应用中，程序通常需要同时访问：
1.  **公网 API** (如 Gemini, OpenAI) -> **需要代理**
2.  **内部微服务** (如 User Service) -> **禁止代理**
3.  **基础设施** (如 Redis, Postgres) -> **禁止代理**

方案 B 能够精确地为 (1) 开启代理，而确保 (2) 和 (3) 的直连性能和安全性。

### 2.2 应对“中间人”拦截 (SSL Inspection)
许多企业代理会进行 SSL 劫持以检查流量。这要求客户端必须信任公司的根证书。使用方案 B，我们可以轻松扩展：

```python
return httpx.AsyncClient(
    proxy=proxy_url,
    verify="/path/to/corporate-ca-cert.pem" # 轻松处理自定义证书
)
```

### 2.3 调试与可观测性
当出现 `ConnectionError` 时，显式的配置让我们可以迅速定位：是 LLM 的代理挂了，还是本机的基础网络出了问题。方案 B 让网络拓扑在代码层面变得透明。

## 3. 性能优化：连接池管理 (Connection Pooling)

在高性能应用中，代理配置的实现方式直接影响吞吐量。

| 特性 | `os.environ` (全局变量) | `_get_http_client` (程序化单例) |
| :--- | :--- | :--- |
| **隔离性** | 差（影响全进程所有请求） | **优（仅作用于 LLM Provider）** |
| **连接复用** | 依赖 SDK 内部实现 | **强（显式单例连接池复用）** |
| **握手开销** | 中（取决于 SDK 默认行为） | **极低（Keep-Alive 长连接）** |
| **定制化** | 无（仅限代理地址） | **极强（超时、证书、并发限制）** |
| **可观测性** | 隐式（难以追踪网络路径） | **显式（代码层面清晰可见）** |

### 3.1 为什么不推荐每次新建客户端？
每次创建 `httpx.AsyncClient` 都会初始化一个新的连接池。这意味着：
*   **TCP 握手开销**：每个请求都需要重新进行三次握手。
*   **资源枯竭**：高并发下会导致大量 `TIME_WAIT` 状态的连接，最终耗尽端口。

### 3.2 我们的解决方案：单例模式 (Singleton)
我们在 `models.py` 中实现了全局单例的 HTTP 客户端。通过复用同一个 `AsyncClient` 实例，我们实现了：
*   **Keep-Alive 复用**：多个 LLM 请求复用同一个长连接。
*   **并发控制**：通过 `httpx.Limits` 限制最大连接数，防止压垮代理服务器。

```python
_shared_http_client = httpx.AsyncClient(
    proxy=proxy_url,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)
)
```

### 3.3 深度权衡：显式设计与单例模式

在本项目中，我们选择 **程序化单例** 而非 **环境变量** 的核心逻辑如下：

1.  **确定性网络拓扑**：在企业级应用中，网络路径应该是可预测的。全局变量 `os.environ` 引入了“隐式副作用”，可能导致非预期的流量走向。而程序化注入确保了只有 LLM 流量走代理，其他流量（如 DB/Cache）保持直连。
2.  **资源效率**：通过 `_shared_http_client` 全局单例，我们避免了频繁的 TCP 三次握手和 TLS 协商，这在高并发 Agent 场景下能显著降低响应延迟（Latency）。
3.  **可测试性**：程序化配置允许我们在单元测试中轻松注入 Mock Client，而无需修改系统的全局状态。

---

## 4. 本项目中的具体实现

我们在 `common/models.py` 中通过 `_get_http_client()` 辅助函数实现了这一模式。它通过读取 `LLM_PROXY_URL` 环境变量，动态地为 Azure 和 Google Provider 生成适配的 HTTP 客户端。

这种设计确保了系统既能在普通开发环境下“开箱即用”，也能在严苛的企业生产环境下通过简单配置达到“工业级稳健”。
