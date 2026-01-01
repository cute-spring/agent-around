const { embed } = require('ai');
const { ollama } = require('ai-sdk-ollama');
require('dotenv').config();

/**
 * 计算余弦相似度
 */
function cosineSimilarity(vecA, vecB) {
  const dotProduct = vecA.reduce((sum, a, i) => sum + a * vecB[i], 0);
  const magA = Math.sqrt(vecA.reduce((sum, a) => sum + a * a, 0));
  const magB = Math.sqrt(vecB.reduce((sum, b) => sum + b * b, 0));
  return dotProduct / (magA * magB);
}

/**
 * 获取文本向量
 */
async function getEmbedding(text) {
  const { embedding } = await embed({
    model: ollama.embedding('nomic-embed-text'),
    value: text,
  });
  return embedding;
}

/**
 * 性能追踪装饰器 (模拟)
 */
async function trace(name, fn) {
  const start = Date.now();
  try {
    const result = await fn();
    const duration = Date.now() - start;
    return { result, duration, success: true };
  } catch (error) {
    const duration = Date.now() - start;
    return { error, duration, success: false };
  }
}

module.exports = {
  cosineSimilarity,
  getEmbedding,
  trace
};
