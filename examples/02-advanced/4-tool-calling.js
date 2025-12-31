const { generateText, tool } = require('ai');
const { ollama } = require('ai-sdk-ollama');
const { z } = require('zod');

async function main() {
  console.log('--- Tool Calling with Ollama (deepseek-r1:latest) ---');

  const result = await generateText({
    // qwen2.5-coder supports tool calling natively in Ollama
    model: ollama('qwen2.5-coder:latest'),
    tools: {
      getWeather: tool({
        description: 'Get the weather in a location',
        parameters: z.object({
          location: z.string().describe('The city and state, e.g. San Francisco, CA'),
        }),
        execute: async ({ location }) => {
          console.log(`\n[Tool] Fetching weather for ${location}...`);
          return {
            location,
            temperature: 72,
            unit: 'F',
            description: 'Sunny',
          };
        },
      }),
    },
    maxSteps: 5,
    prompt: 'What is the weather like in New York?',
  });

  console.log('\nFinal Answer:', result.text);
}

main().catch(console.error);
