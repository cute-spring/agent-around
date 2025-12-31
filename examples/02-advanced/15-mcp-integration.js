const { Client } = require('@modelcontextprotocol/sdk/client/index.js');
const { StreamableHTTPClientTransport } = require('@modelcontextprotocol/sdk/client/streamableHttp.js');
const { z } = require('zod');
const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
require('dotenv').config();

// Simple JSON Schema to Zod converter for basic types
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
  
  if (schema.type === 'string') return z.string();
  if (schema.type === 'number' || schema.type === 'integer') return z.number();
  if (schema.type === 'boolean') return z.boolean();
  if (schema.type === 'array') {
    return z.array(jsonSchemaToZod(schema.items));
  }
  
  return z.any();
}

async function main() {
  const apiKey = process.env.ZHIPU_API_KEY;
  if (!apiKey) {
    console.error('ZHIPU_API_KEY is not set in .env');
    process.exit(1);
  }

  // MCP Server Configuration
  const mcpConfig = {
    url: 'https://open.bigmodel.cn/api/mcp/web_search_prime/mcp',
    headers: {
      Authorization: `Bearer ${apiKey}`,
    }
  };

  console.log('Connecting to MCP server...');
  const transport = new StreamableHTTPClientTransport(
    mcpConfig.url, 
    {
      requestInit: {
        headers: mcpConfig.headers
      }
    }
  );
  
  const client = new Client({
    name: "agent-around-client",
    version: "1.0.0",
  }, {
    capabilities: {
      tools: {},
    },
  });

  try {
    await client.connect(transport);
    console.log('Connected to MCP server');

    // List tools
    const mcpToolsList = await client.listTools();
    const toolNames = mcpToolsList.tools.map(t => t.name).join(', ');
    console.log(`Found ${mcpToolsList.tools.length} tools: ${toolNames}`);

    // Optional: Manual Tool Verification (to prove MCP connection works)
    // console.log('\n--- Verifying Tool Execution Manually ---');
    // ... code ...

    // Convert MCP tools to AI SDK tools
    const tools = {};
    for (const mcpTool of mcpToolsList.tools) {
      tools[mcpTool.name] = tool({
        description: mcpTool.description,
        parameters: jsonSchemaToZod(mcpTool.inputSchema),
        execute: async (args) => {
          console.log(`[Tool] Executing ${mcpTool.name} with args:`, JSON.stringify(args));
          const result = await client.callTool({
              name: mcpTool.name,
              arguments: args
          });
          
          // Return the content from the tool result
          if (result.content && result.content.length > 0) {
              const textContent = result.content.map(c => c.text).join('\n');
              console.log(`[Tool] Result (truncated):`, textContent.substring(0, 100) + '...');
              return textContent;
          }
          return "No content returned from tool.";
        },
      });
    }

    // Use with AI SDK
    console.log('\n--- Generating Text with MCP Tools ---');
    const result = await generateText({
      model: ollama('qwen2.5-coder:latest'), 
      tools: tools,
      maxSteps: 5,
      // Explicitly instructing the model to use the tool correctly can help with smaller models
      prompt: 'Use the "webSearchPrime" tool to search for "DeepSeek latest news". Make sure to use the correct parameter "search_query".',
    });

    console.log('\nFinal Answer:\n', result.text);

    // Fallback: If the tool wasn't executed automatically but the text contains a tool call JSON
    if (result.toolCalls.length === 0) {
        console.log('\n[Fallback] Checking if model generated tool call JSON...');
        try {
            // Attempt to find JSON block in the text
            const jsonMatch = result.text.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                const potentialToolCall = JSON.parse(jsonMatch[0]);
                if (potentialToolCall.name && potentialToolCall.arguments) {
                    console.log(`[Fallback] Detected manual tool call for ${potentialToolCall.name}`);
                    const toolName = potentialToolCall.name;
                    const toolArgs = potentialToolCall.arguments;
                    
                    if (tools[toolName]) {
                        console.log(`[Fallback] Executing ${toolName} manually...`);
                        const manualResult = await client.callTool({
                            name: toolName,
                            arguments: toolArgs
                        });
                        
                        if (manualResult.content && manualResult.content.length > 0) {
                             const textContent = manualResult.content.map(c => c.text).join('\n');
                             console.log('\n--- Manual Tool Execution Result ---');
                             try {
                                 // The content might be a JSON string wrapped in quotes, or double-stringified
                                 let parsedContent = textContent;
                                 if (typeof textContent === 'string') {
                                     try {
                                         parsedContent = JSON.parse(textContent);
                                     } catch (e) {
                                         // ignore
                                     }
                                 }
                                 // If it was double stringified (e.g. "[...]" inside a string), parse again
                                 if (typeof parsedContent === 'string') {
                                      try {
                                          parsedContent = JSON.parse(parsedContent);
                                      } catch (e) {
                                          // ignore
                                      }
                                 }
                                 
                                 console.log(JSON.stringify(parsedContent, null, 2));
                             } catch (e) {
                                 // If not JSON, print as is
                                 console.log(textContent);
                             }
                             console.log('------------------------------------');
                        }
                    }
                }
            }
        } catch (e) {
            // Not a valid JSON or tool call, ignore
        }
    }

  } catch (error) {
    console.error('Error:', error);
  } finally {
    await client.close();
  }
}

main().catch(console.error);
