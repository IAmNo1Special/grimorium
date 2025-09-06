# 🪄 Grimorium: The Dynamic Spellbook for AI Agents

[![PyPI version](https://badge.fury.io/py/grimorium.svg)](https://badge.fury.io/py/grimorium)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Grimorium** is a powerful library that allows your AI agents to dynamically discover and load new tools—or "spells"—on the fly. Inspired by the principles of active tool discovery outlined in the [MCP-Zero research paper](https://arxiv.org/html/2506.01056v4), Grimorium transforms agents from passive tool users into active problem-solvers that can identify their own capability gaps and request new abilities in real-time.

## ✨ Why Grimorium?

Traditional agent frameworks often rely on providing all available tools in the agent's context, leading to significant overhead. Grimorium's approach, similar to that of MCP-Zero, offers substantial benefits:

* **Massive Context Reduction:** By only loading tools as they are needed, this framework can reduce token consumption by up to **98%** compared to traditional methods. This leads to faster response times and lower operational costs.
* **Improved Scalability & Accuracy:** This approach maintains high tool-selection accuracy even with a vast collection of tools. The MCP-Zero paper demonstrated this with a dataset of over 2,700 tools, a scale where traditional methods suffer from attention dilution.
* **Enhanced Autonomy:** Agents become more autonomous and adaptable, capable of tackling complex, multi-domain tasks by building their own toolchains on the fly.

## Key Features

* **Dynamic Tool Loading:** Agents can request and load new tools at runtime without interrupting their workflow.
* **Semantic Search:** Uses vector embeddings to find the most relevant tool for a given task based on natural language descriptions.
* **Extensible:** Easily add new "spells" to the agent's repertoire by simply writing a Python function with a descriptive docstring.
* **Seamless Integration:** Designed for the `google.adk` framework, but the concepts are portable to other agent-based systems.
* **Modern Architecture:** Built with a clean, modular design, using modern Python features like type hints.

## Core Components

* **`Grimorium`:** The main orchestrator. It injects a specialized "grimorium" agent as a tool into the main agent and uses an `after_tool_callback` to trigger the spell discovery and loading process.
* **`SpellSync`:** The engine for the semantic search. It loads a pre-computed list of spells and their embeddings, generates embeddings for user queries, and calculates the cosine similarity to find the best match.
* **`tools.py`:** The spellbook itself. A module containing the Python functions ("spells") that can be loaded.
* **`tools_embeddings.json`:** A pre-computed database of the spells, containing their names, docstrings, and docstring embeddings.

## ⚙️ How It Works

Grimorium's magic lies in its two-step discovery and loading process, which is triggered after the main agent tries to use the `grimorium` tool.

1. **The Request:**** A user asks the agent to do something for which it doesn't have a tool (e.g., "What's the weather?"). The agent, knowing it can learn, uses the `grimorium` tool to request a spell.
2. **The Discovery:**** The `grimorium` tool, guided by specific prompts, extracts the core requirement (e.g., "get the current weather"). This description is passed to the `SpellSync` engine.
3. **The Matching:**** `SpellSync` converts the description into a vector embedding and compares it against the pre-computed embeddings of all available spells, finding the best match via cosine similarity.
4. **The Learning:**** The `Grimorium` class, via an `after_tool_callback`, receives the name of the best-matching spell. It dynamically retrieves the function from `tools.py` and injects it into the main agent's toolset.
5. **The Execution:**** The agent receives a confirmation that the spell has been added. The user can now repeat the initial request, and the agent will have the tool to fulfill it.

```mermaid
graph TD
    A[User: "What's the weather?"] --> B{Agent lacks tool}
    B --> C[Agent uses Grimorium tool: "I need a spell for weather"]
    C --> D[SpellSync finds `weather_forecast` spell]
    D --> E[Grimorium loads `weather_forecast` into agent]
    E --> F[Agent confirms: "Spell added"]
    F --> G[User: "What's the weather?"]
    G --> H[Agent uses `weather_forecast` tool]
    H --> I[Agent provides weather]
```

## 🚀 Getting Started

### Installation

```bash
uv add grimorium
```

### Basic Usage

```python
from google.adk.agents import Agent
from grimorium import Grimorium

# 1. Create your main agent
main_agent = Agent(
    name="main_agent",
    model="gemini-2.0-pro",
    instruction="You are a helpful assistant. If you need a new tool, ask the Grimorium for it."
)

# 2. Give it the Grimorium
# This will automatically equip your agent with the ability to learn new spells.
grimoire = Grimorium(main_agent=main_agent)

# 3. Interact with the agent
# The agent will now automatically use the Grimorium to find and load tools
# when it needs them to answer user queries.
# (See the example/ directory for a full implementation)
```

## 📖 Adding New Spells

To add a new spell to your Grimorium, you need to perform two steps:

1. **Define the function** in your `tools.py` file with a clear, descriptive docstring.

    ```python
    # src/grimorium/tools.py

    def get_stock_price(ticker: str) -> dict:
        """
        Retrieves the current stock price for a given ticker symbol.

        Args:
            ticker: The stock ticker symbol (e.g., "GOOGL").

        Returns:
            A dictionary with the stock price information.
        """
        # Your implementation here...
        return {"price": 150.0}
    ```

2. **Update the embeddings.** You must run an offline script to generate the vector embedding for the new spell's docstring and add it to `tools_embeddings.json`. This process is not yet automated.

## 🔧 Configuration

Grimorium is designed to be configurable via a `config.yaml` file in `~/.grimorium/`. However, this configuration system is still under development and not yet fully implemented.

## 🗺️ Roadmap

* [ ] **Automated Embedding Generation:** A script to automatically update `tools_embeddings.json` when new spells are added.
* [ ] **Dynamic Spell Reset:** A mechanism to decide when to unload spells that are no longer needed.
* [ ] **Richer Built-in Spells:** A more comprehensive set of default spells.
* [ ] **Full Configuration Support:** Complete the implementation of the `config.yaml`-based configuration system.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
