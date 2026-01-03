"""
高级RAG示例：知识图谱增强检索

展示如何结合向量检索与知识图谱推理实现精准的多跳问答
"""

import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from examples.common.models import get_model


# ==================== 知识图谱领域模型 ====================

class KnowledgeEntity(BaseModel):
    """知识图谱实体"""
    id: str = Field(description="实体ID")
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型")
    description: str = Field(description="实体描述")


class KnowledgeRelation(BaseModel):
    """知识图谱关系"""
    source_id: str = Field(description="源实体ID")
    target_id: str = Field(description="目标实体ID") 
    relation_type: str = Field(description="关系类型")
    weight: float = Field(description="关系权重", ge=0, le=1)


class KnowledgeGraph(BaseModel):
    """知识图谱"""
    entities: Dict[str, KnowledgeEntity] = Field(description="实体字典")
    relations: List[KnowledgeRelation] = Field(description="关系列表")


class RetrievedContext(BaseModel):
    """检索到的上下文"""
    text_chunks: List[str] = Field(description="文本片段")
    entities: List[KnowledgeEntity] = Field(description="相关实体")
    relations: List[KnowledgeRelation] = Field(description="相关关系")


class MultiHopAnswer(BaseModel):
    """多跳推理答案"""
    final_answer: str = Field(description="最终答案")
    reasoning_steps: List[str] = Field(description="推理步骤")
    supporting_evidence: List[str] = Field(description="支持证据")
    confidence: float = Field(description="置信度", ge=0, le=1)


# ==================== 模拟知识图谱数据 ====================

# 模拟医疗知识图谱
def create_medical_knowledge_graph() -> KnowledgeGraph:
    """创建模拟的医疗知识图谱"""
    
    entities = {
        "diabetes": KnowledgeEntity(
            id="diabetes",
            name="糖尿病",
            type="disease", 
            description="一种慢性代谢性疾病，特征是高血糖"
        ),
        "insulin": KnowledgeEntity(
            id="insulin", 
            name="胰岛素",
            type="treatment",
            description="用于治疗糖尿病的激素药物"
        ),
        "metformin": KnowledgeEntity(
            id="metformin",
            name="二甲双胍",
            type="treatment",
            description="口服降糖药物，常用于2型糖尿病"
        ),
        "heart_disease": KnowledgeEntity(
            id="heart_disease",
            name="心脏病", 
            type="disease",
            description="影响心脏功能的疾病总称"
        ),
        "ai_diagnosis": KnowledgeEntity(
            id="ai_diagnosis",
            name="AI辅助诊断",
            type="technology",
            description="使用人工智能技术辅助医疗诊断"
        )
    }
    
    relations = [
        KnowledgeRelation(
            source_id="diabetes",
            target_id="insulin",
            relation_type="treated_by",
            weight=0.9
        ),
        KnowledgeRelation(
            source_id="diabetes", 
            target_id="metformin",
            relation_type="treated_by",
            weight=0.8
        ),
        KnowledgeRelation(
            source_id="diabetes",
            target_id="heart_disease", 
            relation_type="complicates_to",
            weight=0.7
        ),
        KnowledgeRelation(
            source_id="ai_diagnosis",
            target_id="diabetes",
            relation_type="can_diagnose",
            weight=0.85
        )
    ]
    
    return KnowledgeGraph(entities=entities, relations=relations)


# ==================== RAG Agent 定义 ====================

# 1. 查询理解Agent
query_understanding_agent = Agent(
    model=get_model(),
    system_prompt="""你是一个查询理解专家。分析用户问题，识别关键实体和关系。
输出结构化的查询分析结果。"""
)


# 2. 图谱检索Agent  
knowledge_retrieval_agent = Agent(
    model=get_model(),
    result_type=RetrievedContext,
    system_prompt="""你是一个知识检索专家。基于查询分析结果，从知识图谱中检索相关信息。
返回相关的实体、关系和文本证据。"""
)


