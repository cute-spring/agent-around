/**
 * 示例 10: 语义相似度计算 (Semantic Similarity)
 * 
 * 核心价值：将文本转化为数学距离 (Text to Math)
 * 这是 RAG 和搜索系统的核心。通过比较两个向量之间的“余弦相似度”，
 * 我们可以量化两段文本在语义上的接近程度，而不仅仅是关键词匹配。
 * 
 * 这能做什么？
 * 1. 自动分类：将用户反馈自动归类到最接近的分类中。
 * 2. 去重：在数据库中寻找语义重复的内容。
 * 3. 推荐系统：寻找与用户正在阅读的文章语义最接近的其他文章。
 */

const { embedMany, cosineSimilarity } = require('ai');
const { ollama } = require('ai-sdk-ollama');

async function main() {
  console.log('--- 示例 10: 语义相似度计算 ---');

  const model = ollama.embeddingModel('nomic-embed-text:latest');

  const phrases = [
    '人工智能将改变世界',    // 基准句子
    'AI 正在革新我们的生活', // 语义非常接近
    '今天天气真不错',       // 语义完全无关
    '机器学习是 AI 的分支',   // 语义相关
    'AI正在颠覆我们的生活方式、改变我们的工作方式、以及我们与世界的互动方式。',
  ];

  console.log(`正在对比以下短语与 "${phrases[0]}" 的相似度...\n`);

  // 1. 批量获取所有短语的向量
  const { embeddings } = await embedMany({
    model,
    values: phrases,
  });

  // 2. 计算第一个句子与其他句子的余弦相似度
  // 余弦相似度范围从 -1 到 1，越接近 1 表示语义越相似
  for (let i = 1; i < phrases.length; i++) {
    const similarity = cosineSimilarity(embeddings[0], embeddings[i]);
    
    let label = '';
    if (similarity > 0.8) label = '🔥 (极度相似)';
    else if (similarity > 0.5) label = '✅ (比较相关)';
    else label = '❌ (毫不相关)';

    console.log(`[相似度: ${similarity.toFixed(4)}] ${label}`);
    console.log(`   - "${phrases[0]}"`);
    console.log(`   - "${phrases[i]}"\n`);
  }
}

main().catch(console.error);
