import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';
import dotenv from 'dotenv';
import { convertToModelMessages, streamText, generateText } from 'ai';
import { MODEL_REGISTRY, getModelInstance, registerModel } from '../../../lib/ai-providers.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SESSIONS_DIR = path.join(__dirname, '../../../data/sessions');
const AGENTS_DIR = path.join(__dirname, '../../../data/agents');

// 确保目录存在
if (!fs.existsSync(SESSIONS_DIR)) {
  fs.mkdirSync(SESSIONS_DIR, { recursive: true });
}
if (!fs.existsSync(AGENTS_DIR)) {
  fs.mkdirSync(AGENTS_DIR, { recursive: true });
}

// 必须在加载 ai-providers 之前加载环境变量
dotenv.config({ path: path.join(__dirname, '../../../.env') });

// --- 示例：通过代码注册 Azure 模型 (支持 Token Provider) ---
try {
  registerModel({
    id: 'azure-gpt-4',
    name: 'Azure GPT-4 (Token Auth)',
    provider: 'azure',
    modelId: 'gpt-4',
    resourceName: process.env.AZURE_RESOURCE_NAME,
    tokenProvider: async () => {
      console.log('Fetching Azure AD Token...');
      return "dummy-token-for-demo"; 
    }
  });
} catch (e) {
  console.warn('Azure registration skipped:', e.message);
}

// --- 示例：通过代码注册 Google Gemini 模型 ---
try {
  registerModel({
    id: 'gemini-1.5-flash',
    name: 'Google Gemini 1.5 Flash',
    provider: 'google',
    modelId: 'gemini-1.5-flash',
    apiKeyEnv: 'GOOGLE_GENERATIVE_AI_API_KEY',
    group: 'cloud'
  });
} catch (e) {
  console.warn('Gemini registration skipped:', e.message);
}

import { execSync } from 'child_process';

const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// 获取可用模型列表
app.get('/api/models', (req, res) => {
  res.json(MODEL_REGISTRY());
});

// --- Agent 相关接口 ---

