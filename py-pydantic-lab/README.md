# PydanticAI Pattern Lab (Python)

Welcome to the **PydanticAI Pattern Lab**. This project is a collection of design patterns and examples for building production-grade AI applications using [PydanticAI](https://ai.pydantic.dev/).

## 🚀 Quick Start

To simplify the development experience, we provide a `run.sh` script that automatically manages your virtual environment and dependencies.

### Running an Example

```bash
# Make the script executable (first time only)
chmod +x run.sh

# Run any example script
./run.sh examples/01-basics/1-basic-generation.py
```

## 🛠️ Implementation Details (`run.sh`)

The [run.sh](run.sh) script is designed to automate the repetitive tasks of Python environment management:

- **Automatic Venv Creation**: If the `venv` directory doesn't exist, it creates one using `python3 -m venv`.
- **Smart Dependency Sync**: 
    - It tracks the modification time of `requirements.txt`.
    - It only runs `pip install` if `requirements.txt` has been changed since the last sync.
    - Uses a hidden `.last_sync` file in the `venv` to store the sync state.
- **Environment Variable Loading**: Automatically exports variables from a local `.env` file if it exists.
- **PYTHONPATH Management**: Automatically adds the project root to `PYTHONPATH`, allowing scripts in subdirectories to import from `common.*` without issues.

## ⚙️ Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Configure your `LLM_PROVIDER` and corresponding API keys in `.env`.

## 📖 Learning Path

- **[LEARNING_GUIDE.md](LEARNING_GUIDE.md)**: A deep dive into the architecture and design patterns used in the examples.
- **[MULTI_AGENT_GUIDE.md](MULTI_AGENT_GUIDE.md)**: Specific patterns for multi-agent orchestration.

## 📂 Project Structure

- `examples/01-basics/`: Core concepts like streaming, tool calling, and structured output.
- `examples/02-intermediate/`: Advanced patterns like reflection, memory, and MCP (Model Context Protocol).
- `examples/03-advanced/`: Production-ready features like monitoring and fallback strategies.
- `examples/common/`: Shared utilities and model factories.
