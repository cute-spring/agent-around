/**
 * 示例 8: 向量嵌入 (Embeddings)
 * 
 * 核心价值：统一的向量化接口 (Standardized Embedding API)
 * 除了生成文本，AI 应用中非常重要的一环是向量化（RAG 的基础）。
 * SDK 提供了 embed 和 embedMany 函数，让你能以统一的方式将文本转化为数字向量。
 */

const { embed, embedMany } = require('ai');
const { ollama } = require('ai-sdk-ollama');

async function main() {
  console.log('--- 示例 8: 向量嵌入演示 ---');

  const model = ollama.embeddingModel('nomic-embed-text:latest');

  // 1. 单个文本向量化
  console.log('\n正在向量化单个词汇: "机器学习"...');
  const { embedding } = await embed({
    model,
    value: '机器学习',
  });
  console.log(`向量长度: ${embedding.length} (前 5 位: ${embedding.slice(0, 5)}...)`);

  // 2. 批量文本向量化
  console.log('\n正在批量向量化多个句子...');
  const { embeddings } = await embedMany({
    model,
    values: ['太阳很温暖', '今天在下雨', '人工智能正在改变世界'],
  });
  console.log(`成功获取 ${embeddings.length} 个向量。`);
  
  // 核心价值：这些向量可以直接存入 Pinecone, Supabase, Milvus 等向量数据库。
}

main().catch(console.error);
