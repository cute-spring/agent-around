# Routing KPIs & Release Playbook | 路由指标与发布手册

This document operationalizes routing into something you can ship, monitor, and roll back like code.
本文把“路由”工程化为可发布、可监控、可回滚的系统能力。

**Scope | 范围**

- KPI dictionary (definitions, formulas, dimensions) | 指标字典（定义、公式、维度）
- Data contract (events/fields for observability) | 数据契约（埋点事件与字段）
- Gates & alerts (CI + online) | 门禁与告警（离线 + 线上）
- Release SOP (shadow → canary → rollout → rollback) | 发布 SOP（旁路 → 灰度 → 全量 → 回滚）
- Reporting templates (weekly + per-release) | 报告模板（周报 + 版本回归）

---

## 1) KPI Dictionary | 指标字典

The golden rule: report KPIs with **routing version** and **taxonomy version**.
黄金原则：所有 KPI 必须绑定**路由版本**与**分类体系版本**。

### 1.1 Routing Quality | 路由质量

#### Top-1 accuracy | Top-1 准确率

- Definition | 定义：% requests where router’s top choice equals the final label.
  路由器 Top-1 选择与最终标签一致的比例。
- Formula | 公式：`correct_top1 / total_labeled`.
- Dimensions | 维度建议：`route_version`, `tenant`, `channel`, `locale`, `department`, `intent`, `risk_tier`.
- Notes | 说明：
  - Offline: golden dataset in CI for regressions. | 离线：金标集用于门禁回归。
  - Online: human-labeled or downstream verified outcomes. | 线上：人工标注或下游可验证结果。

#### Coverage (auto-route share) | Coverage（自动路由占比）

- Definition | 定义：% requests successfully routed without abstain/escalation.
  无需拒绝/澄清/升级即可自动分发的比例。
- Formula | 公式：`auto_routed / total_requests`.
- Split | 拆分建议：`coverage_by_stage`（在哪一层命中：cache/regex/vector/llm）。

#### Abstain rate | Abstain rate（拒绝/澄清比例）

- Definition | 定义：% requests ending with clarify or reject.
  以澄清或拒绝结束的比例。
- Formula | 公式：`abstain / total_requests`.
- Must split | 必须拆分：
  - `clarify_rate`（ask a question）| 澄清率（追问）
  - `reject_rate`（refuse safely）| 拒绝率（安全拒绝）
- Interpretation | 解读：
  - Too low can mean unsafe routing (over-confident). | 过低可能代表不够安全（过度自信）。
  - Too high can mean poor taxonomy / thresholds / context. | 过高可能代表分类体系/阈值/上下文处理有问题。

#### Escalation rate | Escalation rate（进人工比例）

- Definition | 定义：% requests handed to human review/fallback.
  进入人工复核/兜底的比例。
- Formula | 公式：`human_handoff / total_requests`.
- Operational note | 运营提示：Always track queue SLA (time-to-first-response). | 必须同时盯人工队列 SLA（首响时间）。

#### Hard-case hit rate | Hard-case 命中率

- Definition | 定义：accuracy/recall on a curated high-risk subset.
  在高风险子集上的准确率/召回率。
- Dataset policy | 数据集政策：Hard-case set is curated, versioned, and cannot be “auto-updated”.
  Hard-case 集合需人工维护、版本化，不允许自动滚动更新。
- Typical gates | 常见门槛：no regression, or stricter thresholds than general traffic.
  通常要求不回归，或门槛显著高于全量。

### 1.2 Cost Metrics | 成本指标

#### Tokens per request | 每请求 token

- Definition | 定义：avg and P95 tokens per request.
  每请求 token 的均值与 P95。
- Split | 拆分：
  - prompt vs completion | prompt 与 completion
  - router vs downstream | 路由层与下游执行层
  - by stage | 按阶段（cache/regex/vector/llm）

#### LLM call share | LLM 调用占比

- Definition | 定义：% traffic that triggers LLM during routing.
  路由过程中触发 LLM 的流量比例。
- Why | 价值：cost + tail latency driver; essential for canary safety.
  成本与长尾延迟的关键驱动，是灰度安全的核心指标。

#### Cache hit rate | 缓存命中率

- Must split | 必须拆分：
  - exact hit | 精确命中
  - semantic hit | 语义命中
- Extra SLO | 额外 SLO：semantic cache wrong-hit incidents.
  语义缓存“错误命中”必须单独做 SLO，不要只看命中率。

---

## 2) Data Contract | 数据契约（埋点与字段）

Goal: make every routing decision **traceable** and **replayable**.
目标：让每一次路由决策都**可追溯**、并可在离线环境**复现**。

### 2.1 Event: routing.decision | 事件：routing.decision

Emit once per user request.
每次用户请求产生一条。

