"""
监控与成本优化示例

展示如何实现生产环境的监控、成本控制和性能优化
"""

import asyncio
import time
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic_ai import Agent

# 环境配置
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))
from common.models import get_model


# ==================== 监控领域模型 ====================

@dataclass
class APICallMetrics:
    """API调用指标"""
    timestamp: datetime
    model: str
    operation: str  # 'completion', 'chat', 'embedding'
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency_ms: float
    success: bool
    cost_usd: float


class SystemMetrics(BaseModel):
    """系统监控指标"""
    timestamp: datetime = Field(description="指标时间")
    active_requests: int = Field(description="活跃请求数")
    error_rate: float = Field(description="错误率", ge=0, le=1)
    avg_latency_ms: float = Field(description="平均延迟毫秒")
    total_cost_today: float = Field(description="今日总成本USD")
    token_usage: Dict[str, int] = Field(description="各模型Token使用量")


class CostOptimizationAdvice(BaseModel):
    """成本优化建议"""
    identified_issue: str = Field(description="识别到的问题")
    recommendation: str = Field(description="优化建议")
    estimated_savings: float = Field(description="预计节省成本USD")
    confidence: float = Field(description="建议置信度", ge=0, le=1)


# ==================== 监控系统实现 ====================

class MonitoringSystem:
    """监控系统"""
    
    def __init__(self):
        self.api_calls: List[APICallMetrics] = []
        self.cost_rates = {
            'gpt-4': {'input': 0.03, 'output': 0.06},  # 每1K tokens
            'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
            'claude-3': {'input': 0.015, 'output': 0.075}
        }
    
    def record_api_call(self, metrics: APICallMetrics):
        """记录API调用指标"""
        self.api_calls.append(metrics)
        
        # 简单的控制台输出（实际应该发送到监控系统）
        print(f"📊 API调用: {metrics.model} | Tokens: {metrics.total_tokens} | "
              f"耗时: {metrics.latency_ms:.0f}ms | 成本: ${metrics.cost_usd:.6f}")
    
    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """计算调用成本"""
        if model not in self.cost_rates:
            return 0.0
        
        rates = self.cost_rates[model]
        input_cost = (prompt_tokens / 1000) * rates['input']
        output_cost = (completion_tokens / 1000) * rates['output']
        return input_cost + output_cost
    
    def get_system_metrics(self) -> SystemMetrics:
        """获取系统级指标"""
        today_calls = [m for m in self.api_calls 
                      if m.timestamp.date() == datetime.now().date()]
        
        if not today_calls:
            return SystemMetrics(
                timestamp=datetime.now(),
                active_requests=0,
                error_rate=0,
                avg_latency_ms=0,
                total_cost_today=0,
                token_usage={}
            )
        
        total_cost = sum(m.cost_usd for m in today_calls)
        error_rate = sum(1 for m in today_calls if not m.success) / len(today_calls)
        avg_latency = sum(m.latency_ms for m in today_calls) / len(today_calls)
        
        token_usage = {}
        for call in today_calls:
            if call.model not in token_usage:
                token_usage[call.model] = 0
            token_usage[call.model] += call.total_tokens
        
        return SystemMetrics(
            timestamp=datetime.now(),
            active_requests=len([m for m in self.api_calls if m.latency_ms < 1000]),  # 简化
            error_rate=error_rate,
            avg_latency_ms=avg_latency,
            total_cost_today=total_cost,
            token_usage=token_usage
        )


# ==================== 成本优化Agent ====================

cost_optimization_agent = Agent(
    model=get_model(),
    output_type=CostOptimizationAdvice,
    system_prompt="""你是一个成本优化专家。分析API使用模式，提出具体的成本优化建议。
考虑模型选择、提示工程、缓存策略等方面。给出具体的节省估算。"""
)


# ==================== 带监控的Agent包装器 ====================

class MonitoredAgent:
    """带监控的Agent包装器"""
    
    def __init__(self, agent: Agent, model_name: str, monitoring: MonitoringSystem):
        self.agent = agent
        self.model_name = model_name
        self.monitoring = monitoring
    
    async def run_with_monitoring(self, *args, **kwargs) -> Any:
        """带监控的运行方法"""
        start_time = time.time()
        
        try:
            result = await self.agent.run(*args, **kwargs)
            end_time = time.time()
            
            # 计算Token使用（简化，实际应该从响应中提取）
            prompt_tokens = len(str(args)) // 4  # 近似计算
            completion_tokens = len(str(result)) // 4
            
            metrics = APICallMetrics(
                timestamp=datetime.now(),
                model=self.model_name,
                operation='completion',
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                latency_ms=(end_time - start_time) * 1000,
                success=True,
                cost_usd=self.monitoring.calculate_cost(
                    self.model_name, prompt_tokens, completion_tokens
                )
            )
            
            self.monitoring.record_api_call(metrics)
            return result
            
        except Exception as e:
            end_time = time.time()
            
            metrics = APICallMetrics(
                timestamp=datetime.now(),
                model=self.model_name,
                operation='completion',
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                latency_ms=(end_time - start_time) * 1000,
                success=False,
                cost_usd=0
            )
            
            self.monitoring.record_api_call(metrics)
            raise e


# ==================== 使用示例 ====================

async def main():
    """监控与成本优化示例"""
    
    # 初始化监控系统
    monitoring_system = MonitoringSystem()
    
    # 创建带监控的Agent
    base_agent = Agent(
        model=get_model(),
        system_prompt="你是一个有帮助的AI助手"
    )
    
    monitored_agent = MonitoredAgent(
        agent=base_agent,
        model_name="gpt-4",  # 假设使用GPT-4
        monitoring=monitoring_system
    )
    
    print("🚀 开始模拟API调用...")
    
    # 模拟多个API调用
    queries = [
        "请解释人工智能的基本概念",
        "写一篇关于机器学习的简短介绍", 
        "生成一些Python代码示例",
        "帮助我理解深度学习"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 调用 {i}: {query}")
        try:
            result = await monitored_agent.run_with_monitoring(query)
            print(f"✅ 成功: {result.output[:100]}...")
        except Exception as e:
            print(f"❌ 失败: {e}")
        
        # 模拟一些延迟
        await asyncio.sleep(0.5)
    
    # 获取系统指标
    print("\n" + "="*60)
    print("📈 系统监控指标")
    print("="*60)
    
    metrics = monitoring_system.get_system_metrics()
    print(f"活跃请求数: {metrics.active_requests}")
    print(f"错误率: {metrics.error_rate:.1%}")
    print(f"平均延迟: {metrics.avg_latency_ms:.0f}ms")
    print(f"今日总成本: ${metrics.total_cost_today:.6f}")
    print(f"Token使用: {metrics.token_usage}")
    
    # 成本优化建议
    print("\n" + "="*60)
    print("💡 成本优化建议")
    print("="*60)
    
    optimization_data = f"""
系统指标:
- 总调用次数: {len(monitoring_system.api_calls)}
- 总成本: ${metrics.total_cost_today:.6f}
- 主要模型: {list(metrics.token_usage.keys())}
- Token使用分布: {metrics.token_usage}
"""
    
    advice_result = await cost_optimization_agent.run(
        f"请分析以下使用数据并提出成本优化建议:\n{optimization_data}"
    )
    advice = advice_result.output
    
    print(f"识别问题: {advice.identified_issue}")
    print(f"优化建议: {advice.recommendation}")
    print(f"预计节省: ${advice.estimated_savings:.4f}")
    print(f"置信度: {advice.confidence:.0%}")


if __name__ == "__main__":
    asyncio.run(main())