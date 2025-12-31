const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StreamableHTTPClientTransport } = require('@modelcontextprotocol/sdk/client/streamableHttp.js');
const { z } = require('zod');
const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
require('dotenv').config();

/**
 * Simple JSON Schema to Zod converter for basic types.
 * Converts MCP tool input schemas to Zod schemas for AI SDK compatibility.
 * 
 * @param {Object} schema - The JSON schema to convert
 * @returns {z.ZodType} - The corresponding Zod schema
 */
function jsonSchemaToZod(schema) {
  if (!schema) return z.any();
  
  if (schema.type === 'object') {
    const shape = {};
    if (schema.properties) {
      for (const [key, value] of Object.entries(schema.properties)) {
        shape[key] = jsonSchemaToZod(value);
        if (schema.required && !schema.required.includes(key)) {
            shape[key] = shape[key].optional();
        }
      }
    }
    return z.object(shape).passthrough();
  }
  
  switch (schema.type) {
    case 'string': return z.string();
    case 'number':
    case 'integer': return z.number();
    case 'boolean': return z.boolean();
    case 'array': return z.array(jsonSchemaToZod(schema.items));
    default: return z.any();
  }
}

/**
 * Initializes and connects an MCP client.
 * 
 * @param {Object} config - Configuration for the MCP client
 * @param {string} config.url - The MCP server URL
 * @param {Object} config.headers - Headers for the connection
 * @returns {Promise<Client>} - The connected MCP client
 */
async function setupMcpClient({ url, headers }) {
  console.log(`Connecting to MCP server at ${url}...`);
  
  const transport = new StreamableHTTPClientTransport(url, {
    requestInit: { headers }
  });
  
  const client = new Client({
    name: "agent-around-client",
    version: "1.0.0",
  }, {
    capabilities: { tools: {} },
  });

  await client.connect(transport);
  console.log('Successfully connected to MCP server');
  return client;
}

/**
 * Converts a list of MCP tools into AI SDK compatible tools.
 * 
 * @param {Client} client - The connected MCP client
 * @param {Array} mcpTools - List of tools from MCP server
 * @returns {Object} - Object containing AI SDK tool definitions
 */
function convertToAiSdkTools(client, mcpTools) {
  const tools = {};
  
  for (const mcpTool of mcpTools) {
    tools[mcpTool.name] = tool({
      description: mcpTool.description,
      parameters: jsonSchemaToZod(mcpTool.inputSchema),
      execute: async (args) => {
        console.log(`[Tool] Executing ${mcpTool.name} with args:`, JSON.stringify(args));
        const result = await client.callTool({
          name: mcpTool.name,
          arguments: args
        });
        
        if (result.content && result.content.length > 0) {
          const textContent = result.content.map(c => c.text).join('\n');
          console.log(`[Tool] Result (truncated):`, textContent.substring(0, 100) + '...');
          return textContent;
        }
        return "No content returned from tool.";
      },
    });
  }
  
  return tools;
}

/**
 * Handles fallback for cases where the model might generate a manual tool call string
 * instead of using the tool execution mechanism directly.
 */
async function handleFallbackToolCall(client, resultText, tools) {
  const jsonMatch = resultText.match(/\{[\s\S]*\}/);
  if (!jsonMatch) return;

  try {
    const potentialToolCall = JSON.parse(jsonMatch[0]);
    const { name: toolName, arguments: toolArgs } = potentialToolCall;

    if (toolName && toolArgs && tools[toolName]) {
      console.log(`[Fallback] Executing ${toolName} manually...`);
      const manualResult = await client.callTool({
        name: toolName,
        arguments: toolArgs
      });
      
      if (manualResult.content && manualResult.content.length > 0) {
        const textContent = manualResult.content.map(c => c.text).join('\n');
        console.log('\n--- Manual Tool Execution Result ---');
        
        // Attempt to parse and format if it's JSON
        try {
          let parsed = JSON.parse(textContent);
          if (typeof parsed === 'string') parsed = JSON.parse(parsed);
          console.log(JSON.stringify(parsed, null, 2));
        } catch {
          console.log(textContent);
        }
        console.log('------------------------------------');
      }
    }
  } catch (e) {
    // Not a valid JSON or tool call, ignore
  }
}

async function main() {
  const apiKey = process.env.ZHIPU_API_KEY;
  if (!apiKey) {
    console.error('Error: ZHIPU_API_KEY is not set in .env');
    process.exit(1);
  }

  const mcpConfig = {
    url: 'https://open.bigmodel.cn/api/mcp/web_search_prime/mcp',
    headers: { Authorization: `Bearer ${apiKey}` }
  };

  let client;
  try {
    client = await setupMcpClient(mcpConfig);

    const mcpToolsList = await client.listTools();
    console.log(`Found ${mcpToolsList.tools.length} tools: ${mcpToolsList.tools.map(t => t.name).join(', ')}`);

    const tools = convertToAiSdkTools(client, mcpToolsList.tools);

    console.log('\n--- Generating Text with MCP Tools ---');
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'), 
      tools,
      maxSteps: 5,
      prompt: 'Use the "webSearchPrime" tool to search for "DeepSeek latest news". Make sure to use the correct parameter "search_query".',
    });

    console.log('\nFinal Answer:\n', result.text);

    if (result.toolCalls.length === 0) {
      console.log('\n[Fallback] Checking for manual tool call generation...');
      await handleFallbackToolCall(client, result.text, tools);
    }

  } catch (error) {
    console.error('Application Error:', error);
  } finally {
    if (client) {
      await client.close();
      console.log('MCP connection closed.');
    }
  }
}

main().catch(console.error);