```json
{
  "event": "routing.decision",
  "timestamp": "2026-01-01T00:00:00Z",
  "trace_id": "...",
  "request_id": "...",
  "tenant_id": "...",
  "channel": "web|app|api",
  "locale": "zh-CN",
  "route_version": "router@2026-01-01",
  "taxonomy_version": "intent@v3",
  "model": {
    "provider": "...",
    "model_id": "..."
  },
  "prompt_version": "router_prompt@v12",
  "threshold_version": "thresholds@v5",
  "input": {
    "text_hash": "sha256(...)"
  },
  "decision": {
    "label": "BILLING_REFUND",
    "confidence": 0.86,
    "stage": "vector|llm|regex|cache",
    "outcome": "auto|clarify|reject|human",
    "reason": "short_reason_or_code"
  },
  "cost": {
    "tokens_prompt": 123,
    "tokens_completion": 45,
    "llm_calls": 1
  },
  "latency_ms": {
    "total": 80,
    "stage": {
      "cache": 1,
      "regex": 0,
      "vector": 40,
      "llm": 35
    }
  }
}
```

Guidelines | 指南：

- Store raw text separately with policy/consent; log only hashes by default.
  原文按合规策略单独存储；日志默认只存 hash。
- `route_version`, `taxonomy_version`, `prompt_version`, `threshold_version` must be present.
  四个版本字段必须齐全。
- `outcome` must be one of allowlisted outcomes.
  `outcome` 必须来自白名单。

---

## 3) Gates & Alerts | 门禁与告警

### 3.1 CI Gate (offline) | 离线门禁（CI）

Recommended gates (examples) | 推荐门槛（示例）：

- Hard-case: no regression allowed.
  Hard-case：不允许回归。
- Top-1 accuracy: regression ≤ 0.5% absolute on golden set.
  Top-1 accuracy：金标集绝对下降不超过 0.5%。
- Abstain + escalation: bounded increases.
  Abstain + escalation：增幅必须受限。

### 3.2 Online Alerts (production) | 线上告警（生产）

- Sudden spike: LLM call share, reject rate, human handoff.
  突增类：LLM 调用占比、拒绝率、人工移交比例。
- Drift signals: confusion matrix shift on critical intents.
  漂移信号：关键意图混淆矩阵发生显著迁移。
- Tail latency: P95/P99 increase for routing total.
  长尾延迟：路由总耗时 P95/P99 上升。

---

## 4) Release SOP | 发布 SOP

### 4.1 Shadow Routing | 旁路评估

- Run new router in parallel and compare decisions.
  新旧路由并行运行，仅对比决策。
- Compare: label, confidence, outcome, downstream cost impact.
  对比：标签、置信度、结果（auto/clarify/reject/human）、以及对下游成本的影响。

### 4.2 Canary Rollout | 小流量灰度

- Start at 1% traffic, then 5% → 25% → 50% → 100%.
  从 1% 开始，再到 5% → 25% → 50% → 100%。
- Gates per step | 每一步门槛：
  - Hard-case no regression. | Hard-case 不回归。
  - Reject/clarify/escalation bounded increase. | 拒绝/澄清/升级率增幅受限。
  - P95/P99 routing latency stable. | P95/P99 路由延迟稳定。
  - Cost within budget (tokens, LLM calls). | 成本在预算内（token、LLM 调用）。

### 4.3 Rollback | 回滚

- One-click rollback to last known-good `route_version`.
  一键回滚到上一版已验证的 `route_version`。
- Store routing artifacts as immutable packages.
  路由产物以不可变包形式保存（prompts/阈值/分类映射/模型选择）。

---

## 5) Reporting Templates | 报告模板

### 5.1 Weekly Routing Health Report | 路由健康周报

- Summary: Top-1 accuracy, coverage, abstain, escalation, LLM call share, P95/P99.
  摘要：Top-1 accuracy、Coverage、Abstain、Escalation、LLM 调用占比、P95/P99。
- Confusion matrix deltas for critical intents.
  关键意图混淆矩阵变化。
- Top regressions: worst 20 intents by recall delta.
  最大回归：recall 下降最多的 20 个意图。
- Cost: tokens/request trend and budget.
  成本：每请求 token 趋势与预算。
- Action items: update hard-case set, thresholds, taxonomy.
  行动项：更新 Hard-case、阈值、分类体系。

### 5.2 Per-Release Report | 版本回归报告

- Versions: route_version, taxonomy_version, model_id, prompt_version, threshold_version.
  版本信息：route_version、taxonomy_version、model_id、prompt_version、threshold_version。
- Offline CI results: golden + hard-case.
  离线结果：金标集 + Hard-case。
- Shadow deltas: mismatch rate and top mismatch clusters.
  旁路差异：不一致率与主要不一致簇。
- Canary results: KPI trends by step.
  灰度结果：各阶段 KPI 曲线。
- Rollback plan and oncall owner.
  回滚预案与值班负责人。