# 3. 多跳推理Agent
multi_hop_reasoning_agent = Agent(
    model=get_model(), 
    result_type=MultiHopAnswer,
    system_prompt="""你是一个多跳推理专家。基于检索到的知识，进行多步推理来回答问题。
展示清晰的推理步骤和置信度评估。"""
)


# ==================== 高级RAG系统 ====================

class AdvancedRAGSystem:
    """知识图谱增强的RAG系统"""
    
    def __init__(self):
        self.knowledge_graph = create_medical_knowledge_graph()
        self.query_understander = query_understanding_agent
        self.knowledge_retriever = knowledge_retrieval_agent
        self.reasoning_engine = multi_hop_reasoning_agent
    
    def retrieve_from_knowledge_graph(self, query_analysis: str) -> RetrievedContext:
        """从知识图谱中检索相关信息"""
        
        # 模拟检索逻辑 - 实际应该使用图数据库查询
        entities = []
        relations = []
        text_chunks = []
        
        # 简单的内容匹配检索
        if "糖尿病" in query_analysis:
            entities.append(self.knowledge_graph.entities["diabetes"])
            entities.append(self.knowledge_graph.entities["insulin"])
            relations.extend([r for r in self.knowledge_graph.relations 
                           if r.source_id == "diabetes"])
            
            text_chunks.extend([
                "糖尿病是一种慢性代谢性疾病，全球有数亿患者",
                "胰岛素是治疗糖尿病的关键药物，需要定期注射",
                "AI技术可以辅助糖尿病诊断和个性化治疗方案制定"
            ])
        
        if "AI" in query_analysis or "人工智能" in query_analysis:
            entities.append(self.knowledge_graph.entities["ai_diagnosis"])
            text_chunks.append(
                "人工智能在医疗诊断中的应用包括影像分析、病历理解和风险预测"
            )
        
        return RetrievedContext(
            text_chunks=text_chunks,
            entities=entities,
            relations=relations
        )
    
    async def answer_question(self, question: str) -> MultiHopAnswer:
        """回答复杂问题"""
        
        print(f"🧠 处理问题: {question}")
        
        # 阶段1: 查询理解
        print("🔍 阶段1 - 查询理解")
        query_analysis = await self.query_understander.run(
            f"请分析以下问题的关键实体和关系: {question}"
        )
        
        # 阶段2: 知识检索  
        print("📚 阶段2 - 知识检索")
        context = self.retrieve_from_knowledge_graph(query_analysis.data)
        
        print(f"✅ 检索到 {len(context.entities)} 个实体, {len(context.relations)} 个关系")
        
        # 阶段3: 多跳推理
        print("🤔 阶段3 - 多跳推理")
        context_text = f"""
检索到的知识:
文本证据: {', '.join(context.text_chunks)}
相关实体: {', '.join([e.name for e in context.entities])}
相关关系: {', '.join([f'{r.relation_type}({r.source_id}->{r.target_id})' for r in context.relations])}
"""
        
        answer = await self.reasoning_engine.run(
            f"基于以下知识，请回答这个问题: {question}\n{context_text}"
        )
        
        print("🎉 多跳推理完成!")
        return answer


# ==================== 使用示例 ====================

async def main():
    """高级RAG系统示例"""
    
    rag_system = AdvancedRAGSystem()
    
    # 复杂的多跳问题
    complex_question = """
    糖尿病如何治疗？AI技术如何帮助糖尿病的诊断和治疗？
    如果糖尿病控制不好，可能会导致什么并发症？
    """
    
    try:
        answer = await rag_system.answer_question(complex_question)
        
        print("\n" + "="*60)
        print("💡 多跳推理答案")
        print("="*60)
        print(f"最终答案: {answer.final_answer}")
        print(f"\n置信度: {answer.confidence:.2f}")
        print(f"\n推理步骤:")
        for i, step in enumerate(answer.reasoning_steps, 1):
            print(f"  {i}. {step}")
        print(f"\n支持证据: {', '.join(answer.supporting_evidence[:2])}...")
        
    except Exception as e:
        print(f"❌ RAG处理过程中出现错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())