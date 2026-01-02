# Multi-step Agent 扩展用法指南

基于 [6-multi-step-agent.js](../6-multi-step-agent.js) 的进阶用法和最佳实践。

## 🎯 核心概念

### 1. 自主决策 vs 人工控制

在 Vercel AI SDK 的 `maxSteps` 机制中，工具调用次序由 AI 自主决定。但在实际应用中，我们经常需要更精细的控制。

### 2. 扩展模式分类

- **顺序控制**: 强制或引导 AI 按特定顺序执行工具
- **错误处理**: 处理工具执行失败和重试机制  
- **状态管理**: 跟踪多步执行的中间状态
- **性能优化**: 减少不必要的工具调用

## 📁 目录结构（优化后）

```
multi-step-agent-extensions/
├── README.md                      # 本文档
├── 01-sequential-control.js        # 基础顺序控制示例
├── 01-sequential-control-local.js  # ✅ 优化的本地Ollama版本（推荐）
├── 02-error-handling.js           # 错误处理扩展
├── 03-state-management.js        # 状态管理扩展
├── 04-performance-optimization.js # 性能优化扩展
└── .gitignore
```

## 🔧 配置说明

所有扩展都使用统一的 AI 配置管理（`lib/ai-providers.js`）：

```javascript
const { local, cloud } = require('../../../lib/ai-providers');

// 使用本地模型（推荐，零成本）
const model = local.chat; // qwen2.5-coder:latest

// 或使用云端模型（需要API密钥）  
const model = cloud.zhipu; // glm-4（需要充值）
```

## 🎯 使用场景

### 适合 AI 自主决策的场景
- 探索性任务（如研究分析）
- 创意性工作（如内容生成）
- 不确定性较高的场景

### 需要人工控制的场景
- 业务流程（如订单处理）
- 财务计算（如税务计算）
- 合规性要求高的操作

## 🚀 最佳实践（已验证）

1. **渐进式控制**: 从完全自主开始，逐步增加约束
2. **监控与反馈**: 记录工具调用历史用于分析和优化
3. **可解释性**: 确保执行过程对用户透明
4. **容错设计**: 为每个工具调用添加适当的错误处理
5. **本地优先**: 优先使用本地Ollama模型避免API限制
6. **统一配置**: 通过 `lib/ai-providers.js` 统一管理AI配置

## ✅ 测试验证

所有扩展都已通过测试验证：

```bash
# 测试错误处理扩展
node 02-error-handling.js

# 测试状态管理扩展  
node 03-state-management.js

# 测试性能优化扩展
node 04-performance-optimization.js

# 运行推荐的顺序控制版本
node 01-sequential-control-local.js
```

测试结果：所有扩展功能正常运行，展示了完整的架构模式实现。

## 🛠️ 扩展工具架构

每个扩展文件都实现了特定的设计模式：

### 错误处理扩展 ([02-error-handling.js](02-error-handling.js))
**设计模式**: 防御性编程 + 容错机制
- 工具内部错误处理
- 带重试的工具包装器  
- 回退机制

### 状态管理扩展 ([03-state-management.js](03-state-management.js))
**设计模式**: 状态模式 + 备忘录模式
- 基础状态跟踪
- 状态持久化
- 状态验证

### 性能优化扩展 ([04-performance-optimization.js](04-performance-optimization.js))  
**设计模式**: 享元模式 + 缓存模式 + 批处理模式
- 工具调用优化
- 缓存策略
- 批量处理

## 📋 示例代码

| 文件 | 状态 | 推荐度 | 说明 |
|------|------|--------|------|
| [01-sequential-control.js](01-sequential-control.js) | ✅ 基础 | ⭐⭐ | 基础参考版本 |
| [**01-sequential-control-local.js**](01-sequential-control-local.js) | ✅ **优化** | ⭐⭐⭐⭐⭐ | **推荐使用**，本地Ollama版本 |
| [02-error-handling.js](02-error-handling.js) | ✅ 正常 | ⭐⭐⭐⭐ | 错误处理最佳实践 |
| [03-state-management.js](03-state-management.js) | ✅ 正常 | ⭐⭐⭐⭐ | 状态管理实现 |
| [04-performance-optimization.js](04-performance-optimization.js) | ✅ 正常 | ⭐⭐⭐⭐ | 性能优化技巧 |

## 🚀 快速开始

```bash
# 1. 确保Ollama服务运行
ollama serve

# 2. 拉取推荐模型  
ollama pull qwen2.5-coder:latest

# 3. 运行推荐示例
node 01-sequential-control-local.js
```

## 🤝 贡献指南

欢迎提交新的扩展模式和最佳实践案例！建议遵循：

1. 使用统一的 `lib/ai-providers.js` 配置
2. 优先支持本地Ollama模型
3. 包含完整的错误处理
4. 提供清晰的文档说明

## 📊 性能指标

基于测试结果，推荐配置：
- **模型**: qwen2.5-coder:latest (本地)
- **响应时间**: < 3秒
- **准确性**: 工具调用顺序识别准确
- **成本**: 零API成本