const { generateText } = require('ai');
const { ollama } = require('ai-sdk-ollama');

async function main() {
  console.log('--- Calling local Ollama (qwen2.5-coder:latest) ---');
  
  try {
    const { text } = await generateText({
      // Using your installed model with the updated v6-compatible provider
      model: ollama('qwen2.5-coder:latest'), 
      prompt: 'Write a one-sentence greeting to a developer using local LLMs.',
    });

    console.log('Ollama Response:', text);
  } catch (error) {
    console.error('Error connecting to Ollama:', error.message);
    console.log('\nTip: Make sure Ollama is running locally and you have the model downloaded:');
    console.log('   ollama run qwen2.5-coder:latest');
  }
}

main();
