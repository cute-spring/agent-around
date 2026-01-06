# Pydantic-AI 多模态视觉提取实验室报告

本报告总结了在 `py-pydantic-lab` 中实现的 4 个基于 Pydantic-AI 和智谱 GLM-4.6v 模型的视觉提取示例。

---

## 🚀 核心架构设计

在所有示例中，我们采用了以下设计模式：
1. **Schema-First Extraction**: 先定义 Pydantic 模型，利用模型校验 LLM 的输出。
2. **Graceful Degradation (优雅降级)**: 当结构化提取因校验失败时，自动回退到纯文本分析模式。
3. **Provider Factory**: 通过 `common/models.py` 统一管理不同 LLM Provider 的初始化。

---

## 🧪 实验用例详解

### 1. 基础视觉多模态 (Case 7)
*   **文件**: [7-vision-multimodal.py](7-vision-multimodal.py)
*   **目标**: 验证模型对图片的识别与基础描述能力。
*   **特性**: 适配了 `llama3.2-vision` (本地) 和 `glm-4.6v` (云端)。

### 2. 固定业务板块提取 (Case 8)
*   **文件**: [8-extract-report.py](8-extract-report.py)
*   **目标**: 从 Apple 财报图中提取指定的 Operating Segments 数据。
*   **关键模型**:
    ```python
    class OperatingSegment(BaseModel):
        segment_name: str
        revenue: str
    ```
*   **成果**: 成功精准提取了 Americas, Europe, Japan 等 6 个板块的数值。

### 3. 多维财务审计专家 (Case 9)
*   **文件**: [9-financial-auditor.py](9-financial-auditor.py)
*   **目标**: 模拟专业审计师，同时解析“区域”和“产品”两个维度的表格，并进行 YoY 增长率分析。
*   **进阶特性**:
    *   **数据一致性校验**: 自动验证各区域总和是否匹配 Total。
    *   **智能洞察**: 识别出增长最快的“明星产品” (iPhone) 和区域 (Asia Pacific)。

### 4. 动态时期数据提取器 (Case 10) 🎯
*   **文件**: [10-dynamic-period-extractor.py](10-dynamic-period-extractor.py)
*   **目标**: 根据用户输入的动态时间段 (如 "Q4 2009")，在包含多列数据的复杂表格中精准定位。
*   **输入/输出示例**:
    *   **Input**: "Q4 2009"
    *   **Output**: 成功提取 Americas CPU: 1,252, Revenue: $5,236。
    *   **Input**: "Q1 2010"
    *   **Output**: 成功提取 Americas CPU: 1,187, Revenue: 6,092。

---

## 🛠 开发环境配置

*   **Python 虚拟环境**: `py-pydantic-lab/venv`
*   **核心库**: `pydantic-ai`, `pydantic`, `openai` (作为智谱协议层)
*   **环境变量 (.env)**:
    *   `LLM_PROVIDER=zhipu`
    *   `ZHIPU_MODEL_NAME=glm-4.6v`
    *   `ZHIPU_API_KEY=***`

---

## 💡 教练点评与最佳实践

1.  **容错设计**: 在视觉 OCR 场景中，建议将数值字段定义为 `str` 或 `Optional[str]`，因为 LLM 经常会提取出带千分位逗号的数字（如 "1,252"），直接定义为 `int` 会导致 Pydantic 校验失败。
2.  **Prompt 引导**: 在 System Prompt 中明确告诉模型表格中存在多列数据（如 Q4 09 vs Q1 10），可以显著提高提取的准确率。
3.  **视觉对齐**: 对于多列复杂报表，GLM-4.6v 展现出了极强的列对齐能力，这是实现动态时期提取的关键。

---
*文档生成日期: 2026-01-06*
