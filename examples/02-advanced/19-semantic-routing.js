/**
 * 示例 19: 语义路由 (Semantic Routing)
 * 
 * 核心原理：
 * 传统的路由依赖关键字匹配 (Regex) 或复杂的 If/Else。
 * 语义路由利用向量嵌入 (Embeddings) 计算用户输入与各“路由示例”之间的余弦相似度。
 * 这种方式更智能，能够理解用户意图（例如，“我无法登录”和“账号密码报错”会被自动路由到技术支持）。
 */
const { embed, cosineSimilarity } = require('ai');
const { ollama } = require('ai-sdk-ollama');
require('dotenv').config();

// 选择一个本地嵌入模型
const embeddingModel = ollama.embedding('nomic-embed-text');

// 1. 定义不同的业务路由及其示例 query
const routes = [
  {
    name: '技术支持 (Technical Support)',
    description: '处理 Bug、安装问题或代码错误。',
    examples: [
      '我的代码抛出了 TypeError 错误 (My code threw a TypeError)',
      '如何安装这个库？ (How to install this library?)',
      '服务器启动时一直崩溃 (Server keeps crashing on startup)',
      '空指针异常调试 (Null pointer exception debugging)',
      'API 返回了 500 错误 (API returned 500 error)',
    ],
  },
  {
    name: '账单与账户 (Billing & Account)',
    description: '处理付款、订阅或账户设置。',
    examples: [
      '我想更改我的信用卡信息 (I want to change my credit card)',
      '如何取消订阅？ (How to cancel subscription?)',
      '在哪里可以找到我上个月的发票？ (Where to find my invoice?)',
      '我的账户被锁定了 (My account is locked)',
      '申请退款流程 (Refund request process)',
    ],
  },
];

/**
 * 计算一组示例字符串的平均向量 (Centroid)
 * 将多个示例聚合成一个代表该路由特征的单一向量
 */
async function getRouteEmbedding(examples) {
  const embeddings = await Promise.all(
    examples.map(async (text) => {
      const { embedding } = await embed({
        model: embeddingModel,
        value: text,
      });
      return embedding;
    })
  );

  // 计算所有示例向量的均值
  const length = embeddings[0].length;
  const avg = new Array(length).fill(0);
  for (const emb of embeddings) {
    for (let i = 0; i < length; i++) {
      avg[i] += emb[i] / embeddings.length;
    }
  }
  return avg;
}

/**
 * 核心路由函数：计算输入与各路由的相似度并分发
 */
async function routeQuery(query) {
  console.log(`\n用户输入: "${query}"`);
  console.log('正在计算语义相似度...');

  // 1. 将用户输入转化为向量
  const { embedding: queryEmbedding } = await embed({
    model: embeddingModel,
    value: query,
  });

  // 2. 将输入向量与每个路由的特征向量进行对比
  const results = await Promise.all(
    routes.map(async (route) => {
      const routeEmbedding = await getRouteEmbedding(route.examples);
      const similarity = cosineSimilarity(queryEmbedding, routeEmbedding);
      return { name: route.name, similarity };
    })
  );

  // 3. 按相似度得分排序，选择最高分
  const bestMatch = results.sort((a, b) => b.similarity - a.similarity)[0];

  console.log('各路由得分详情:');
  results.forEach(r => console.log(` - ${r.name}: ${r.similarity.toFixed(4)}`));
  
  console.log(`\n[路由决策] 匹配度最高的是: ${bestMatch.name.toUpperCase()}`);
}

async function main() {
  console.log('--- 语义路由 (Semantic Router) 模式演示 ---');
  console.log('利用向量相似度将请求精准分发至不同部门，无需复杂的关键词规则。\n');

  // 测试用例 1: 模糊的技术问题
  await routeQuery('我在日志里看到了空指针异常 (null pointer exception)');
  
  // 测试用例 2: 账单相关问题
  await routeQuery('我的年度计划可以退款吗？');
}

main().catch(console.error);
