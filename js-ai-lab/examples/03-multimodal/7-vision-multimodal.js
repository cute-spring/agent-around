/**
 * 示例 7: 多模态视觉 (Vision / Multimodal)
 * 
 * 核心价值：标准化的多模态输入 (Standardized Multimodal Inputs)
 * 不同模型对图片的输入格式要求各异（Base64, URL, Uint8Array 等）。
 * Vercel AI SDK 提供了一套标准化的 content 数组格式，让你能以同样的方式处理图片和文本。
 */

const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const fs = require('fs');
const path = require('path');

async function main() {
  console.log('--- 示例 7: 多模态视觉演示 (使用本地图片) ---');

  try {
    // 读取 assets 目录下的本地图片文件
    const imagePath = path.join(__dirname, 'assets', 'image-1.png');
    
    if (!fs.existsSync(imagePath)) {
      throw new Error(`找不到图片文件: ${imagePath}`);
    }

    const imageBuffer = fs.readFileSync(imagePath);

    const result = await generateText({
      // 使用你本地安装的视觉模型
      model: ollama('llama3.2-vision'),
      messages: [
        {
          role: 'user',
          content: [
            { type: 'text', text: '这张图片里有什么？请详细描述。' },
            {
              type: 'image',
              // SDK 支持直接传入 Buffer, Uint8Array, ArrayBuffer 或 Base64 字符串
              image: imageBuffer,
            },
          ],
        },
      ],
    });

    console.log('\nAI 视觉分析结果:');
    console.log(result.text);
  } catch (error) {
    console.error('执行失败:', error.message);
    console.log('\n提示: 请确保你已经运行了 `ollama run llama3.2-vision:11b` 并且模型已就绪。');
  }
}

main().catch(console.error);
