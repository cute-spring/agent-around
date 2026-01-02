/**
 * 方案 3: 多级树形路由 (Hierarchical Tree Routing)
 * 
 * 【原因】
 * 在大型企业中，业务分类可能多达数百个。一次性将所有分类交给模型或向量匹配会导致准确率下降和 Token 消耗剧增。
 * 
 * 【目标】
 * 模仿人类行政体系，先通过一级路由确定大部门（如“账单部”），再由二级路由确定具体小组（如“退款组”）。
 * 
 * 【结果】
 * 1. 每一层只需要处理 3-5 个选项，极大地提升了模型的判断精度。
 * 2. 路由逻辑更加清晰，便于各部门维护自己的二级路由规则。
 * 
 * 【可进一步提升的地方】
 * 1. 实现动态路由树加载：根据一级路由的结果，动态从数据库加载二级的 Prompt 或关键词配置。
 * 2. 引入“跳过层级”逻辑：对于某些极高频且明确的请求，支持从一级直达三级，减少处理链路。
 */
const ROUTES_TREE = {
  SUPPORT: {
    description: '技术支持与故障处理',
    subRoutes: {
      INSTALLATION: '安装与环境配置问题',
      RUNTIME: '运行报错与性能问题',
      SECURITY: '账号安全与权限问题'
    }
  },
  BILLING: {
    description: '账单、发票与支付',
    subRoutes: {
      REFUND: '退款申请',
      INVOICE: '发票开具',
      SUBSCRIPTION: '订阅计划变更'
    }
  }
};

async function hierarchicalRoute(input) {
  console.log(`\n--- 分层处理请求: "${input}" ---`);

  // 第一步：识别一级大类 (此处简化演示，实际可调用向量或 LLM)
  let topCategory = 'SUPPORT';
  if (input.includes('钱') || input.includes('费') || input.includes('退款')) {
    topCategory = 'BILLING';
  }
  console.log(`[Level 1] 命中大类: ${topCategory} (${ROUTES_TREE[topCategory].description})`);

  // 第二步：在一级大类下细分 (二级路由)
  const subRoutes = ROUTES_TREE[topCategory].subRoutes;
  let subCategory = 'GENERAL';
  
  // 模拟二级识别逻辑
  for (const [id, desc] of Object.entries(subRoutes)) {
    if (input.includes(id.toLowerCase()) || input.includes(desc.substring(0, 2))) {
      subCategory = id;
      break;
    }
  }
  
  const finalPath = `${topCategory} > ${subCategory}`;
  console.log(`[Level 2] 精准定位: ${subCategory}`);
  console.log(`[最终结果] 路由路径: ${finalPath}`);
  
  return finalPath;
}

async function main() {
  console.log('--- 企业级方案 3: 分层路由 (嵌套结构版) ---');
  await hierarchicalRoute('我需要申请退款，年度计划不符合预期');
  await hierarchicalRoute('软件在启动时提示权限不足');
}

main().catch(console.error);
