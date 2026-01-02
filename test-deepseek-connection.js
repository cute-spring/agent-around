/**
 * DeepSeek API连接测试脚本
 * 用于验证API密钥和网络连接
 */

require('dotenv').config();
const { createOpenAI } = require('@ai-sdk/openai');

async function testDeepSeekConnection() {
  console.log('🔍 测试DeepSeek API连接...');
  
  const apiKey = process.env.DEEPSEEK_API_KEY;
  
  if (!apiKey || apiKey === 'your_deepseek_api_key_here') {
    console.error('❌ 错误: 未找到有效的DEEPSEEK_API_KEY');
    console.log('请检查.env文件中的DEEPSEEK_API_KEY配置');
    return false;
  }
  
  console.log('✅ API密钥格式正确');
  
  // 创建DeepSeek客户端
  const deepseekProvider = createOpenAI({
    apiKey: apiKey,
    baseURL: 'https://api.deepseek.com',
    compatibility: 'compatible',
  });
  
  try {
    console.log('🔄 尝试连接到DeepSeek API...');
    
    // 使用AI SDK的正确方式进行测试
    const { generateText } = require('ai');
    
    const result = await generateText({
      model: deepseekProvider.chat('deepseek-chat'),
      prompt: 'Hello, this is a connection test.',
      maxTokens: 10
    });
    
    console.log('✅ DeepSeek API连接成功！');
    console.log('响应:', result.text);
    return true;
    
  } catch (error) {
    console.error('❌ DeepSeek API连接失败:');
    console.error('错误信息:', error.message);
    
    if (error.status === 401) {
      console.error('🔐 认证失败: API密钥可能无效或已过期');
      console.log('请从 https://platform.deepseek.com/ 获取新的API密钥');
    } else if (error.code === 'ENOTFOUND') {
      console.error('🌐 网络连接问题: 无法解析api.deepseek.com');
      console.log('请检查网络连接和DNS设置');
    } else {
      console.error('详细错误:', error);
    }
    
    return false;
  }
}

// 运行测试
async function main() {
  console.log('=== DeepSeek API连接测试 ===');
  const success = await testDeepSeekConnection();
  
  if (success) {
    console.log('\n🎉 测试成功！可以正常运行DeepSeek示例');
  } else {
    console.log('\n❌ 测试失败，请解决上述问题后再运行示例');
  }
}

main().catch(console.error);