# 高德地图 (AMap) MCP 服务器功能清单

本指南列出了 `@amap/amap-maps-mcp-server` 提供的所有工具及其详细功能。这些工具可以直接通过 MCP 协议集成到任何兼容的 AI Agent（如 Pydantic AI, Claude Desktop 等）中。

---

## 🌍 地理编码与逆地理编码

| 工具名称 | 功能描述 |
| :--- | :--- |
| **`maps_geo`** | **地理编码**：将详细的结构化地址（如“北京市朝阳区阜通东大街6号”）转换为经纬度坐标。支持对地标性名胜景区、建筑物名称解析。 |
| **`maps_regeocode`** | **逆地理编码**：将经纬度坐标转换为对应的行政区划地址信息（如国家、省、市、区、街道及门牌号）。 |

## 🔍 地点搜索 (POI)

| 工具名称 | 功能描述 |
| :--- | :--- |
| **`maps_text_search`** | **关键词搜索**：根据用户传入的关键词，搜索出相关的兴趣点 (POI)。例如搜索“咖啡馆”、“火车站”等。 |
| **`maps_around_search`** | **周边搜索**：根据用户传入的关键词以及坐标中心点，在指定的半径范围内搜索 POI。 |
| **`maps_search_detail`** | **详情查询**：查询特定 POI ID 的详细信息（如电话、营业时间、评分等）。 |

## 🧭 路径规划 (Direction)

| 工具名称 | 功能描述 |
| :--- | :--- |
| **`maps_direction_driving`** | **驾车路径规划**：根据起终点坐标规划小客车/轿车通勤方案，支持躲避拥堵、避免收费等多种策略。 |
| **`maps_direction_transit_integrated`** | **公交/地铁规划**：规划综合各类公共交通方式（火车、公交、地铁）的通勤方案。 |
| **`maps_direction_walking`** | **步行路径规划**：规划 100km 以内的步行通勤方案。 |
| **`maps_bicycling`** | **骑行路径规划**：规划 500km 以内的骑行方案，会考虑天桥、单行线、封路等情况。 |

## 🌡️ 环境与定位

| 工具名称 | 功能描述 |
| :--- | :--- |
| **`maps_weather`** | **天气查询**：根据城市名称或标准行政区划代码 (adcode) 查询指定城市的实时天气及未来 3 天预报。 |
| **`maps_ip_location`** | **IP 定位**：根据用户输入的 IP 地址，定位该 IP 所在的城市位置。 |
| **`maps_distance`** | **距离测量**：测量两个经纬度坐标之间的直线距离、驾车距离或步行距离。 |

---

## 🛠️ 如何在代码中使用

在 [6-mcp-amap.py](file:///Users/gavinzhang/ws-ai-recharge-2026/agent-around/py-pydantic-lab/examples/02-intermediate/6-mcp-amap.py) 中，你只需通过以下方式即可启用所有这些功能：

```python
server = MCPServerStdio(
    'npx',
    args=['-y', '@amap/amap-maps-mcp-server'],
    env=os.environ.copy()
)

agent = Agent(
    model,
    toolsets=[server],  # 这一行会自动注入上述所有工具
    system_prompt="..."
)
```

---
*文档更新日期：2026-01-17*