// 获取所有 Agent
app.get('/api/agents', (req, res) => {
  try {
    if (!fs.existsSync(AGENTS_DIR)) return res.json([]);
    const files = fs.readdirSync(AGENTS_DIR);
    const agents = files
      .filter(f => f.endsWith('.json'))
      .map(f => {
        const filePath = path.join(AGENTS_DIR, f);
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
      });
    res.json(agents);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// 创建或更新 Agent
app.post('/api/agents', (req, res) => {
  const { id, name, prompt } = req.body;
  if (!name || !prompt) {
    return res.status(400).json({ error: 'Name and Prompt are required' });
  }

  const agentId = id || `agent-${Date.now()}`;
  const agentData = { id: agentId, name, prompt };
  const filePath = path.join(AGENTS_DIR, `${agentId}.json`);

  try {
    fs.writeFileSync(filePath, JSON.stringify(agentData, null, 2));
    res.json(agentData);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// 删除 Agent
app.delete('/api/agents/:id', (req, res) => {
  const filePath = path.join(AGENTS_DIR, `${req.params.id}.json`);
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    res.json({ success: true });
  } else {
    res.status(404).json({ error: 'Agent not found' });
  }
});

// 获取所有会话
app.get('/api/sessions', (req, res) => {
  try {
    const files = fs.readdirSync(SESSIONS_DIR);
    const sessions = files
      .filter(f => f.endsWith('.json'))
      .map(f => {
        const id = f.replace('.json', '');
        const filePath = path.join(SESSIONS_DIR, f);
        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
        const title = Array.isArray(data) ? id : (data.title || id);
        return { id, title };
      });
    res.json(sessions);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// 获取特定会话内容
app.get('/api/sessions/:id', (req, res) => {
  const filePath = path.join(SESSIONS_DIR, `${req.params.id}.json`);
  if (fs.existsSync(filePath)) {
    try {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      // 兼容旧格式（数组）和新格式（对象）
      const messages = Array.isArray(data) ? data : (data.messages || []);
      res.json(messages);
    } catch (e) {
      res.status(500).json({ error: 'Failed to parse session file' });
    }
  } else {
    res.json([]);
  }
});

// 删除会话
app.delete('/api/sessions/:id', (req, res) => {
  const filePath = path.join(SESSIONS_DIR, `${req.params.id}.json`);
  if (fs.existsSync(filePath)) {
    fs.unlinkSync(filePath);
    res.json({ success: true });
  } else {
    res.status(404).json({ error: 'Session not found' });
  }
});

// 搜索会话内容 (使用 grep 优化)
app.get('/api/search', (req, res) => {
  const { q } = req.query;
  if (!q) return res.json([]);

  try {
    // 使用 grep 在 sessions 目录下进行全文搜索 (-i 不区分大小写, -l 仅列出匹配的文件名)
    // 这种方式比在 Node.js 中读取并解析所有 JSON 文件要快得多
    const command = `grep -il "${q.replace(/"/g, '\\"')}" ${SESSIONS_DIR}/*.json`;
    let output = '';
    try {
      output = execSync(command).toString();
    } catch (e) {
      // 如果 grep 没找到匹配项，它会抛出错误（退出码 1），这里捕获并返回空数组
      return res.json([]);
    }

    const matchedFiles = output.split('\n').filter(Boolean);
    const results = matchedFiles.map(filePath => {
      const fileName = path.basename(filePath);
      const id = fileName.replace('.json', '');
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      const title = Array.isArray(data) ? id : (data.title || id);
      return { id, title };
    });

    res.json(results);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.post('/api/chat', async (req, res) => {
  const { sessionId, userInput, modelId, agentId } = req.body;
  
  try {
    const model = await getModelInstance(modelId || 'qwen-local');

    // 加载 Agent 配置
    let systemPrompt = '';
    if (agentId) {
      const agentPath = path.join(AGENTS_DIR, `${agentId}.json`);
      if (fs.existsSync(agentPath)) {
        const agentData = JSON.parse(fs.readFileSync(agentPath, 'utf8'));
        systemPrompt = agentData.prompt;
      }
    }

    // 加载历史
    const filePath = path.join(SESSIONS_DIR, `${sessionId}.json`);
    let sessionData = { messages: [], title: sessionId };
    if (fs.existsSync(filePath)) {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      if (Array.isArray(data)) {
        sessionData.messages = data;
      } else {
        sessionData = data;
      }
    }

    // 添加用户消息
    sessionData.messages.push({ role: 'user', content: userInput });

    // 如果是新会话且没有标题，生成标题
    if (sessionData.messages.length === 1 && (!sessionData.title || sessionData.title.startsWith('session-'))) {
      try {
        const { text: generatedTitle } = await generateText({
          model: model,
          system: '你是一个对话标题生成助手。请根据用户的第一句话，总结出一个简短、准确的标题（不超过10个字）。直接返回标题，不要包含任何标点符号、解释或引用。',
          prompt: `用户说: "${userInput}"\n\n请生成标题:`,
        });
        sessionData.title = generatedTitle.trim().replace(/^["']|["']$/g, '');
      } catch (e) {
        console.error('Failed to generate title:', e);
        sessionData.title = userInput.slice(0, 20);
      }
    }

    const result = await streamText({
      model: model,
      system: systemPrompt,
      messages: sessionData.messages,
      onFinish: ({ text }) => {
        // 保存 AI 回复
        sessionData.messages.push({ role: 'assistant', content: text });
        fs.writeFileSync(filePath, JSON.stringify(sessionData, null, 2));
      }
    });

    res.setHeader('Content-Type', 'text/plain; charset=utf-8');
    
    for await (const part of result.fullStream) {
      if (part.type === 'text-delta') {
        res.write(`0:${JSON.stringify(part.text)}\n`); // 匹配 index.html 的解析逻辑
      }
    }
    res.end();

  } catch (error) {
    console.error('Chat error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/generate-title', async (req, res) => {
  const { message, modelId } = req.body;
  
  try {
    const model = await getModelInstance(modelId || 'qwen-local');

    const { text } = await generateText({
      model: model,
      system: '你是一个对话标题生成助手。请根据用户的第一句话，总结出一个简短、准确的标题（不超过10个字）。直接返回标题，不要包含任何标点符号、解释或引用。',
      prompt: `用户说: "${message}"\n\n请生成标题:`,
    });

    res.json({ title: text.trim().replace(/^["']|["']$/g, '') });

  } catch (error) {
    console.error('Title generation error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Backend server running at http://localhost:${port}`);
});
