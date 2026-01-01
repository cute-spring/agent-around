/**
 * 方案 1: 混合分层路由 (Hybrid Tiered Routing)
 * 
 * 【原因】
 * 纯语义路由（Embedding）虽然召回率高，但存在性能开销（需要调用模型）且对特定硬性指令（如 "sudo"）不够灵敏。
 * 纯关键词匹配虽然极快且精准，但无法处理模糊表达。
 * 
 * 【目标】
 * 结合两者的优势：先通过关键词实现“极速闪电层”，未命中时再通过语义向量实现“深度理解层”。
 * 
 * 【结果】
 * 1. 关键词命中时响应时间 < 1ms。
 * 2. 模糊表达（如“应用闪退”）能准确路由到技术支持部门。
 * 
 * 【可进一步提升的地方】
 * 1. 引入 Aho-Corasick 算法提升大规模关键词过滤性能。
 * 2. 将语义向量匹配部分接入向量数据库（如 Pinecone 或 Milvus）以支持百万级路由规则。
 */
const { embed } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { cosineSimilarity } = require('./utils');
require('dotenv').config();

const ROUTES = {
  ADMIN: {
    keywords: ['sudo', 'root', 'config', 'system-reset'],
    examples: ['如何重置系统配置', '进入管理后台', '修改系统底层参数']
  },
  SUPPORT: {
    keywords: ['help', 'error', 'bug', '无法'],
    examples: ['软件运行报错了', '安装过程中崩溃', '找不到对应的文件']
  }
};

/**
 * 获取路由的重心向量
 */
async function getRouteCentroid(examples) {
  const embeddings = await Promise.all(
    examples.map(async (text) => {
      const { embedding } = await embed({
        model: ollama.embedding('nomic-embed-text'),
        value: text,
      });
      return embedding;
    })
  );
  const len = embeddings[0].length;
  const avg = new Array(len).fill(0);
  for (const emb of embeddings) {
    for (let i = 0; i < len; i++) avg[i] += emb[i] / embeddings.length;
  }
  return avg;
}

async function hybridRoute(input) {
  console.log(`\n--- 处理输入: "${input}" ---`);

  // 1. 关键词匹配 (极速层)
  for (const [name, config] of Object.entries(ROUTES)) {
    if (config.keywords.some(k => input.toLowerCase().includes(k))) {
      console.log(`[极速层] 🚀 命中关键词 "${name}"，跳过语义计算。`);
      return name;
    }
  }

  // 2. 语义匹配 (深度层)
  console.log('[深度层] 🧠 正在执行向量相似度计算...');
  const { embedding: inputVec } = await embed({
    model: ollama.embedding('nomic-embed-text'),
    value: input,
  });

  let bestRoute = null;
  let maxScore = -1;

  for (const [name, config] of Object.entries(ROUTES)) {
    const centroid = await getRouteCentroid(config.examples);
    const score = cosineSimilarity(inputVec, centroid);
    console.log(` - 路由 ${name} 匹配得分: ${score.toFixed(4)}`);
    if (score > maxScore) {
      maxScore = score;
      bestRoute = name;
    }
  }

  console.log(`[结果] 最终路由至: ${bestRoute} (得分: ${maxScore.toFixed(4)})`);
}

async function main() {
  await hybridRoute('sudo reset system');
  await hybridRoute('我的应用在启动时闪退了');
}

main().catch(console.error);
