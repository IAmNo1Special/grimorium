# 🪄 Magetools: The Dynamic Spellbook for AI Agents

[![PyPI version](https://badge.fury.io/py/magetools.svg)](https://badge.fury.io/py/magetools)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Magetools** (formerly Grimorium) is an enterprise-grade library that allows your AI agents to dynamically discover, search, and load new tools—or "spells"—on the fly. It transforms agents from static assistants into adaptive problem-solvers that build their own toolchains in real-time.

---

## 🚀 Quick Start

### 1. Installation

```bash
uv add magetools
```

### 2. Create your Grimorium

Create a `.magetools` directory in your project root. Inside, create folders for your "collections".

```text
my_project/
├── .magetools/
│   ├── math_spells/      # Collection Name: "math_spells"
│   │   └── algebra.py
│   └── web_tools/        # Collection Name: "web_tools"
        └── search.py
```

### 3. Scribe a Spell

In `algebra.py`, define a function and decorate it. The docstring is the "embedding source" used for search.

```python
from magetools import register_spell

@register_spell
def magic_add(a: int, b: int) -> int:
    """Calculates the sum of two integers using arcane mathematics."""
    return a + b
```

### 4. Equip the Grimorium

```python
from magetools import Grimorium

# Initialize the Grimorium
# It automatically scans .magetools/ and indexes spells
grimoire = Grimorium(
    root_path="./",  # Explicitly set root (optional, defaults to auto-detect)
    allowed_collections=["math_spells"] # Optional: Restrict access
)

# Add tools to your agent (works with Adk, LangChain, etc.)
agent_tools = await grimoire.get_tools()
```

### 5. Agent Usage

The agent now has access to:
*   `magetools_search_spells(query: str)`
*   `magetools_execute_spell(spell_name: str, arguments: dict)`

---

## 🧠 How It Works

### Architecture
Magetools uses a **Distributed Collection** pattern on a **Unified Database**.
*   **Filesystem**: Each subdirectory in `.magetools` is a "Collection".
*   **Registry**: Spells are tagged via a **passive decorator** (`@register_spell`).
*   **Index**: `SpellSync` scans valid files, extracts metadata, and syncs embeddings to a local Vector Store (ChromaDB).

### Data Flow
1.  **Search**: The agent calls `magetools_search_spells(query="add numbers")`.
2.  **Lookup**: Magetools queries the local Vector Store for semantically similar functions.
3.  **Execute**: The agent calls `magetools_execute_spell(spell_name="math_spells.magic_add", arguments={"a": 1, "b": 2})`.
4.  **Guardrails**: Magetools verifies the spell is in an allowed collection, injects any required context, and executes it securely (offloading to a thread if necessary).

---

## 🛡️ Dependency Injection

Magetools is vendor-agnostic. You can inject your own Embedding provider or Vector Store.

```python
from magetools import Grimorium
from magetools.interfaces import EmbeddingProviderProtocol
from typing import Any

class MyOpenAIProvider(EmbeddingProviderProtocol):
    def get_embedding_function(self) -> Any:
        return openai_embedding_function

grimoire = Grimorium(embedding_provider=MyOpenAIProvider())
```

---

## 📦 Distribution

To build and publish:

```bash
uv build
uv publish
```
